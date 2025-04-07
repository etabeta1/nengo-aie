import numpy as np
import argparse
import sys

from aie.dialects.aie import *
from aie.dialects.aiex import *
from aie.extras.context import mlir_mod_ctx
from aie.helpers.dialects.ext.scf import _for as range_

import aie.utils.trace as trace_utils

class ElementWiseIncBuilder:
    def _build(self, dev, size):
        @device(dev)
        def device_body():
            shim_tile = tile(0, 0)
            memory_tile = tile(0, 1)
            mult_tile = tile(0, 2)
            sum_tile = tile(0, 3)
    
            dtype = np.ndarray[(size, ), np.dtype[np.float16]]
    
            of_A = object_fifo("A in", shim_tile, mult_tile, 2, dtype)
            of_X = object_fifo("X in", shim_tile, mult_tile, 2, dtype)
            of_sum = object_fifo("sum", mult_tile, sum_tile, 2, dtype)
            of_Yin = object_fifo("Y in", shim_tile, sum_tile, 2, dtype)
            of_Yout = object_fifo("Y out", sum_tile, shim_tile, 2, dtype)
    
            element_wise_prod_bfloat16_vec = external_func(
                "element_wise_prod_bfloat16_vec",
                inputs = [dtype, dtype, dtype, np.int32]
            )

            element_wise_sum_bfloat16_vec = external_func(
                "element_wise_sum_bfloat16_vec",
                inputs = [dtype, dtype, dtype, np.int32]
            )

            merge_bfloat16_vec = external_func(
                "merge_bfloat16_vec",
                inputs = [dtype, dtype, dtype, np.int32]
            )

            @core(mult_tile, "element_wise_increment.o")
            def core_body():
                for _ in range_(size // 32):
                    A = of_A.acquire(ObjectFifoPort.Consume, 1)
                    X = of_X.acquire(ObjectFifoPort.Consume, 1)
                    S = of_sum.acquire(ObjectFifoPort.Produce, 1)
    
                    element_wise_prod_bfloat16_vec(A, X, S, 1)
    
                    of_sum.release(ObjectFifoPort.Produce, 1)
                    of_X.release(ObjectFifoPort.Consume, 1)
                    of_A.release(ObjectFifoPort.Consume, 1)

            @core(sum_tile, "element_wise_increment.o")
            def core_body():
                for _ in range_(size // 32):
                    Yin = of_Yin.acquire(ObjectFifoPort.Consume, 1)
                    S = of_sum.acquire(ObjectFifoPort.Consume, 1)
                    Yout = of_Yout.acquire(ObjectFifoPort.Produce, 1)

                    element_wise_sum_bfloat16_vec(Yin, S, Yout, 1)

                    of_Yout.release(ObjectFifoPort.Produce, 1)
                    of_sum.release(ObjectFifoPort.Consume, 1)
                    of_Yin.release(ObjectFifoPort.Consume, 1)

            @core(memory_tile, "element_wise_incrment.o")
            def core_body():
                for _ in range_(size // 32):
                    
                    
            @runtime_sequence(dtype, dtype, dtype, dtype)
            def sequence(A, X, Yin, Yout):
                A_task = shim_dma_single_bd_task(
                    of_A, A, sizes=[1, 1, 1, 32], issue_token=True
                )

                X_task = shim_dma_single_bd_task(
                    of_X, X, sizes=[1, 1, 1, 32], issue_token=True
                )

                Yin_task = shim_dma_single_bd_task(
                    of_Yin, Yin, sizes=[1, 1, 1, 32], issue_token=True
                )

                Yout_task = shim_dma_single_bd_task(
                    of_Yout, Yout, sizes=[1, 1, 1, 32], issue_token=True
                )

                dma_start_task(A_task, X_task, Yin_task, Yout_task)
                dma_await_task(A_task, X_task, Yin_task, Yout_task)
                
    def build(self, size):
        with mlir_mod_ctx() as ctx:
            self._build(AIEDevice.npu2, size)
            ctx.module.operation.verify()
            return ctx.module.__str__()
