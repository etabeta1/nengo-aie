module attributes {llvm.target_triple = "aie2"} {
  llvm.mlir.global external @data_input_fifo_cons_buff_1() {addr_space = 0 : i32} : !llvm.array<288 x f16>
  llvm.mlir.global external @data_input_fifo_cons_buff_0() {addr_space = 0 : i32} : !llvm.array<288 x f16>
  llvm.mlir.global external @param_input_fifo_cons_buff_1() {addr_space = 0 : i32} : !llvm.array<1 x i32>
  llvm.mlir.global external @param_input_fifo_cons_buff_0() {addr_space = 0 : i32} : !llvm.array<1 x i32>
  llvm.mlir.global external @output_fifo_buff_1() {addr_space = 0 : i32} : !llvm.array<288 x f16>
  llvm.mlir.global external @output_fifo_buff_0() {addr_space = 0 : i32} : !llvm.array<288 x f16>
  llvm.func @debug_i32(i32) attributes {sym_visibility = "private"}
  llvm.func @llvm.aie2.put.ms(i32, i32) attributes {sym_visibility = "private"}
  llvm.func @llvm.aie2.get.ss() -> !llvm.struct<(i32, i32)> attributes {sym_visibility = "private"}
  llvm.func @llvm.aie2.mcd.write.vec(vector<16xi32>, i32) attributes {sym_visibility = "private"}
  llvm.func @llvm.aie2.scd.read.vec(i32) -> vector<16xi32> attributes {sym_visibility = "private"}
  llvm.func @llvm.aie2.acquire(i32, i32) attributes {sym_visibility = "private"}
  llvm.func @llvm.aie2.release(i32, i32) attributes {sym_visibility = "private"}
  llvm.mlir.global external @output_fifo_cons() {addr_space = 0 : i32} : !llvm.array<288 x f16>
  llvm.mlir.global external @output_fifo() {addr_space = 0 : i32} : !llvm.array<288 x f16>
  llvm.mlir.global external @param_input_fifo_cons() {addr_space = 0 : i32} : !llvm.array<1 x i32>
  llvm.mlir.global external @param_input_fifo() {addr_space = 0 : i32} : !llvm.array<1 x i32>
  llvm.mlir.global external @data_input_fifo_cons() {addr_space = 0 : i32} : !llvm.array<288 x f16>
  llvm.mlir.global external @data_input_fifo() {addr_space = 0 : i32} : !llvm.array<288 x f16>
  llvm.func @elementwise_inc(!llvm.ptr, !llvm.ptr, !llvm.ptr) attributes {sym_visibility = "private"}
  llvm.func @core_0_2() {
    %0 = llvm.mlir.addressof @data_input_fifo_cons_buff_1 : !llvm.ptr
    %1 = llvm.mlir.addressof @param_input_fifo_cons_buff_1 : !llvm.ptr
    %2 = llvm.mlir.addressof @output_fifo_buff_1 : !llvm.ptr
    %3 = llvm.mlir.addressof @data_input_fifo_cons_buff_0 : !llvm.ptr
    %4 = llvm.mlir.addressof @param_input_fifo_cons_buff_0 : !llvm.ptr
    %5 = llvm.mlir.constant(32 : index) : i64
    %6 = llvm.mlir.constant(true) : i1
    %7 = llvm.mlir.addressof @output_fifo_buff_0 : !llvm.ptr
    %8 = llvm.mlir.constant(50 : i32) : i32
    %9 = llvm.mlir.constant(53 : i32) : i32
    %10 = llvm.mlir.constant(48 : i32) : i32
    %11 = llvm.mlir.constant(49 : i32) : i32
    %12 = llvm.mlir.constant(52 : i32) : i32
    %13 = llvm.mlir.constant(51 : i32) : i32
    %14 = llvm.mlir.constant(1 : i32) : i32
    %15 = llvm.mlir.constant(-1 : i32) : i32
    %16 = llvm.mlir.constant(0 : index) : i64
    %17 = llvm.mlir.constant(9223372036854775806 : index) : i64
    %18 = llvm.mlir.constant(2 : index) : i64
    llvm.br ^bb1(%16 : i64)
  ^bb1(%19: i64):  // 2 preds: ^bb0, ^bb2
    %20 = llvm.icmp "slt" %19, %17 : i64
    llvm.cond_br %20, ^bb2, ^bb3
  ^bb2:  // pred: ^bb1
    llvm.call @llvm.aie2.acquire(%13, %15) : (i32, i32) -> ()
    llvm.call @llvm.aie2.acquire(%12, %15) : (i32, i32) -> ()
    llvm.call @llvm.aie2.acquire(%11, %15) : (i32, i32) -> ()
    %21 = llvm.getelementptr %7[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.array<288 x f16>
    llvm.intr.assume %6 ["align"(%21, %5 : !llvm.ptr, i64)] : i1
    %22 = llvm.getelementptr %4[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.array<1 x i32>
    llvm.intr.assume %6 ["align"(%22, %5 : !llvm.ptr, i64)] : i1
    %23 = llvm.getelementptr %3[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.array<288 x f16>
    llvm.intr.assume %6 ["align"(%23, %5 : !llvm.ptr, i64)] : i1
    llvm.call @elementwise_inc(%22, %23, %21) : (!llvm.ptr, !llvm.ptr, !llvm.ptr) -> ()
    llvm.call @llvm.aie2.release(%10, %14) : (i32, i32) -> ()
    llvm.call @llvm.aie2.release(%9, %14) : (i32, i32) -> ()
    llvm.call @llvm.aie2.release(%8, %14) : (i32, i32) -> ()
    llvm.call @llvm.aie2.acquire(%13, %15) : (i32, i32) -> ()
    llvm.call @llvm.aie2.acquire(%12, %15) : (i32, i32) -> ()
    llvm.call @llvm.aie2.acquire(%11, %15) : (i32, i32) -> ()
    %24 = llvm.getelementptr %2[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.array<288 x f16>
    llvm.intr.assume %6 ["align"(%24, %5 : !llvm.ptr, i64)] : i1
    %25 = llvm.getelementptr %1[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.array<1 x i32>
    llvm.intr.assume %6 ["align"(%25, %5 : !llvm.ptr, i64)] : i1
    %26 = llvm.getelementptr %0[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.array<288 x f16>
    llvm.intr.assume %6 ["align"(%26, %5 : !llvm.ptr, i64)] : i1
    llvm.call @elementwise_inc(%25, %26, %24) : (!llvm.ptr, !llvm.ptr, !llvm.ptr) -> ()
    llvm.call @llvm.aie2.release(%10, %14) : (i32, i32) -> ()
    llvm.call @llvm.aie2.release(%9, %14) : (i32, i32) -> ()
    llvm.call @llvm.aie2.release(%8, %14) : (i32, i32) -> ()
    %27 = llvm.add %19, %18 : i64
    llvm.br ^bb1(%27 : i64)
  ^bb3:  // pred: ^bb1
    llvm.call @llvm.aie2.acquire(%13, %15) : (i32, i32) -> ()
    llvm.call @llvm.aie2.acquire(%12, %15) : (i32, i32) -> ()
    llvm.call @llvm.aie2.acquire(%11, %15) : (i32, i32) -> ()
    %28 = llvm.getelementptr %7[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.array<288 x f16>
    llvm.intr.assume %6 ["align"(%28, %5 : !llvm.ptr, i64)] : i1
    %29 = llvm.getelementptr %4[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.array<1 x i32>
    llvm.intr.assume %6 ["align"(%29, %5 : !llvm.ptr, i64)] : i1
    %30 = llvm.getelementptr %3[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.array<288 x f16>
    llvm.intr.assume %6 ["align"(%30, %5 : !llvm.ptr, i64)] : i1
    llvm.call @elementwise_inc(%29, %30, %28) : (!llvm.ptr, !llvm.ptr, !llvm.ptr) -> ()
    llvm.call @llvm.aie2.release(%10, %14) : (i32, i32) -> ()
    llvm.call @llvm.aie2.release(%9, %14) : (i32, i32) -> ()
    llvm.call @llvm.aie2.release(%8, %14) : (i32, i32) -> ()
    llvm.return
  }
}

