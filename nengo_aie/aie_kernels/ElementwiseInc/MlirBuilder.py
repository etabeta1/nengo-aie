from .. import MlirBuilderBase

import numpy as np
import argparse
import sys

from aie.iron import Kernel, ObjectFifo, Program, Runtime, Worker
from aie.iron.placers import SequentialPlacer
from aie.iron.controlflow import range_

class ElementwiseIncBuilder(MlirBuilderBase):
    def __init__(self):
        super().__init__("ElementwiseInc.mlir")

    def build(self, device, size):
        value_type = np.half

        entire_input_type = np.ndarray[(3 * size, ), np.dtype[value_type]]
        entire_output_type = np.ndarray[(size, ), np.dtype[value_type]]
        
        input_type = np.ndarray[(96, ), np.dtype[value_type]]
        output_type = np.ndarray[(32, ), np.dtype[value_type]]
    
        kernel_fn = Kernel(
            "elementwise_inc",
            "kernel.o",
            [input_type, output_type]
        )
    
        # of_in_param = ObjectFifo(param_type, name="param_input_fifo")
        of_in_data = ObjectFifo(input_type, name="input_fifo")
        of_out = ObjectFifo(output_type, name="output_fifo")
    
        def core_fn(of_data, of_out, kernel):
            for _ in range_(0xFFFFFFFF):
                o = of_out.acquire(1)
                i = of_data.acquire(1)
                kernel(i, o)
                of_data.release(1)
                of_out.release(1)
    
        worker = Worker(core_fn, [of_in_data.cons(), of_out.prod(), kernel_fn])
    
        rt = Runtime()
    
        with rt.sequence(entire_input_type, entire_output_type) as (i, o):
            rt.start(worker)
            rt.fill(of_in_data.prod(), i)
            rt.drain(of_out.cons(), o, wait=True)
    
        program = Program(device, rt)
    
        resolved = program.resolve_program(SequentialPlacer())

        with open(self.filename) as f:
            print(resolved, file=f)
    