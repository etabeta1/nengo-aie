module {
  aie.device(npu1_1col) {
    memref.global "public" @output_fifo_cons : memref<32xf16>
    memref.global "public" @output_fifo : memref<32xf16>
    memref.global "public" @input_fifo_cons : memref<96xf16>
    memref.global "public" @input_fifo : memref<96xf16>
    %tile_0_2 = aie.tile(0, 2) {controller_id = #aie.packet_info<pkt_type = 0, pkt_id = 27>}
    %shim_noc_tile_0_0 = aie.tile(0, 0) {controller_id = #aie.packet_info<pkt_type = 0, pkt_id = 15>}
    %output_fifo_cons_prod_lock_0 = aie.lock(%shim_noc_tile_0_0, 2) {init = 1 : i32, sym_name = "output_fifo_cons_prod_lock_0"}
    %output_fifo_cons_cons_lock_0 = aie.lock(%shim_noc_tile_0_0, 3) {init = 0 : i32, sym_name = "output_fifo_cons_cons_lock_0"}
    %output_fifo_buff_0 = aie.buffer(%tile_0_2) {address = 32768 : i32, mem_bank = 2 : i32, sym_name = "output_fifo_buff_0"} : memref<32xf16> 
    %output_fifo_buff_1 = aie.buffer(%tile_0_2) {address = 49152 : i32, mem_bank = 3 : i32, sym_name = "output_fifo_buff_1"} : memref<32xf16> 
    %output_fifo_prod_lock_0 = aie.lock(%tile_0_2, 2) {init = 2 : i32, sym_name = "output_fifo_prod_lock_0"}
    %output_fifo_cons_lock_0 = aie.lock(%tile_0_2, 3) {init = 0 : i32, sym_name = "output_fifo_cons_lock_0"}
    %input_fifo_cons_buff_0 = aie.buffer(%tile_0_2) {address = 1024 : i32, mem_bank = 0 : i32, sym_name = "input_fifo_cons_buff_0"} : memref<96xf16> 
    %input_fifo_cons_buff_1 = aie.buffer(%tile_0_2) {address = 16384 : i32, mem_bank = 1 : i32, sym_name = "input_fifo_cons_buff_1"} : memref<96xf16> 
    %input_fifo_cons_prod_lock_0 = aie.lock(%tile_0_2, 0) {init = 2 : i32, sym_name = "input_fifo_cons_prod_lock_0"}
    %input_fifo_cons_cons_lock_0 = aie.lock(%tile_0_2, 1) {init = 0 : i32, sym_name = "input_fifo_cons_cons_lock_0"}
    %input_fifo_prod_lock_0 = aie.lock(%shim_noc_tile_0_0, 0) {init = 1 : i32, sym_name = "input_fifo_prod_lock_0"}
    %input_fifo_cons_lock_0 = aie.lock(%shim_noc_tile_0_0, 1) {init = 0 : i32, sym_name = "input_fifo_cons_lock_0"}
    %switchbox_0_0 = aie.switchbox(%shim_noc_tile_0_0) {
      aie.connect<South : 3, North : 1>
      aie.connect<North : 1, South : 2>
      %0 = aie.amsel<5> (3)
      %1 = aie.masterset(South : 0, %0) {keep_pkt_header = true}
      aie.packet_rules(TileControl : 0) {
        aie.rule(31, 15, %0)
      }
    }
    %shim_mux_0_0 = aie.shim_mux(%shim_noc_tile_0_0) {
      aie.connect<DMA : 0, North : 3>
      aie.connect<North : 2, DMA : 0>
    }
    %mem_tile_0_1 = aie.tile(0, 1)
    %switchbox_0_1 = aie.switchbox(%mem_tile_0_1) {
      aie.connect<South : 1, North : 1>
      aie.connect<North : 1, South : 1>
    }
    %switchbox_0_2 = aie.switchbox(%tile_0_2) {
      aie.connect<South : 1, DMA : 0>
      aie.connect<DMA : 0, South : 1>
    }
    func.func private @elementwise_inc(memref<96xf16>, memref<32xf16>)
    %core_0_2 = aie.core(%tile_0_2) {
      %c0 = arith.constant 0 : index
      %c9223372036854775807 = arith.constant 9223372036854775807 : index
      %c1 = arith.constant 1 : index
      %c9223372036854775806 = arith.constant 9223372036854775806 : index
      %c2 = arith.constant 2 : index
      cf.br ^bb1(%c0 : index)
    ^bb1(%0: index):  // 2 preds: ^bb0, ^bb8
      %1 = arith.cmpi slt, %0, %c9223372036854775806 : index
      cf.cond_br %1, ^bb2, ^bb9
    ^bb2:  // pred: ^bb1
      %c0_0 = arith.constant 0 : index
      %c4294967295 = arith.constant 4294967295 : index
      %c1_1 = arith.constant 1 : index
      %c4294967294 = arith.constant 4294967294 : index
      %c2_2 = arith.constant 2 : index
      cf.br ^bb3(%c0_0 : index)
    ^bb3(%2: index):  // 2 preds: ^bb2, ^bb4
      %3 = arith.cmpi slt, %2, %c4294967294 : index
      cf.cond_br %3, ^bb4, ^bb5
    ^bb4:  // pred: ^bb3
      aie.use_lock(%output_fifo_prod_lock_0, AcquireGreaterEqual, 1)
      aie.use_lock(%input_fifo_cons_cons_lock_0, AcquireGreaterEqual, 1)
      func.call @elementwise_inc(%input_fifo_cons_buff_0, %output_fifo_buff_0) : (memref<96xf16>, memref<32xf16>) -> ()
      aie.use_lock(%input_fifo_cons_prod_lock_0, Release, 1)
      aie.use_lock(%output_fifo_cons_lock_0, Release, 1)
      aie.use_lock(%output_fifo_prod_lock_0, AcquireGreaterEqual, 1)
      aie.use_lock(%input_fifo_cons_cons_lock_0, AcquireGreaterEqual, 1)
      func.call @elementwise_inc(%input_fifo_cons_buff_1, %output_fifo_buff_1) : (memref<96xf16>, memref<32xf16>) -> ()
      aie.use_lock(%input_fifo_cons_prod_lock_0, Release, 1)
      aie.use_lock(%output_fifo_cons_lock_0, Release, 1)
      %4 = arith.addi %2, %c2_2 : index
      cf.br ^bb3(%4 : index)
    ^bb5:  // pred: ^bb3
      aie.use_lock(%output_fifo_prod_lock_0, AcquireGreaterEqual, 1)
      aie.use_lock(%input_fifo_cons_cons_lock_0, AcquireGreaterEqual, 1)
      func.call @elementwise_inc(%input_fifo_cons_buff_0, %output_fifo_buff_0) : (memref<96xf16>, memref<32xf16>) -> ()
      aie.use_lock(%input_fifo_cons_prod_lock_0, Release, 1)
      aie.use_lock(%output_fifo_cons_lock_0, Release, 1)
      %c0_3 = arith.constant 0 : index
      %c4294967295_4 = arith.constant 4294967295 : index
      %c1_5 = arith.constant 1 : index
      %c4294967294_6 = arith.constant 4294967294 : index
      %c2_7 = arith.constant 2 : index
      cf.br ^bb6(%c0_3 : index)
    ^bb6(%5: index):  // 2 preds: ^bb5, ^bb7
      %6 = arith.cmpi slt, %5, %c4294967294_6 : index
      cf.cond_br %6, ^bb7, ^bb8
    ^bb7:  // pred: ^bb6
      aie.use_lock(%output_fifo_prod_lock_0, AcquireGreaterEqual, 1)
      aie.use_lock(%input_fifo_cons_cons_lock_0, AcquireGreaterEqual, 1)
      func.call @elementwise_inc(%input_fifo_cons_buff_1, %output_fifo_buff_1) : (memref<96xf16>, memref<32xf16>) -> ()
      aie.use_lock(%input_fifo_cons_prod_lock_0, Release, 1)
      aie.use_lock(%output_fifo_cons_lock_0, Release, 1)
      aie.use_lock(%output_fifo_prod_lock_0, AcquireGreaterEqual, 1)
      aie.use_lock(%input_fifo_cons_cons_lock_0, AcquireGreaterEqual, 1)
      func.call @elementwise_inc(%input_fifo_cons_buff_0, %output_fifo_buff_0) : (memref<96xf16>, memref<32xf16>) -> ()
      aie.use_lock(%input_fifo_cons_prod_lock_0, Release, 1)
      aie.use_lock(%output_fifo_cons_lock_0, Release, 1)
      %7 = arith.addi %5, %c2_7 : index
      cf.br ^bb6(%7 : index)
    ^bb8:  // pred: ^bb6
      aie.use_lock(%output_fifo_prod_lock_0, AcquireGreaterEqual, 1)
      aie.use_lock(%input_fifo_cons_cons_lock_0, AcquireGreaterEqual, 1)
      func.call @elementwise_inc(%input_fifo_cons_buff_1, %output_fifo_buff_1) : (memref<96xf16>, memref<32xf16>) -> ()
      aie.use_lock(%input_fifo_cons_prod_lock_0, Release, 1)
      aie.use_lock(%output_fifo_cons_lock_0, Release, 1)
      %8 = arith.addi %0, %c2 : index
      cf.br ^bb1(%8 : index)
    ^bb9:  // pred: ^bb1
      %c0_8 = arith.constant 0 : index
      %c4294967295_9 = arith.constant 4294967295 : index
      %c1_10 = arith.constant 1 : index
      %c4294967294_11 = arith.constant 4294967294 : index
      %c2_12 = arith.constant 2 : index
      cf.br ^bb10(%c0_8 : index)
    ^bb10(%9: index):  // 2 preds: ^bb9, ^bb11
      %10 = arith.cmpi slt, %9, %c4294967294_11 : index
      cf.cond_br %10, ^bb11, ^bb12
    ^bb11:  // pred: ^bb10
      aie.use_lock(%output_fifo_prod_lock_0, AcquireGreaterEqual, 1)
      aie.use_lock(%input_fifo_cons_cons_lock_0, AcquireGreaterEqual, 1)
      func.call @elementwise_inc(%input_fifo_cons_buff_0, %output_fifo_buff_0) : (memref<96xf16>, memref<32xf16>) -> ()
      aie.use_lock(%input_fifo_cons_prod_lock_0, Release, 1)
      aie.use_lock(%output_fifo_cons_lock_0, Release, 1)
      aie.use_lock(%output_fifo_prod_lock_0, AcquireGreaterEqual, 1)
      aie.use_lock(%input_fifo_cons_cons_lock_0, AcquireGreaterEqual, 1)
      func.call @elementwise_inc(%input_fifo_cons_buff_1, %output_fifo_buff_1) : (memref<96xf16>, memref<32xf16>) -> ()
      aie.use_lock(%input_fifo_cons_prod_lock_0, Release, 1)
      aie.use_lock(%output_fifo_cons_lock_0, Release, 1)
      %11 = arith.addi %9, %c2_12 : index
      cf.br ^bb10(%11 : index)
    ^bb12:  // pred: ^bb10
      aie.use_lock(%output_fifo_prod_lock_0, AcquireGreaterEqual, 1)
      aie.use_lock(%input_fifo_cons_cons_lock_0, AcquireGreaterEqual, 1)
      func.call @elementwise_inc(%input_fifo_cons_buff_0, %output_fifo_buff_0) : (memref<96xf16>, memref<32xf16>) -> ()
      aie.use_lock(%input_fifo_cons_prod_lock_0, Release, 1)
      aie.use_lock(%output_fifo_cons_lock_0, Release, 1)
      aie.end
    } {link_with = "/tmp/tmptppg587x.o"}
    aiex.runtime_sequence @sequence(%arg0: memref<24576xf16>, %arg1: memref<8192xf16>) {
      %0 = aiex.dma_configure_task_for @input_fifo {
        aie.dma_bd(%arg0 : memref<24576xf16>, 0, 24576, [<size = 1, stride = 0>, <size = 1, stride = 0>, <size = 1, stride = 0>, <size = 24576, stride = 1>]) {burst_length = 0 : i32}
        aie.end
      }
      aiex.dma_start_task(%0)
      %1 = aiex.dma_configure_task_for @output_fifo {
        aie.dma_bd(%arg1 : memref<8192xf16>, 0, 8192, [<size = 1, stride = 0>, <size = 1, stride = 0>, <size = 1, stride = 0>, <size = 8192, stride = 1>]) {burst_length = 0 : i32}
        aie.end
      } {issue_token = true}
      aiex.dma_start_task(%1)
      aiex.dma_await_task(%1)
      aiex.dma_free_task(%0)
    }
    aie.shim_dma_allocation @input_fifo(MM2S, 0, 0)
    %mem_0_2 = aie.mem(%tile_0_2) {
      %0 = aie.dma_start(S2MM, 0, ^bb1, ^bb3)
    ^bb1:  // 2 preds: ^bb0, ^bb2
      aie.use_lock(%input_fifo_cons_prod_lock_0, AcquireGreaterEqual, 1)
      aie.dma_bd(%input_fifo_cons_buff_0 : memref<96xf16>, 0, 96) {bd_id = 0 : i32, next_bd_id = 1 : i32}
      aie.use_lock(%input_fifo_cons_cons_lock_0, Release, 1)
      aie.next_bd ^bb2
    ^bb2:  // pred: ^bb1
      aie.use_lock(%input_fifo_cons_prod_lock_0, AcquireGreaterEqual, 1)
      aie.dma_bd(%input_fifo_cons_buff_1 : memref<96xf16>, 0, 96) {bd_id = 1 : i32, next_bd_id = 0 : i32}
      aie.use_lock(%input_fifo_cons_cons_lock_0, Release, 1)
      aie.next_bd ^bb1
    ^bb3:  // pred: ^bb0
      %1 = aie.dma_start(MM2S, 0, ^bb4, ^bb6)
    ^bb4:  // 2 preds: ^bb3, ^bb5
      aie.use_lock(%output_fifo_cons_lock_0, AcquireGreaterEqual, 1)
      aie.dma_bd(%output_fifo_buff_0 : memref<32xf16>, 0, 32) {bd_id = 2 : i32, next_bd_id = 3 : i32}
      aie.use_lock(%output_fifo_prod_lock_0, Release, 1)
      aie.next_bd ^bb5
    ^bb5:  // pred: ^bb4
      aie.use_lock(%output_fifo_cons_lock_0, AcquireGreaterEqual, 1)
      aie.dma_bd(%output_fifo_buff_1 : memref<32xf16>, 0, 32) {bd_id = 3 : i32, next_bd_id = 2 : i32}
      aie.use_lock(%output_fifo_prod_lock_0, Release, 1)
      aie.next_bd ^bb4
    ^bb6:  // pred: ^bb3
      aie.end
    }
    aie.shim_dma_allocation @output_fifo(S2MM, 0, 0)
    aie.packet_flow(15) {
      aie.packet_source<%shim_noc_tile_0_0, TileControl : 0>
      aie.packet_dest<%shim_noc_tile_0_0, South : 0>
    } {keep_pkt_header = true, priority_route = true}
    aie.wire(%shim_mux_0_0 : North, %switchbox_0_0 : South)
    aie.wire(%shim_noc_tile_0_0 : DMA, %shim_mux_0_0 : DMA)
    aie.wire(%mem_tile_0_1 : Core, %switchbox_0_1 : Core)
    aie.wire(%mem_tile_0_1 : DMA, %switchbox_0_1 : DMA)
    aie.wire(%switchbox_0_0 : North, %switchbox_0_1 : South)
    aie.wire(%tile_0_2 : Core, %switchbox_0_2 : Core)
    aie.wire(%tile_0_2 : DMA, %switchbox_0_2 : DMA)
    aie.wire(%switchbox_0_1 : North, %switchbox_0_2 : South)
  }
}

