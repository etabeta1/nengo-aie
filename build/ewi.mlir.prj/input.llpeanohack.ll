; ModuleID = 'LLVMDialectModule'
source_filename = "LLVMDialectModule"
target triple = "aie2p"

@output_fifo_buff_1 = external global [3072 x half]
@output_fifo_buff_0 = external global [3072 x half]
@input_fifo_cons_buff_1 = external global [3076 x half]
@input_fifo_cons_buff_0 = external global [3076 x half]
@input_fifo_cons = external global [3076 x half]
@input_fifo = external global [3076 x half]
@output_fifo_cons = external global [3072 x half]
@output_fifo = external global [3072 x half]

declare void @debug_i32(i32)

declare void @llvm.aie2p.put.ms(i32, i32)

declare { i32, i32 } @llvm.aie2p.get.ss()

declare void @llvm.aie2p.mcd.write.vec(<16 x i32>, i32)

declare <16 x i32> @llvm.aie2p.scd.read.vec(i32)

declare void @llvm.aie2p.acquire(i32, i32)

declare void @llvm.aie2p.release(i32, i32)

declare void @elementwise_inc(ptr, ptr)

define void @core_0_2() {
  br label %1

1:                                                ; preds = %4, %0
  %2 = phi i64 [ %5, %4 ], [ 0, %0 ]
  %3 = icmp slt i64 %2, 9223372036854775806
  br i1 %3, label %4, label %6

4:                                                ; preds = %1
  call void @llvm.aie2p.acquire(i32 48, i32 -1)
  call void @llvm.aie2p.acquire(i32 51, i32 -1)
  call void @llvm.assume(i1 true) [ "align"(ptr @input_fifo_cons_buff_0, i64 32) ]
  call void @llvm.assume(i1 true) [ "align"(ptr @output_fifo_buff_0, i64 32) ]
  call void @elementwise_inc(ptr @input_fifo_cons_buff_0, ptr @output_fifo_buff_0)
  call void @llvm.aie2p.release(i32 50, i32 1)
  call void @llvm.aie2p.release(i32 49, i32 1)
  call void @llvm.aie2p.acquire(i32 48, i32 -1)
  call void @llvm.aie2p.acquire(i32 51, i32 -1)
  call void @llvm.assume(i1 true) [ "align"(ptr @input_fifo_cons_buff_1, i64 32) ]
  call void @llvm.assume(i1 true) [ "align"(ptr @output_fifo_buff_1, i64 32) ]
  call void @elementwise_inc(ptr @input_fifo_cons_buff_1, ptr @output_fifo_buff_1)
  call void @llvm.aie2p.release(i32 50, i32 1)
  call void @llvm.aie2p.release(i32 49, i32 1)
  %5 = add i64 %2, 2
  br label %1

6:                                                ; preds = %1
  call void @llvm.aie2p.acquire(i32 48, i32 -1)
  call void @llvm.aie2p.acquire(i32 51, i32 -1)
  call void @llvm.assume(i1 true) [ "align"(ptr @input_fifo_cons_buff_0, i64 32) ]
  call void @llvm.assume(i1 true) [ "align"(ptr @output_fifo_buff_0, i64 32) ]
  call void @elementwise_inc(ptr @input_fifo_cons_buff_0, ptr @output_fifo_buff_0)
  call void @llvm.aie2p.release(i32 50, i32 1)
  call void @llvm.aie2p.release(i32 49, i32 1)
  ret void
}

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(inaccessiblemem: write)
declare void @llvm.assume(i1 noundef) #0

attributes #0 = { nocallback nofree nosync nounwind willreturn memory(inaccessiblemem: write) }

!llvm.module.flags = !{!0}

!0 = !{i32 2, !"Debug Info Version", i32 3}
