from .. import MlirBuilderBase, OpNames
from ..KernelManager import KernelManager

import numpy as np
import argparse
import sys

from aie.iron import Kernel, ObjectFifo, Program, Runtime, Worker  # type: ignore
from aie.iron.placers import SequentialPlacer  # type: ignore
from aie.iron.controlflow import range_  # type: ignore
from aie.helpers.taplib import TensorAccessPattern  # type: ignore

from ml_dtypes import bfloat16


class ElementwiseIncBuilder(MlirBuilderBase):
    """MLIR module builder for ElementiwseInc operator.

    Methods
    -------
    build(device, size)
        Writes the MLIR module to a temp file and returns a tuple containing the path to the file containing the instructions and the path to the xclbin.
    """

    def __init__(self):
        super().__init__()

    def build(self, device, size) -> tuple[str, str]:
        """Writes the MLIR module to a temp file, compiles it and returns a tuple containing the path to the file containing the instructions and the path to the xclbin.

        Defines all the structure of the MLIR module (and compiles it) used to compute the ElementwiseInc on a 3-vectors list of np.float32 input.
        If this is used to compute "Y += A . X", the input should be a concatenation of three equally sized vectors, the first of which contains all the values for A, the second contains the values for X ant the third contains the values for Y.
        A single vector of the same size of the input vectors and containing the computation (the new Y) result is returned.
        Each one of the three input vectors should be padded up to a multiple of 16 elements.

        Parameters
        ----------
        device : xrt.device
            The device this module is ging to be uploaded to.
        size : int
            The size of each one of the input vectors (should be a multiple of 16).
        """
        num_workers = 4
        value_type = bfloat16
        vec_factor = 32

        entire_axy_input_type = np.ndarray[(3 * size, ), np.dtype[value_type]]
        entire_output_type = np.ndarray[(1 * size, ), np.dtype[value_type]]

        axy_group_type = np.ndarray[(
            3 * vec_factor * num_workers, ), np.dtype[value_type]]
        output_group_type = np.ndarray[(
            vec_factor * num_workers, ), np.dtype[value_type]]

        axy_type = np.ndarray[(3 * vec_factor, ), np.dtype[value_type]]
        output_type = np.ndarray[(vec_factor, ), np.dtype[value_type]]

        axy_offsets = [3 * vec_factor * i for i in range(num_workers)]
        output_offsets = [vec_factor * i for i in range(num_workers)]

        axy_input_of = ObjectFifo(axy_group_type, name="axy_input_of")
        axy_splits = axy_input_of.cons().split(
            axy_offsets,
            obj_types=[axy_type] * num_workers,
            names=[f"axy_input_of.split{i}" for i in range(num_workers)]
        )

        output_of = ObjectFifo(output_group_type, name="output_of")
        output_joins = output_of.prod().join(
            output_offsets,
            obj_types=[output_type] * num_workers,
            names=[f"output_of.join{i}" for i in range(num_workers)]
        )

        kernel_fn = Kernel(
            "elementwise_inc",
            KernelManager.get_kernel_object_for(OpNames.ELEMENTWISE_INC),
            [axy_type, output_type]
        )

        def core_fn(ay_of, out_of, kernel):
            for _ in range_(0xFFFFFFFF):
                ay = ay_of.acquire(1)
                o = out_of.acquire(1)
                kernel(ay, o)
                out_of.release(1)
                ay_of.release(1)

        workers = [
            Worker(core_fn, [axy_splits[i].cons(), output_joins[i].prod(), kernel_fn])
            for i in range(num_workers)
        ]

        rt = Runtime()

        with rt.sequence(entire_axy_input_type, entire_output_type) as (axy, o):
            rt.start(*workers)
            rt.fill(
                axy_input_of.prod(), axy,
                TensorAccessPattern((3, size // vec_factor, vec_factor), offset=0, sizes=[1, size // vec_factor, 3, vec_factor], strides=[0, vec_factor, size, 1]))
            rt.drain(output_of.cons(), o, wait=True)

        program = Program(device, rt)

        resolved = program.resolve_program(SequentialPlacer())

        with open(super().mlir_source, "w") as f:
            print(resolved, file=f)

        return super().compile()
