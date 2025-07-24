; ModuleID = '/notebooks/nengo-aie/tmpbm3c36ah.mlir.prj/input.llpeanohack.ll'
source_filename = "LLVMDialectModule"
target datalayout = "e-m:e-p:20:32-i1:8:32-i8:8:32-i16:16:32-i32:32:32-f32:32:32-i64:32-f64:32-a:0:32-n32"
target triple = "aie2"

@input_fifo_cons_buff_1 = external global [96 x half]
@input_fifo_cons_buff_0 = external global [96 x half]
@output_fifo_buff_1 = external global [32 x half]
@output_fifo_buff_0 = external global [32 x half]

; Function Attrs: nounwind
declare void @llvm.aie2.acquire(i32, i32) #0

; Function Attrs: nounwind
declare void @llvm.aie2.release(i32, i32) #0

declare void @elementwise_inc(ptr, ptr) local_unnamed_addr

define void @core_0_2() local_unnamed_addr {
  br label %.preheader3

.preheader3:                                      ; preds = %0, %15
  %1 = phi i64 [ 0, %0 ], [ %16, %15 ]
  br label %2

2:                                                ; preds = %6, %.preheader3
  %3 = phi i64 [ 0, %.preheader3 ], [ %7, %6 ]
  tail call void @llvm.aie2.acquire(i32 50, i32 -1)
  tail call void @llvm.aie2.acquire(i32 49, i32 -1)
  tail call void @elementwise_inc(ptr nonnull @input_fifo_cons_buff_0, ptr nonnull @output_fifo_buff_0)
  tail call void @llvm.aie2.release(i32 48, i32 1)
  tail call void @llvm.aie2.release(i32 51, i32 1)
  tail call void @llvm.aie2.acquire(i32 50, i32 -1)
  tail call void @llvm.aie2.acquire(i32 49, i32 -1)
  tail call void @elementwise_inc(ptr nonnull @input_fifo_cons_buff_1, ptr nonnull @output_fifo_buff_1)
  tail call void @llvm.aie2.release(i32 48, i32 1)
  tail call void @llvm.aie2.release(i32 51, i32 1)
  tail call void @llvm.aie2.acquire(i32 50, i32 -1)
  tail call void @llvm.aie2.acquire(i32 49, i32 -1)
  tail call void @elementwise_inc(ptr nonnull @input_fifo_cons_buff_0, ptr nonnull @output_fifo_buff_0)
  tail call void @llvm.aie2.release(i32 48, i32 1)
  tail call void @llvm.aie2.release(i32 51, i32 1)
  tail call void @llvm.aie2.acquire(i32 50, i32 -1)
  tail call void @llvm.aie2.acquire(i32 49, i32 -1)
  tail call void @elementwise_inc(ptr nonnull @input_fifo_cons_buff_1, ptr nonnull @output_fifo_buff_1)
  tail call void @llvm.aie2.release(i32 48, i32 1)
  tail call void @llvm.aie2.release(i32 51, i32 1)
  %4 = or disjoint i64 %3, 4
  tail call void @llvm.aie2.acquire(i32 50, i32 -1)
  tail call void @llvm.aie2.acquire(i32 49, i32 -1)
  tail call void @elementwise_inc(ptr nonnull @input_fifo_cons_buff_0, ptr nonnull @output_fifo_buff_0)
  tail call void @llvm.aie2.release(i32 48, i32 1)
  tail call void @llvm.aie2.release(i32 51, i32 1)
  tail call void @llvm.aie2.acquire(i32 50, i32 -1)
  tail call void @llvm.aie2.acquire(i32 49, i32 -1)
  tail call void @elementwise_inc(ptr nonnull @input_fifo_cons_buff_1, ptr nonnull @output_fifo_buff_1)
  tail call void @llvm.aie2.release(i32 48, i32 1)
  tail call void @llvm.aie2.release(i32 51, i32 1)
  %5 = icmp ult i64 %4, 4294967292
  br i1 %5, label %6, label %8

6:                                                ; preds = %2
  tail call void @llvm.aie2.acquire(i32 50, i32 -1)
  tail call void @llvm.aie2.acquire(i32 49, i32 -1)
  tail call void @elementwise_inc(ptr nonnull @input_fifo_cons_buff_0, ptr nonnull @output_fifo_buff_0)
  tail call void @llvm.aie2.release(i32 48, i32 1)
  tail call void @llvm.aie2.release(i32 51, i32 1)
  tail call void @llvm.aie2.acquire(i32 50, i32 -1)
  tail call void @llvm.aie2.acquire(i32 49, i32 -1)
  tail call void @elementwise_inc(ptr nonnull @input_fifo_cons_buff_1, ptr nonnull @output_fifo_buff_1)
  tail call void @llvm.aie2.release(i32 48, i32 1)
  tail call void @llvm.aie2.release(i32 51, i32 1)
  %7 = add nuw nsw i64 %3, 8
  br label %2

8:                                                ; preds = %2
  tail call void @llvm.aie2.acquire(i32 50, i32 -1)
  tail call void @llvm.aie2.acquire(i32 49, i32 -1)
  tail call void @elementwise_inc(ptr nonnull @input_fifo_cons_buff_0, ptr nonnull @output_fifo_buff_0)
  tail call void @llvm.aie2.release(i32 48, i32 1)
  tail call void @llvm.aie2.release(i32 51, i32 1)
  br label %9

9:                                                ; preds = %13, %8
  %10 = phi i64 [ 0, %8 ], [ %14, %13 ]
  tail call void @llvm.aie2.acquire(i32 50, i32 -1)
  tail call void @llvm.aie2.acquire(i32 49, i32 -1)
  tail call void @elementwise_inc(ptr nonnull @input_fifo_cons_buff_1, ptr nonnull @output_fifo_buff_1)
  tail call void @llvm.aie2.release(i32 48, i32 1)
  tail call void @llvm.aie2.release(i32 51, i32 1)
  tail call void @llvm.aie2.acquire(i32 50, i32 -1)
  tail call void @llvm.aie2.acquire(i32 49, i32 -1)
  tail call void @elementwise_inc(ptr nonnull @input_fifo_cons_buff_0, ptr nonnull @output_fifo_buff_0)
  tail call void @llvm.aie2.release(i32 48, i32 1)
  tail call void @llvm.aie2.release(i32 51, i32 1)
  tail call void @llvm.aie2.acquire(i32 50, i32 -1)
  tail call void @llvm.aie2.acquire(i32 49, i32 -1)
  tail call void @elementwise_inc(ptr nonnull @input_fifo_cons_buff_1, ptr nonnull @output_fifo_buff_1)
  tail call void @llvm.aie2.release(i32 48, i32 1)
  tail call void @llvm.aie2.release(i32 51, i32 1)
  tail call void @llvm.aie2.acquire(i32 50, i32 -1)
  tail call void @llvm.aie2.acquire(i32 49, i32 -1)
  tail call void @elementwise_inc(ptr nonnull @input_fifo_cons_buff_0, ptr nonnull @output_fifo_buff_0)
  tail call void @llvm.aie2.release(i32 48, i32 1)
  tail call void @llvm.aie2.release(i32 51, i32 1)
  %11 = or disjoint i64 %10, 4
  tail call void @llvm.aie2.acquire(i32 50, i32 -1)
  tail call void @llvm.aie2.acquire(i32 49, i32 -1)
  tail call void @elementwise_inc(ptr nonnull @input_fifo_cons_buff_1, ptr nonnull @output_fifo_buff_1)
  tail call void @llvm.aie2.release(i32 48, i32 1)
  tail call void @llvm.aie2.release(i32 51, i32 1)
  tail call void @llvm.aie2.acquire(i32 50, i32 -1)
  tail call void @llvm.aie2.acquire(i32 49, i32 -1)
  tail call void @elementwise_inc(ptr nonnull @input_fifo_cons_buff_0, ptr nonnull @output_fifo_buff_0)
  tail call void @llvm.aie2.release(i32 48, i32 1)
  tail call void @llvm.aie2.release(i32 51, i32 1)
  %12 = icmp ult i64 %11, 4294967292
  br i1 %12, label %13, label %15

13:                                               ; preds = %9
  tail call void @llvm.aie2.acquire(i32 50, i32 -1)
  tail call void @llvm.aie2.acquire(i32 49, i32 -1)
  tail call void @elementwise_inc(ptr nonnull @input_fifo_cons_buff_1, ptr nonnull @output_fifo_buff_1)
  tail call void @llvm.aie2.release(i32 48, i32 1)
  tail call void @llvm.aie2.release(i32 51, i32 1)
  tail call void @llvm.aie2.acquire(i32 50, i32 -1)
  tail call void @llvm.aie2.acquire(i32 49, i32 -1)
  tail call void @elementwise_inc(ptr nonnull @input_fifo_cons_buff_0, ptr nonnull @output_fifo_buff_0)
  tail call void @llvm.aie2.release(i32 48, i32 1)
  tail call void @llvm.aie2.release(i32 51, i32 1)
  %14 = add nuw nsw i64 %10, 8
  br label %9

15:                                               ; preds = %9
  tail call void @llvm.aie2.acquire(i32 50, i32 -1)
  tail call void @llvm.aie2.acquire(i32 49, i32 -1)
  tail call void @elementwise_inc(ptr nonnull @input_fifo_cons_buff_1, ptr nonnull @output_fifo_buff_1)
  tail call void @llvm.aie2.release(i32 48, i32 1)
  tail call void @llvm.aie2.release(i32 51, i32 1)
  %16 = add nuw nsw i64 %1, 2
  %.not = icmp eq i64 %16, 9223372036854775806
  br i1 %.not, label %.preheader, label %.preheader3

.preheader:                                       ; preds = %15, %.preheader.3
  %17 = phi i64 [ %20, %.preheader.3 ], [ 0, %15 ]
  tail call void @llvm.aie2.acquire(i32 50, i32 -1)
  tail call void @llvm.aie2.acquire(i32 49, i32 -1)
  tail call void @elementwise_inc(ptr nonnull @input_fifo_cons_buff_0, ptr nonnull @output_fifo_buff_0)
  tail call void @llvm.aie2.release(i32 48, i32 1)
  tail call void @llvm.aie2.release(i32 51, i32 1)
  tail call void @llvm.aie2.acquire(i32 50, i32 -1)
  tail call void @llvm.aie2.acquire(i32 49, i32 -1)
  tail call void @elementwise_inc(ptr nonnull @input_fifo_cons_buff_1, ptr nonnull @output_fifo_buff_1)
  tail call void @llvm.aie2.release(i32 48, i32 1)
  tail call void @llvm.aie2.release(i32 51, i32 1)
  tail call void @llvm.aie2.acquire(i32 50, i32 -1)
  tail call void @llvm.aie2.acquire(i32 49, i32 -1)
  tail call void @elementwise_inc(ptr nonnull @input_fifo_cons_buff_0, ptr nonnull @output_fifo_buff_0)
  tail call void @llvm.aie2.release(i32 48, i32 1)
  tail call void @llvm.aie2.release(i32 51, i32 1)
  tail call void @llvm.aie2.acquire(i32 50, i32 -1)
  tail call void @llvm.aie2.acquire(i32 49, i32 -1)
  tail call void @elementwise_inc(ptr nonnull @input_fifo_cons_buff_1, ptr nonnull @output_fifo_buff_1)
  tail call void @llvm.aie2.release(i32 48, i32 1)
  tail call void @llvm.aie2.release(i32 51, i32 1)
  %18 = or disjoint i64 %17, 4
  tail call void @llvm.aie2.acquire(i32 50, i32 -1)
  tail call void @llvm.aie2.acquire(i32 49, i32 -1)
  tail call void @elementwise_inc(ptr nonnull @input_fifo_cons_buff_0, ptr nonnull @output_fifo_buff_0)
  tail call void @llvm.aie2.release(i32 48, i32 1)
  tail call void @llvm.aie2.release(i32 51, i32 1)
  tail call void @llvm.aie2.acquire(i32 50, i32 -1)
  tail call void @llvm.aie2.acquire(i32 49, i32 -1)
  tail call void @elementwise_inc(ptr nonnull @input_fifo_cons_buff_1, ptr nonnull @output_fifo_buff_1)
  tail call void @llvm.aie2.release(i32 48, i32 1)
  tail call void @llvm.aie2.release(i32 51, i32 1)
  %19 = icmp ult i64 %18, 4294967292
  br i1 %19, label %.preheader.3, label %21

.preheader.3:                                     ; preds = %.preheader
  tail call void @llvm.aie2.acquire(i32 50, i32 -1)
  tail call void @llvm.aie2.acquire(i32 49, i32 -1)
  tail call void @elementwise_inc(ptr nonnull @input_fifo_cons_buff_0, ptr nonnull @output_fifo_buff_0)
  tail call void @llvm.aie2.release(i32 48, i32 1)
  tail call void @llvm.aie2.release(i32 51, i32 1)
  tail call void @llvm.aie2.acquire(i32 50, i32 -1)
  tail call void @llvm.aie2.acquire(i32 49, i32 -1)
  tail call void @elementwise_inc(ptr nonnull @input_fifo_cons_buff_1, ptr nonnull @output_fifo_buff_1)
  tail call void @llvm.aie2.release(i32 48, i32 1)
  tail call void @llvm.aie2.release(i32 51, i32 1)
  %20 = add nuw nsw i64 %17, 8
  br label %.preheader

21:                                               ; preds = %.preheader
  tail call void @llvm.aie2.acquire(i32 50, i32 -1)
  tail call void @llvm.aie2.acquire(i32 49, i32 -1)
  tail call void @elementwise_inc(ptr nonnull @input_fifo_cons_buff_0, ptr nonnull @output_fifo_buff_0)
  tail call void @llvm.aie2.release(i32 48, i32 1)
  tail call void @llvm.aie2.release(i32 51, i32 1)
  ret void
}

attributes #0 = { nounwind }

!llvm.module.flags = !{!0}

!0 = !{i32 2, !"Debug Info Version", i32 3}
