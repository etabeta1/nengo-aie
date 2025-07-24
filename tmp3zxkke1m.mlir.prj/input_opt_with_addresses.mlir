module attributes {llvm.target_triple = "aie2"} {
  llvm.mlir.global external @input_fifo_cons_buff_1() {addr_space = 0 : i32} : !llvm.array<96 x f16>
  llvm.mlir.global external @input_fifo_cons_buff_0() {addr_space = 0 : i32} : !llvm.array<96 x f16>
  llvm.mlir.global external @output_fifo_buff_1() {addr_space = 0 : i32} : !llvm.array<32 x f16>
  llvm.mlir.global external @output_fifo_buff_0() {addr_space = 0 : i32} : !llvm.array<32 x f16>
  llvm.func @debug_i32(i32) attributes {sym_visibility = "private"}
  llvm.func @llvm.aie2.put.ms(i32, i32) attributes {sym_visibility = "private"}
  llvm.func @llvm.aie2.get.ss() -> !llvm.struct<(i32, i32)> attributes {sym_visibility = "private"}
  llvm.func @llvm.aie2.mcd.write.vec(vector<16xi32>, i32) attributes {sym_visibility = "private"}
  llvm.func @llvm.aie2.scd.read.vec(i32) -> vector<16xi32> attributes {sym_visibility = "private"}
  llvm.func @llvm.aie2.acquire(i32, i32) attributes {sym_visibility = "private"}
  llvm.func @llvm.aie2.release(i32, i32) attributes {sym_visibility = "private"}
  llvm.mlir.global external @output_fifo_cons() {addr_space = 0 : i32} : !llvm.array<32 x f16>
  llvm.mlir.global external @output_fifo() {addr_space = 0 : i32} : !llvm.array<32 x f16>
  llvm.mlir.global external @input_fifo_cons() {addr_space = 0 : i32} : !llvm.array<96 x f16>
  llvm.mlir.global external @input_fifo() {addr_space = 0 : i32} : !llvm.array<96 x f16>
  llvm.func @elementwise_inc(!llvm.ptr, !llvm.ptr) attributes {sym_visibility = "private"}
  llvm.func @core_0_2() {
    %0 = llvm.mlir.addressof @input_fifo_cons_buff_1 : !llvm.ptr
    %1 = llvm.mlir.addressof @output_fifo_buff_1 : !llvm.ptr
    %2 = llvm.mlir.addressof @input_fifo_cons_buff_0 : !llvm.ptr
    %3 = llvm.mlir.addressof @output_fifo_buff_0 : !llvm.ptr
    %4 = llvm.mlir.constant(51 : i32) : i32
    %5 = llvm.mlir.constant(48 : i32) : i32
    %6 = llvm.mlir.constant(49 : i32) : i32
    %7 = llvm.mlir.constant(50 : i32) : i32
    %8 = llvm.mlir.constant(1 : i32) : i32
    %9 = llvm.mlir.constant(-1 : i32) : i32
    %10 = llvm.mlir.constant(4294967294 : index) : i64
    %11 = llvm.mlir.constant(0 : index) : i64
    %12 = llvm.mlir.constant(9223372036854775806 : index) : i64
    %13 = llvm.mlir.constant(2 : index) : i64
    llvm.br ^bb1(%11 : i64)
  ^bb1(%14: i64):  // 2 preds: ^bb0, ^bb7
    %15 = llvm.icmp "slt" %14, %12 : i64
    llvm.cond_br %15, ^bb2(%11 : i64), ^bb8(%11 : i64)
  ^bb2(%16: i64):  // 2 preds: ^bb1, ^bb3
    %17 = llvm.icmp "slt" %16, %10 : i64
    llvm.cond_br %17, ^bb3, ^bb4
  ^bb3:  // pred: ^bb2
    llvm.call @llvm.aie2.acquire(%7, %9) : (i32, i32) -> ()
    llvm.call @llvm.aie2.acquire(%6, %9) : (i32, i32) -> ()
    %18 = llvm.getelementptr %3[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.array<32 x f16>
    %19 = llvm.getelementptr %2[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.array<96 x f16>
    llvm.call @elementwise_inc(%19, %18) : (!llvm.ptr, !llvm.ptr) -> ()
    llvm.call @llvm.aie2.release(%5, %8) : (i32, i32) -> ()
    llvm.call @llvm.aie2.release(%4, %8) : (i32, i32) -> ()
    llvm.call @llvm.aie2.acquire(%7, %9) : (i32, i32) -> ()
    llvm.call @llvm.aie2.acquire(%6, %9) : (i32, i32) -> ()
    %20 = llvm.getelementptr %1[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.array<32 x f16>
    %21 = llvm.getelementptr %0[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.array<96 x f16>
    llvm.call @elementwise_inc(%21, %20) : (!llvm.ptr, !llvm.ptr) -> ()
    llvm.call @llvm.aie2.release(%5, %8) : (i32, i32) -> ()
    llvm.call @llvm.aie2.release(%4, %8) : (i32, i32) -> ()
    %22 = llvm.add %16, %13 : i64
    llvm.br ^bb2(%22 : i64)
  ^bb4:  // pred: ^bb2
    llvm.call @llvm.aie2.acquire(%7, %9) : (i32, i32) -> ()
    llvm.call @llvm.aie2.acquire(%6, %9) : (i32, i32) -> ()
    %23 = llvm.getelementptr %3[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.array<32 x f16>
    %24 = llvm.getelementptr %2[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.array<96 x f16>
    llvm.call @elementwise_inc(%24, %23) : (!llvm.ptr, !llvm.ptr) -> ()
    llvm.call @llvm.aie2.release(%5, %8) : (i32, i32) -> ()
    llvm.call @llvm.aie2.release(%4, %8) : (i32, i32) -> ()
    llvm.br ^bb5(%11 : i64)
  ^bb5(%25: i64):  // 2 preds: ^bb4, ^bb6
    %26 = llvm.icmp "slt" %25, %10 : i64
    llvm.cond_br %26, ^bb6, ^bb7
  ^bb6:  // pred: ^bb5
    llvm.call @llvm.aie2.acquire(%7, %9) : (i32, i32) -> ()
    llvm.call @llvm.aie2.acquire(%6, %9) : (i32, i32) -> ()
    %27 = llvm.getelementptr %1[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.array<32 x f16>
    %28 = llvm.getelementptr %0[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.array<96 x f16>
    llvm.call @elementwise_inc(%28, %27) : (!llvm.ptr, !llvm.ptr) -> ()
    llvm.call @llvm.aie2.release(%5, %8) : (i32, i32) -> ()
    llvm.call @llvm.aie2.release(%4, %8) : (i32, i32) -> ()
    llvm.call @llvm.aie2.acquire(%7, %9) : (i32, i32) -> ()
    llvm.call @llvm.aie2.acquire(%6, %9) : (i32, i32) -> ()
    llvm.call @elementwise_inc(%24, %23) : (!llvm.ptr, !llvm.ptr) -> ()
    llvm.call @llvm.aie2.release(%5, %8) : (i32, i32) -> ()
    llvm.call @llvm.aie2.release(%4, %8) : (i32, i32) -> ()
    %29 = llvm.add %25, %13 : i64
    llvm.br ^bb5(%29 : i64)
  ^bb7:  // pred: ^bb5
    llvm.call @llvm.aie2.acquire(%7, %9) : (i32, i32) -> ()
    llvm.call @llvm.aie2.acquire(%6, %9) : (i32, i32) -> ()
    %30 = llvm.getelementptr %1[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.array<32 x f16>
    %31 = llvm.getelementptr %0[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.array<96 x f16>
    llvm.call @elementwise_inc(%31, %30) : (!llvm.ptr, !llvm.ptr) -> ()
    llvm.call @llvm.aie2.release(%5, %8) : (i32, i32) -> ()
    llvm.call @llvm.aie2.release(%4, %8) : (i32, i32) -> ()
    %32 = llvm.add %14, %13 : i64
    llvm.br ^bb1(%32 : i64)
  ^bb8(%33: i64):  // 2 preds: ^bb1, ^bb9
    %34 = llvm.icmp "slt" %33, %10 : i64
    llvm.cond_br %34, ^bb9, ^bb10
  ^bb9:  // pred: ^bb8
    llvm.call @llvm.aie2.acquire(%7, %9) : (i32, i32) -> ()
    llvm.call @llvm.aie2.acquire(%6, %9) : (i32, i32) -> ()
    %35 = llvm.getelementptr %3[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.array<32 x f16>
    %36 = llvm.getelementptr %2[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.array<96 x f16>
    llvm.call @elementwise_inc(%36, %35) : (!llvm.ptr, !llvm.ptr) -> ()
    llvm.call @llvm.aie2.release(%5, %8) : (i32, i32) -> ()
    llvm.call @llvm.aie2.release(%4, %8) : (i32, i32) -> ()
    llvm.call @llvm.aie2.acquire(%7, %9) : (i32, i32) -> ()
    llvm.call @llvm.aie2.acquire(%6, %9) : (i32, i32) -> ()
    %37 = llvm.getelementptr %1[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.array<32 x f16>
    %38 = llvm.getelementptr %0[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.array<96 x f16>
    llvm.call @elementwise_inc(%38, %37) : (!llvm.ptr, !llvm.ptr) -> ()
    llvm.call @llvm.aie2.release(%5, %8) : (i32, i32) -> ()
    llvm.call @llvm.aie2.release(%4, %8) : (i32, i32) -> ()
    %39 = llvm.add %33, %13 : i64
    llvm.br ^bb8(%39 : i64)
  ^bb10:  // pred: ^bb8
    llvm.call @llvm.aie2.acquire(%7, %9) : (i32, i32) -> ()
    llvm.call @llvm.aie2.acquire(%6, %9) : (i32, i32) -> ()
    %40 = llvm.getelementptr %3[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.array<32 x f16>
    %41 = llvm.getelementptr %2[0, 0] : (!llvm.ptr) -> !llvm.ptr, !llvm.array<96 x f16>
    llvm.call @elementwise_inc(%41, %40) : (!llvm.ptr, !llvm.ptr) -> ()
    llvm.call @llvm.aie2.release(%5, %8) : (i32, i32) -> ()
    llvm.call @llvm.aie2.release(%4, %8) : (i32, i32) -> ()
    llvm.return
  }
}

