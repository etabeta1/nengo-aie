from .. import MlirBuilderBase

import numpy as np
import argparse
import sys

from aie.iron import Kernel, ObjectFifo, Program, Runtime, Worker
from aie.iron.placers import SequentialPlacer
from aie.iron.controlflow import range_

class MlirBuilder(MlirBuilderBase.MlirBuilder):
    def __init__(self):
        MlirBuilderBase.MlirBuilder.__init__(self, "ElementwiseInc.mlir")

    def build(self, device, size):
        value_type = np.half
        param_type = np.ndarray[(1, ), np.dtype[np.int32]]
        input_type = np.ndarray[(3 * size, ), np.dtype[value_type]]
        output_type = np.ndarray[(3 * size, ), np.dtype[value_type]]
    
        kernel_fn = Kernel(
            "elementwise_inc",
            "kernel.o",
            [param_type, input_type, output_type]
        )
    
        of_in_param = ObjectFifo(param_type, name="param_input_fifo")
        of_in_data = ObjectFifo(input_type, name="data_input_fifo")
        of_out = ObjectFifo(output_type, name="output_fifo")
    
        def core_fn(of_param, of_data, of_out, kernel):
            p = of_param.acquire(1)
            o = of_out.acquire(1)
            i = of_data.acquire(1)
            kernel(p, i, o)
            of_data.release(1)
            of_out.release(1)
            of_param.release(1)
    
        worker = Worker(core_fn, [of_in_param.cons(), of_in_data.cons(), of_out.prod(), kernel_fn])
    
        rt = Runtime()
    
        with rt.sequence(param_type, input_type, output_type) as (p, i, o):
            rt.start(worker)
            rt.fill(of_in_param.prod(), p)
            rt.fill(of_in_data.prod(), i)
            rt.drain(of_out.cons(), o, wait=True)
    
        program = Program(device, rt)
    
        resolved = program.resolve_program(SequentialPlacer())

        with open(self.filename) as f:
            print(resolved, file=f)
    