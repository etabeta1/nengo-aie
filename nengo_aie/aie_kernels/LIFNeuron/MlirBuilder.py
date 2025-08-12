from .. import MlirBuilderBase, OpNames
from ..KernelManager import KernelManager

import numpy as np
import argparse
import sys

import ml_dtypes

from aie.iron import Kernel, ObjectFifo, Program, Runtime, Worker, GlobalBuffer, WorkerRuntimeBarrier  # type: ignore
from aie.iron.placers import SequentialPlacer  # type: ignore
from aie.iron.controlflow import range_  # type: ignore
from aie.helpers.taplib import TensorAccessPattern  # type: ignore
from aie.iron.resolvable import Resolvable  # type: ignore
from aie.iron.device import NPU1Col3  # type: ignore


class LIFNeuronBuilder(MlirBuilderBase):
    """MLIR module builder for LIF neurons

    Methods
    -------
    build(device, size)
        Writes the MLIR module to a temp file and returns a tuple containing the path to the file containing the instructions and the path to the xclbin.
    """

    def __init__(self):
        super().__init__()

    def build(self, device: Resolvable = NPU1Col3(), size: int = 32, **kwargs) -> tuple[str, str]:
        """Writes the MLIR module to a temp file and returns a tuple containing the path to the file containing the instructions and the path to the xclbin.

        Defines all the structure of the MLIR module (and compiles it) used to compute the next state of a :size: sized group of LIR neurons.
        The input sent to the NPU is composed by a concatenation of three bfloat16 vectors (padded up to multiple of 32 elements) that contains the input currents, the voltage and the refractory time of each neuron.
        The output is composed by three equally sized vectors that contains the output, the new voltage and the new refractory time for each neuron.

        Parameters
        ----------
        device : xrt.device
            The device this module is ging to be uploaded to.
        size : int
            The size of each one of the input vectors (should be a multiple of 32).
        tau_rc, tau_ref, min_voltage, dt, amplitude : float
            The neuron parameters.
        """
        num_worker_pairs = 6
        io_depth = 2
        inter_depth = 4
        rtp_value_type = np.float32
        value_type = ml_dtypes.bfloat16
        vec_factor = 32

        input_vecs = 3
        intermediate_vecs = 3
        output_vecs = 3

        rtp_num = 6
        rtp_type = np.ndarray[(rtp_num, ), np.dtype[rtp_value_type]]

        entire_input_type = np.ndarray[(input_vecs * size, ), np.dtype[value_type]]
        entire_output_type = np.ndarray[(output_vecs * size, ), np.dtype[value_type]]

        input_group_type = np.ndarray[(
            input_vecs * vec_factor * num_worker_pairs, ), np.dtype[value_type]]
        output_group_type = np.ndarray[(
            output_vecs * vec_factor * num_worker_pairs, ), np.dtype[value_type]]

        input_type = np.ndarray[(input_vecs * vec_factor, ), np.dtype[value_type]]
        intermediate_type = np.ndarray[(
            intermediate_vecs * vec_factor, ), np.dtype[value_type]]
        output_type = np.ndarray[(output_vecs * vec_factor, ), np.dtype[value_type]]

        input_of = ObjectFifo(input_group_type, depth=io_depth, name="input_of")
        input_splits = input_of.cons().split(
            [input_vecs * vec_factor * i for i in range(num_worker_pairs)],
            obj_types=[input_type] * num_worker_pairs,
            names=[f"input_of.split{i}" for i in range(num_worker_pairs)]
        )

        output_of = ObjectFifo(output_group_type, depth=io_depth, name="output_of")
        output_splits = output_of.prod().join(
            [output_vecs * vec_factor * i for i in range(num_worker_pairs)],
            obj_types=[output_type] * num_worker_pairs,
            names=[f"output_of.join{i}" for i in range(num_worker_pairs)]
        )

        intermediate_ofs = [ObjectFifo(intermediate_type, depth=inter_depth, name=f"intermediate_of.{i}")
                            for i in range(num_worker_pairs)]

        step_1_fn = Kernel(
            "lif_kernel_step_1",
            "kernel.o",
            [rtp_value_type] * rtp_num + [input_type, intermediate_type]
        )

        step_2_fn = Kernel(
            "lif_kernel_step_2",
            "kernel.o",
            [rtp_value_type] * rtp_num + [intermediate_type, output_type]
        )

        def core_fn_step_1(rtps, barrier, input_of, interm_of, kernel):
            barrier.wait_for_value(1)

            tau_rc = rtps[0]
            tau_ref = rtps[1]
            min_voltage = rtps[2]
            dt = rtps[3]
            amplitude = rtps[4]
            spike_height = rtps[5]

            for _ in range_(0xFFFFFFFF):
                i = input_of.acquire(1)
                o = interm_of.acquire(1)
                kernel(tau_rc, tau_ref, min_voltage, dt, amplitude, spike_height, i, o)
                interm_of.release(1)
                input_of.release(1)

        def core_fn_step_2(rtps, barrier, interm_of, output_of, kernel):
            barrier.wait_for_value(1)

            tau_rc = rtps[0]
            tau_ref = rtps[1]
            min_voltage = rtps[2]
            dt = rtps[3]
            amplitude = rtps[4]
            spike_height = rtps[5]

            for _ in range_(0xFFFFFFFF):
                o = output_of.acquire(1)
                i = interm_of.acquire(1)
                kernel(tau_rc, tau_ref, min_voltage, dt, amplitude, spike_height, i, o)
                interm_of.release(1)
                output_of.release(1)

        rtpss = [GlobalBuffer(
            rtp_type, name=f"rtps{i}", use_write_rtp=True) for i in range(2 * num_worker_pairs)]

        rtpbs = [WorkerRuntimeBarrier() for _ in range(2 * num_worker_pairs)]

        workers = [
            Worker(core_fn_step_1, [rtpss[i], rtpbs[i], input_splits[i // 2].cons(), intermediate_ofs[i // 2].prod(), step_1_fn]) if i % 2 == 0 else
            Worker(core_fn_step_2, [rtpss[i], rtpbs[i], intermediate_ofs[i //
                   2].cons(), output_splits[i // 2].prod(), step_2_fn])
            for i in range(2 * num_worker_pairs)
        ]

        rt = Runtime()

        with rt.sequence(entire_input_type, entire_output_type) as (i, o):
            def set_rtps(*rtpss):
                for rtps in rtpss:
                    rtps[0] = np.float32(kwargs["tau_rc"]).view(np.int32)
                    rtps[1] = np.float32(kwargs["tau_ref"]).view(np.int32)
                    rtps[2] = np.float32(kwargs["min_voltage"]).view(np.int32)
                    rtps[3] = np.float32(kwargs["dt"]).view(np.int32)
                    rtps[4] = np.float32(kwargs["amplitude"]).view(np.int32)
                    rtps[5] = np.float32(kwargs["amplitude"] /
                                         kwargs["dt"]).view(np.int32)

            rt.inline_ops(set_rtps, rtpss)

            for rtpb in rtpbs:
                rt.set_barrier(rtpb, 1)

            rt.start(*workers)

            rt.fill(
                input_of.prod(), i,
                TensorAccessPattern((3, size // vec_factor, vec_factor), offset=0, sizes=[1, size // vec_factor, 3, vec_factor], strides=[0, vec_factor, size, 1]))

            rt.drain(
                output_of.cons(), o,
                TensorAccessPattern((3, size // vec_factor, vec_factor), offset=0, sizes=[
                                    1, size // vec_factor, 3, vec_factor], strides=[0, vec_factor, size, 1]),
                wait=True)

        program = Program(device, rt)

        resolved = program.resolve_program(SequentialPlacer())

        with open(super().mlir_source, "w") as f:
            print(resolved, file=f)

        return super().compile()
