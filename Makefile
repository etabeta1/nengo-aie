all: nengoaie.xclbin

nengoaie.xclbin: kernels
	@mkdir -p build
	@cp kernels/*.o build/
	@cd build && aiecc.py --aie-generate-xclbin --no-compile-host --xclbin-name=$(@F) \
		--no-xchesscc --no-xbridge \
		--aie-generate-npu-insts --npu-insts-name=insts.bin ../layers/ewi.mlir ../kernels/element_wise_increment.o

kernels:
	@$(MAKE) -C kernels all

clean:
	@$(MAKE) -C kernels clean
	@rm -rf build/*

.PHONY: all clean kernels

include make.defs
