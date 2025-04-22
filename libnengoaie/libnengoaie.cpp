#include <iostream>
#include <vector>
#include <cstdint>
#include <stdfloat>

#include "libnengoaie.hpp"
#include "utils.hpp"

#include "xrt/xrt_bo.h"
#include "xrt/xrt_device.h"
#include "xrt/xrt_kernel.h"

typedef uint32_t instr_t;

void test_aie() {
    constexpr int32_t size = 96;
    
    std::vector<instr_t> instructions = utils::load_instr_binary("./build/insts.bin");
    
    auto device = xrt::device(0);

    auto xclbin = xrt::xclbin("./build/nengoaie.xclbin");
    auto xkernels = xclbin.get_kernels();
    std::string kernel_name = xkernels[0].get_name();

    device.register_xclbin(xclbin);

    xrt::hw_context context(device, xclbin.get_uuid());

    xrt::kernel kernel = xrt::kernel(context, kernel_name);
    
    auto bo_instr = xrt::bo(device, instructions.size() * sizeof(instr_t), XCL_BO_FLAGS_CACHEABLE, kernel.group_id(1));
    
    auto param_bo = xrt::bo(device, 1 * sizeof(int32_t), XCL_BO_FLAGS_HOST_ONLY, kernel.group_id(3));
    auto data_bo = xrt::bo(device, 3 * size * sizeof(std::bfloat16_t), XCL_BO_FLAGS_HOST_ONLY, kernel.group_id(4));
    auto result_bo = xrt::bo(device, size * sizeof(std::bfloat16_t), XCL_BO_FLAGS_HOST_ONLY, kernel.group_id(5));
    
    void* bufInstr = bo_instr.map<void *>();
    memcpy(bufInstr, instructions.data(), instructions.size() * sizeof(instr_t));
    bo_instr.sync(XCL_BO_SYNC_BO_TO_DEVICE);

    std::int32_t* param_p = param_bo.map<std::int32_t *>();
    std::bfloat16_t* data_p = data_bo.map<std::bfloat16_t *>();
    std::bfloat16_t* result_p = result_bo.map<std::bfloat16_t *>();

    
    param_p[0] = size;
    
    /*
    for(size_t i = 0; i < size / 32; i++) {
        for(size_t j = 0; j < 32; j++) {
            data_p[i * 32 + j] = (std::bfloat16_t) (i + 1);
        }
    }
    */

    for(size_t i = 0; i < size; i++) {
        data_p[i] = 1;
    }
    
    param_bo.sync(XCL_BO_SYNC_BO_TO_DEVICE);
    data_bo.sync(XCL_BO_SYNC_BO_TO_DEVICE);

    
    auto run = kernel(3, bo_instr, instructions.size(), param_bo, data_bo, result_bo);
    
    run.wait();
    
    result_bo.sync(XCL_BO_SYNC_BO_FROM_DEVICE);

    for(size_t i = 0; i < size; i++) {
        std::cout << result_p[i] << std::endl;
    }
}