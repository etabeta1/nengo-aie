#pragma ONCE

#include <iostream>

#include "xrt/xrt_bo.h"
#include "xrt/xrt_device.h"
#include "xrt/xrt_kernel.h"

extern "C" {
    void test_aie();
}

std::vector<uint32_t> load_instr_binary(std::string path);