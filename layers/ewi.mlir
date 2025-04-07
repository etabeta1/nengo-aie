module {
  aie.device(npu2) {
    %shim_noc_tile_0_0 = aie.tile(0, 0)
    %tile_0_2 = aie.tile(0, 2)
    %tile_0_3 = aie.tile(0, 3)
    aie.objectfifo @"A in"(%shim_noc_tile_0_0, {%tile_0_2}, 2 : i32) : !aie.objectfifo<memref<32xf16>> 
    aie.objectfifo @"X in"(%shim_noc_tile_0_0, {%tile_0_2}, 2 : i32) : !aie.objectfifo<memref<32xf16>> 
    aie.objectfifo @sum(%tile_0_2, {%tile_0_3}, 2 : i32) : !aie.objectfifo<memref<32xf16>> 
    aie.objectfifo @"Y in"(%shim_noc_tile_0_0, {%tile_0_3}, 2 : i32) : !aie.objectfifo<memref<32xf16>> 
    aie.objectfifo @"Y out"(%tile_0_3, {%shim_noc_tile_0_0}, 2 : i32) : !aie.objectfifo<memref<32xf16>> 
    func.func private @element_wise_prod_bfloat16_vec(memref<32xf16>, memref<32xf16>, memref<32xf16>, i32)
    func.func private @element_wise_sum_bfloat16_vec(memref<32xf16>, memref<32xf16>, memref<32xf16>, i32)
    %core_0_2 = aie.core(%tile_0_2) {
      %c0 = arith.constant 0 : index
      %c1 = arith.constant 1 : index
      %c1_0 = arith.constant 1 : index
      scf.for %arg0 = %c0 to %c1 step %c1_0 {
        %0 = aie.objectfifo.acquire @"A in"(Consume, 1) : !aie.objectfifosubview<memref<32xf16>>
        %1 = aie.objectfifo.subview.access %0[0] : !aie.objectfifosubview<memref<32xf16>> -> memref<32xf16>
        %2 = aie.objectfifo.acquire @"X in"(Consume, 1) : !aie.objectfifosubview<memref<32xf16>>
        %3 = aie.objectfifo.subview.access %2[0] : !aie.objectfifosubview<memref<32xf16>> -> memref<32xf16>
        %4 = aie.objectfifo.acquire @sum(Produce, 1) : !aie.objectfifosubview<memref<32xf16>>
        %5 = aie.objectfifo.subview.access %4[0] : !aie.objectfifosubview<memref<32xf16>> -> memref<32xf16>
        %c1_i32 = arith.constant 1 : i32
        func.call @element_wise_prod_bfloat16_vec(%1, %3, %5, %c1_i32) : (memref<32xf16>, memref<32xf16>, memref<32xf16>, i32) -> ()
        aie.objectfifo.release @sum(Produce, 1)
        aie.objectfifo.release @"X in"(Consume, 1)
        aie.objectfifo.release @"A in"(Consume, 1)
      }
      aie.end
    } {link_with = "element_wise_increment.o"}
    %core_0_3 = aie.core(%tile_0_3) {
      %c0 = arith.constant 0 : index
      %c1 = arith.constant 1 : index
      %c1_0 = arith.constant 1 : index
      scf.for %arg0 = %c0 to %c1 step %c1_0 {
        %0 = aie.objectfifo.acquire @"Y in"(Consume, 1) : !aie.objectfifosubview<memref<32xf16>>
        %1 = aie.objectfifo.subview.access %0[0] : !aie.objectfifosubview<memref<32xf16>> -> memref<32xf16>
        %2 = aie.objectfifo.acquire @sum(Consume, 1) : !aie.objectfifosubview<memref<32xf16>>
        %3 = aie.objectfifo.subview.access %2[0] : !aie.objectfifosubview<memref<32xf16>> -> memref<32xf16>
        %4 = aie.objectfifo.acquire @"Y out"(Produce, 1) : !aie.objectfifosubview<memref<32xf16>>
        %5 = aie.objectfifo.subview.access %4[0] : !aie.objectfifosubview<memref<32xf16>> -> memref<32xf16>
        %c1_i32 = arith.constant 1 : i32
        func.call @element_wise_sum_bfloat16_vec(%1, %3, %5, %c1_i32) : (memref<32xf16>, memref<32xf16>, memref<32xf16>, i32) -> ()
        aie.objectfifo.release @"Y out"(Produce, 1)
        aie.objectfifo.release @sum(Consume, 1)
        aie.objectfifo.release @"Y in"(Consume, 1)
      }
      aie.end
    } {link_with = "element_wise_increment.o"}
    aiex.runtime_sequence @sequence(%arg0: memref<32xf16>, %arg1: memref<32xf16>, %arg2: memref<32xf16>, %arg3: memref<32xf16>) {
      %0 = aiex.dma_configure_task_for @"A in" {
        aie.dma_bd(%arg0 : memref<32xf16>, 0, 32, [<size = 1, stride = 0>, <size = 1, stride = 0>, <size = 1, stride = 0>, <size = 32, stride = 1>]) {burst_length = 0 : i32}
        aie.end
      } {issue_token = true}
      %1 = aiex.dma_configure_task_for @"X in" {
        aie.dma_bd(%arg1 : memref<32xf16>, 0, 32, [<size = 1, stride = 0>, <size = 1, stride = 0>, <size = 1, stride = 0>, <size = 32, stride = 1>]) {burst_length = 0 : i32}
        aie.end
      } {issue_token = true}
      %2 = aiex.dma_configure_task_for @"Y in" {
        aie.dma_bd(%arg2 : memref<32xf16>, 0, 32, [<size = 1, stride = 0>, <size = 1, stride = 0>, <size = 1, stride = 0>, <size = 32, stride = 1>]) {burst_length = 0 : i32}
        aie.end
      } {issue_token = true}
      %3 = aiex.dma_configure_task_for @"Y out" {
        aie.dma_bd(%arg3 : memref<32xf16>, 0, 32, [<size = 1, stride = 0>, <size = 1, stride = 0>, <size = 1, stride = 0>, <size = 32, stride = 1>]) {burst_length = 0 : i32}
        aie.end
      } {issue_token = true}
      aiex.dma_start_task(%0)
      aiex.dma_start_task(%1)
      aiex.dma_start_task(%2)
      aiex.dma_start_task(%3)
      aiex.dma_await_task(%0)
      aiex.dma_await_task(%1)
      aiex.dma_await_task(%2)
      aiex.dma_await_task(%3)
    }
  }
}
