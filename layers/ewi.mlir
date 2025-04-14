module {
  aie.device(npu2) {
    %tile_0_2 = aie.tile(0, 2)
    %shim_noc_tile_0_0 = aie.tile(0, 0)
    aie.objectfifo @output_fifo(%tile_0_2, {%shim_noc_tile_0_0}, 2 : i32) : !aie.objectfifo<memref<3072xf16>> 
    aie.objectfifo @input_fifo(%shim_noc_tile_0_0, {%tile_0_2}, 2 : i32) : !aie.objectfifo<memref<3076xf16>> 
    func.func private @elementwise_inc(memref<3076xf16>, memref<3072xf16>)
    %core_0_2 = aie.core(%tile_0_2) {
      %c0 = arith.constant 0 : index
      %c9223372036854775807 = arith.constant 9223372036854775807 : index
      %c1 = arith.constant 1 : index
      scf.for %arg0 = %c0 to %c9223372036854775807 step %c1 {
        %0 = aie.objectfifo.acquire @output_fifo(Produce, 1) : !aie.objectfifosubview<memref<3072xf16>>
        %1 = aie.objectfifo.subview.access %0[0] : !aie.objectfifosubview<memref<3072xf16>> -> memref<3072xf16>
        %2 = aie.objectfifo.acquire @input_fifo(Consume, 1) : !aie.objectfifosubview<memref<3076xf16>>
        %3 = aie.objectfifo.subview.access %2[0] : !aie.objectfifosubview<memref<3076xf16>> -> memref<3076xf16>
        func.call @elementwise_inc(%3, %1) : (memref<3076xf16>, memref<3072xf16>) -> ()
        aie.objectfifo.release @input_fifo(Consume, 1)
        aie.objectfifo.release @output_fifo(Produce, 1)
      }
      aie.end
    } {link_with = "elementwise_incr.o"}
    aiex.runtime_sequence @sequence(%arg0: memref<3076xf16>, %arg1: memref<3072xf16>) {
      %0 = aiex.dma_configure_task_for @input_fifo {
        aie.dma_bd(%arg0 : memref<3076xf16>, 0, 3076, [<size = 1, stride = 0>, <size = 1, stride = 0>, <size = 1, stride = 0>, <size = 3076, stride = 1>]) {burst_length = 0 : i32}
        aie.end
      }
      aiex.dma_start_task(%0)
      %1 = aiex.dma_configure_task_for @output_fifo {
        aie.dma_bd(%arg1 : memref<3072xf16>, 0, 3072, [<size = 1, stride = 0>, <size = 1, stride = 0>, <size = 1, stride = 0>, <size = 3072, stride = 1>]) {burst_length = 0 : i32}
        aie.end
      } {issue_token = true}
      aiex.dma_start_task(%1)
      aiex.dma_await_task(%1)
      aiex.dma_free_task(%0)
    }
  }
}

