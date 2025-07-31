from .. import MlirBuilderBase, OpNames
from ..KernelManager import KernelManager

import numpy as np
import argparse
import sys

from aie.iron import Kernel, ObjectFifo, Program, Runtime, Worker, GlobalBuffer, WorkerRuntimeBarrier  # type: ignore
from aie.iron.placers import SequentialPlacer  # type: ignore
from aie.iron.controlflow import range_  # type: ignore
from aie.helpers.taplib import TensorAccessPattern  # type: ignore


class LIFNeuronBuilder(MlirBuilderBase):
    def __init__(self):
        super().__init__()

    def build(self, device, size, **kwargs) -> tuple[str, str]:
        num_workers = 4
        depth = 2
        value_type = np.float32
        vec_factor = 16

        entire_input_type = np.ndarray[(3 * size, ), np.dtype[value_type]]
        entire_output_type = np.ndarray[(3 * size, ), np.dtype[value_type]]

        input_group_type = np.ndarray[(
            3 * vec_factor * num_workers, ), np.dtype[value_type]]
        output_group_type = np.ndarray[(
            3 * vec_factor * num_workers, ), np.dtype[value_type]]

        input_type = np.ndarray[(3 * vec_factor, ), np.dtype[value_type]]
        output_type = np.ndarray[(3 * vec_factor, ), np.dtype[value_type]]

        input_of = ObjectFifo(input_group_type, depth=depth, name="input_of")
        input_splits = input_of.cons().split(
            [3 * vec_factor * i for i in range(num_workers)],
            obj_types=[input_type] * num_workers,
            names=[f"input_of.split{i}" for i in range(num_workers)]
        )

        output_of = ObjectFifo(output_group_type, depth=depth, name="output_of")
        output_splits = output_of.prod().join(
            [3 * vec_factor * i for i in range(num_workers)],
            obj_types=[output_type] * num_workers,
            names=[f"output_of.join{i}" for i in range(num_workers)]
        )

        kernel_fn = Kernel(
            "lif_kernel",
            KernelManager.get_kernel_object_for(OpNames.LIF_NEURON),
            [value_type] * 5 + [input_type, output_type]
        )

        def core_fn(rtps, barrier, input_of, output_of, kernel):
            barrier.wait_for_value(1)
            
            tau_rc = rtps[0]
            tau_ref = rtps[1]
            min_voltage = rtps[2]
            dt = rtps[3]
            amplitude = rtps[4]

            for _ in range_(0xFFFFFFFF):
                i = input_of.acquire(1)
                o = output_of.acquire(1)
                # kernel(kwargs["tau_rc"], kwargs["tau_ref"],
                       # kwargs["min_voltage"], kwargs["dt"], kwargs["amplitude"], i, o)
                kernel(tau_rc, tau_ref, min_voltage, dt, amplitude, i, o)
                output_of.release(1)
                input_of.release(1)

        rtp_type = np.ndarray[(5, ), np.dtype[value_type]]

        rtpss = [GlobalBuffer(
            rtp_type, name=f"rtps{i}", use_write_rtp=True) for i in range(num_workers)]

        rtpbs = [WorkerRuntimeBarrier() for _ in range(num_workers)]

        workers = [
            Worker(core_fn, [rtpss[i], rtpbs[i], input_splits[i].cons(),
                   output_splits[i].prod(), kernel_fn])
            for i in range(num_workers)
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

            rt.inline_ops(set_rtps, rtpss)

            for rtpb in rtpbs:
                rt.set_barrier(rtpb, 1)

            rt.start(*workers)

            rt.fill(
                input_of.prod(), i,
                TensorAccessPattern((3, size // vec_factor, vec_factor), offset=0, sizes=[1, size // vec_factor, 3, vec_factor], strides=[0, vec_factor, size, 1]))

            rt.drain(
                output_of.cons(), o,
                TensorAccessPattern((3, size // vec_factor, vec_factor), offset=0, sizes=[1, size // vec_factor, 3, vec_factor], strides=[0, vec_factor, size, 1]),
                wait=True)

        program = Program(device, rt)

        resolved = program.resolve_program(SequentialPlacer())

        with open(super().mlir_source, "w") as f:
            print(resolved, file=f)

        return super().compile()
