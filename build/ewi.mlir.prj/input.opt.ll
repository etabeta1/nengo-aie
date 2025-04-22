; ModuleID = '/notebooks/nengo-aie/build/ewi.mlir.prj/input.llpeanohack.ll'
source_filename = "LLVMDialectModule"
target datalayout = "e-m:e-p:20:32-i1:8:32-i8:8:32-i16:16:32-i32:32:32-f32:32:32-i64:32-f64:32-a:0:32-n32"
target triple = "aie2"

@data_input_fifo_cons_buff_1 = external global [288 x half]
@data_input_fifo_cons_buff_0 = external global [288 x half]
@param_input_fifo_cons_buff_1 = external global [1 x i32]
@param_input_fifo_cons_buff_0 = external global [1 x i32]
@output_fifo_buff_1 = external global [288 x half]
@output_fifo_buff_0 = external global [288 x half]

; Function Attrs: nounwind
declare void @llvm.aie2.acquire(i32, i32) #0

; Function Attrs: nounwind
declare void @llvm.aie2.release(i32, i32) #0

declare void @elementwise_inc(ptr, ptr, ptr) local_unnamed_addr

define void @core_0_2() local_unnamed_addr {
  br label %1

1:                                                ; preds = %0, %1
  %2 = phi i64 [ 0, %0 ], [ %3, %1 ]
  tail call void @llvm.aie2.acquire(i32 51, i32 -1)
  tail call void @llvm.aie2.acquire(i32 52, i32 -1)
  tail call void @llvm.aie2.acquire(i32 49, i32 -1)
  call void @llvm.assume(i1 true) [ "align"(ptr @output_fifo_buff_0, i64 32) ]
  call void @llvm.assume(i1 true) [ "align"(ptr @param_input_fifo_cons_buff_0, i64 32) ]
  call void @llvm.assume(i1 true) [ "align"(ptr @data_input_fifo_cons_buff_0, i64 32) ]
  tail call void @elementwise_inc(ptr nonnull @param_input_fifo_cons_buff_0, ptr nonnull @data_input_fifo_cons_buff_0, ptr nonnull @output_fifo_buff_0)
  tail call void @llvm.aie2.release(i32 48, i32 1)
  tail call void @llvm.aie2.release(i32 53, i32 1)
  tail call void @llvm.aie2.release(i32 50, i32 1)
  tail call void @llvm.aie2.acquire(i32 51, i32 -1)
  tail call void @llvm.aie2.acquire(i32 52, i32 -1)
  tail call void @llvm.aie2.acquire(i32 49, i32 -1)
  call void @llvm.assume(i1 true) [ "align"(ptr @output_fifo_buff_1, i64 32) ]
  call void @llvm.assume(i1 true) [ "align"(ptr @param_input_fifo_cons_buff_1, i64 32) ]
  call void @llvm.assume(i1 true) [ "align"(ptr @data_input_fifo_cons_buff_1, i64 32) ]
  tail call void @elementwise_inc(ptr nonnull @param_input_fifo_cons_buff_1, ptr nonnull @data_input_fifo_cons_buff_1, ptr nonnull @output_fifo_buff_1)
  tail call void @llvm.aie2.release(i32 48, i32 1)
  tail call void @llvm.aie2.release(i32 53, i32 1)
  tail call void @llvm.aie2.release(i32 50, i32 1)
  %3 = add nuw nsw i64 %2, 2
  %.not = icmp eq i64 %3, 9223372036854775806
  br i1 %.not, label %4, label %1

4:                                                ; preds = %1
  tail call void @llvm.aie2.acquire(i32 51, i32 -1)
  tail call void @llvm.aie2.acquire(i32 52, i32 -1)
  tail call void @llvm.aie2.acquire(i32 49, i32 -1)
  call void @llvm.assume(i1 true) [ "align"(ptr @output_fifo_buff_0, i64 32) ]
  call void @llvm.assume(i1 true) [ "align"(ptr @param_input_fifo_cons_buff_0, i64 32) ]
  call void @llvm.assume(i1 true) [ "align"(ptr @data_input_fifo_cons_buff_0, i64 32) ]
  tail call void @elementwise_inc(ptr nonnull @param_input_fifo_cons_buff_0, ptr nonnull @data_input_fifo_cons_buff_0, ptr nonnull @output_fifo_buff_0)
  tail call void @llvm.aie2.release(i32 48, i32 1)
  tail call void @llvm.aie2.release(i32 53, i32 1)
  tail call void @llvm.aie2.release(i32 50, i32 1)
  ret void
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind willreturn memory(inaccessiblemem: write)
declare void @llvm.assume(i1 noundef) #1

attributes #0 = { nounwind }
attributes #1 = { mustprogress nocallback nofree nosync nounwind willreturn memory(inaccessiblemem: write) }

!llvm.module.flags = !{!0}

!0 = !{i32 2, !"Debug Info Version", i32 3}
