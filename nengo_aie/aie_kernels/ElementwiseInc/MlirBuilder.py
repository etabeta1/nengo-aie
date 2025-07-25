from .. import MlirBuilderBase, OpNames
from ..KernelManager import KernelManager

import numpy as np
import argparse
import sys

from aie.iron import Kernel, ObjectFifo, Program, Runtime, Worker  # type: ignore
from aie.iron.placers import SequentialPlacer  # type: ignore
from aie.iron.controlflow import range_  # type: ignore
from aie.helpers.taplib import TensorAccessPattern # type: ignore


class ElementwiseIncBuilder(MlirBuilderBase):
    def __init__(self):
        super().__init__()

    def build(self, device, size) -> tuple[str, str]:
        value_type = np.half

        entire_ay_input_type = np.ndarray[(2 * size, ), np.dtype[value_type]]
        entire_x_input_type = np.ndarray[(1 * size, ), np.dtype[value_type]]        
        entire_output_type = np.ndarray[(1 * size, ), np.dtype[value_type]]

        ay_type = np.ndarray[(64, ), np.dtype[value_type]]
        x_type = np.ndarray[(32, ), np.dtype[value_type]]
        output_type = np.ndarray[(32, ), np.dtype[value_type]]

        kernel_fn = Kernel(
            "elementwise_inc",
            KernelManager.get_kernel_object_for(OpNames.ELEMENTWISE_INC),
            [ay_type, x_type, output_type]
        )

        # of_in_param = ObjectFifo(param_type, name="param_input_fifo")
        
        #of_in_data = ObjectFifo(input_type, name="input_fifo")
        #of_out = ObjectFifo(output_type, name="output_fifo")

        ay_of = ObjectFifo(ay_type, name="ay_of")
        x_of = ObjectFifo(x_type, name="x_of")
        output_of = ObjectFifo(output_type, name="output_of")

        def core_fn(ay_of, x_of, out_of, kernel):
            for _ in range_(0xFFFFFFFF):
                ay = ay_of.acquire(1)
                x = x_of.acquire(1)
                o = out_of.acquire(1)
                kernel(ay, x, o)
                out_of.release(1)
                x_of.release(1)
                ay_of.release(1)

        worker = Worker(core_fn, [ay_of.cons(), x_of.cons(), output_of.prod(), kernel_fn])

        rt = Runtime()

        with rt.sequence(entire_ay_input_type, entire_x_input_type, entire_output_type) as (ay, x, o):
            rt.start(worker)
            rt.fill(
                ay_of.prod(), ay,
                TensorAccessPattern((2, 4, 32), offset=0, sizes=[1, 4, 2, 32], strides=[0,32, 128, 1]))
            rt.fill(
                x_of.prod(), x,
                TensorAccessPattern((1, 4, 32), offset=0, sizes=[1, 1, 2, 32], strides=[0, 0, 64, 1]))
            rt.drain(output_of.cons(), o,
                     TensorAccessPattern((1, 4, 32), offset=0, sizes=[1, 1, 2, 32], strides=[0, 0, 64, 1]),
                     wait=True)

        program = Program(device, rt)

        resolved = program.resolve_program(SequentialPlacer())

        with open(super().mlir_source, "w") as f:
            print(resolved, file=f)

        return super().compile()
