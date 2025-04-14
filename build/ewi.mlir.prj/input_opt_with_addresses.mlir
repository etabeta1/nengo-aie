module attributes {llvm.target_triple = "aie2p"} {
  llvm.mlir.global external @output_fifo_buff_1() {addr_space = 0 : i32} : !llvm.array<3072 x f16>
  llvm.mlir.global external @output_fifo_buff_0() {addr_space = 0 : i32} : !llvm.array<3072 x f16>
  llvm.mlir.global external @input_fifo_cons_buff_1() {addr_space = 0 : i32} : !llvm.array<3076 x f16>
  llvm.mlir.global external @input_fifo_cons_buff_0() {addr_space = 0 : i32} : !llvm.array<3076 x f16>
  llvm.func @debug_i32(i32) attributes {sym_visibility = "private"}
  llvm.func @llvm.aie2p.put.ms(i32, i32) attributes {sym_visibility = "private"}
  llvm.func @llvm.aie2p.get.ss() -> !llvm.struct<(i32, i32)> attributes {sym_visibility = "private"}
  llvm.func @llvm.aie2p.mcd.write.vec(vector<16xi32>, i32) attributes {sym_visibility = "private"}
  llvm.func @llvm.aie2p.scd.read.vec(i32) -> vector<16xi32> attributes {sym_visibility = "private"}
  llvm.func @llvm.aie2p.acquire(i32, i32) attributes {sym_visibility = "private"}
  llvm.func @llvm.aie2p.release(i32, i32) attributes {sym_visibility = "private"}
  llvm.mlir.global external @input_fifo_cons() {addr_space = 0 : i32} : !llvm.array<3076 x f16>
  llvm.mlir.global external @input_fifo() {addr_space = 0 : i32} : !llvm.array<3076 x f16>
  llvm.mlir.global external @output_fifo_cons() {addr_space = 0 : i32} : !llvm.array<3072 x f16>
  llvm.mlir.global external @output_fifo() {addr_space = 0 : i32} : !llvm.array<3072 x f16>
  llvm.func @elementwise_inc(!llvm.ptr, !llvm.ptr) attributes {sym_visibility = "private"}
  llvm.func @core_0_2() {
    %0 = llvm.mlir.addressof @output_fifo_buff_1 : !llvm.ptr
    %1 = llvm.mlir.addressof @input_fifo_cons_buff_1 : !llvm.ptr
    %2 = llvm.mlir.addressof @output_fifo_buff_0 : !llvm.ptr
    %3 = llvm.mlir.constant(32 : index) : i64
    %4 = llvm.mlir.constant(true) : i1
    %5 = llvm.mlir.addressof @input_fifo_cons_buff_0 : !llvm.ptr
    %6 = llvm.mlir.constant(49 : i32) : i32
    %7 = llvm.mlir.constant(50 : i32) : i32
    %8 = llvm.mlir.constant(51 : i32) : i32
    %9 = llvm.mlir.constant(48 : i32) : i32
    %10 = llvm.mlir.constant(1 : i32) : i32
    %11 = llvm.mlir.constant(-1 : i32) : i32
    %12 = llvm.mlir.constant(0 : index) : i64
    %13 = llvm.mlir.constant(9223372036854775806 : index) : i64
    %14 = llvm.mlir.constant(2 : index) : i64
    llvm.br ^bb1(%12 : i64)
  ^bb1(%15: i64):  // 2 preds: ^bb0, ^bb2
    %16 = llvm.icmp "slt" %15, %13 : i64
    llvm.cond_br %16, ^bb2, ^bb3
  ^bb2:  // pred: ^bb1
    llvm.call @llvm.aie2p.acquire(%9, %11) : (i32, i32) -> ()
    llvm.call @llvm.aie2p.acquire(%8, %11) : (i32, i32) -> ()
    %17 = llvm.getelementptr %5[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.array<3076 x f16>
    llvm.intr.assume %4 ["align"(%17, %3 : !llvm.ptr, i64)] : i1
    %18 = llvm.getelementptr %2[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.array<3072 x f16>
    llvm.intr.assume %4 ["align"(%18, %3 : !llvm.ptr, i64)] : i1
    llvm.call @elementwise_inc(%17, %18) : (!llvm.ptr, !llvm.ptr) -> ()
    llvm.call @llvm.aie2p.release(%7, %10) : (i32, i32) -> ()
    llvm.call @llvm.aie2p.release(%6, %10) : (i32, i32) -> ()
    llvm.call @llvm.aie2p.acquire(%9, %11) : (i32, i32) -> ()
    llvm.call @llvm.aie2p.acquire(%8, %11) : (i32, i32) -> ()
    %19 = llvm.getelementptr %1[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.array<3076 x f16>
    llvm.intr.assume %4 ["align"(%19, %3 : !llvm.ptr, i64)] : i1
    %20 = llvm.getelementptr %0[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.array<3072 x f16>
    llvm.intr.assume %4 ["align"(%20, %3 : !llvm.ptr, i64)] : i1
    llvm.call @elementwise_inc(%19, %20) : (!llvm.ptr, !llvm.ptr) -> ()
    llvm.call @llvm.aie2p.release(%7, %10) : (i32, i32) -> ()
    llvm.call @llvm.aie2p.release(%6, %10) : (i32, i32) -> ()
    %21 = llvm.add %15, %14 : i64
    llvm.br ^bb1(%21 : i64)
  ^bb3:  // pred: ^bb1
    llvm.call @llvm.aie2p.acquire(%9, %11) : (i32, i32) -> ()
    llvm.call @llvm.aie2p.acquire(%8, %11) : (i32, i32) -> ()
    %22 = llvm.getelementptr %5[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.array<3076 x f16>
    llvm.intr.assume %4 ["align"(%22, %3 : !llvm.ptr, i64)] : i1
    %23 = llvm.getelementptr %2[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.array<3072 x f16>
    llvm.intr.assume %4 ["align"(%23, %3 : !llvm.ptr, i64)] : i1
    llvm.call @elementwise_inc(%22, %23) : (!llvm.ptr, !llvm.ptr) -> ()
    llvm.call @llvm.aie2p.release(%7, %10) : (i32, i32) -> ()
    llvm.call @llvm.aie2p.release(%6, %10) : (i32, i32) -> ()
    llvm.return
  }
}

