all: build/nengoaie.xclbin build/insts.bin libnengoaie

build/nengoaie.xclbin: kernels
	@mkdir -p build
	@cp kernels/*.o build/
	@cd build && aiecc.py --aie-generate-xclbin --no-compile-host --xclbin-name=$(@F) \
		--no-xchesscc --no-xbridge \
		--aie-generate-npu-insts --npu-insts-name=insts.bin ../layers/ewi.mlir ../build/element_wise_increment.o

kernels:
	@$(MAKE) -C kernels all

libnengoaie:
	@$(MAKE) -C libnengoaie all MLIR_AIE_PATH=$(MLIR_AIE_PATH)

clean:
	@$(MAKE) -C kernels clean
	@$(MAKE) -C libnengoaie clean
	@rm -rf build/*

run: all
	@./libnengoaie/test

.PHONY: all clean kernels test libnengoaie run

include make.defs
