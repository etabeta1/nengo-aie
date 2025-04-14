//===- vector_scaler_mul.cc -------------------------------------*- C++ -*-===//
//
// This file is licensed under the Apache License v2.0 with LLVM Exceptions.
// See https://llvm.org/LICENSE.txt for license information.
// SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
//
// Copyright (C) 2024, Advanced Micro Devices, Inc.
//
//===----------------------------------------------------------------------===//

#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <type_traits>
#include <aie_api/aie.hpp>

#include "common.hpp"

extern "C" {

void elementwise_inc(bfloat16* in1, bfloat16* out1) {
    bfloat16* __restrict pIn1 = in1;
    bfloat16* __restrict pOut1 = out1;

    constexpr int vec_factor = 32;

    int N = aie::load_v<vec_factor>(pIn1)[0];
    pIn1 += vec_factor;

    for(int i = 0; i < N / vec_factor; i++) {
        aie::vector<bfloat16, vec_factor> vA = aie::load_v<vec_factor>(pIn1);
        pIn1 += vec_factor;
    
        aie::vector<bfloat16, vec_factor> vX = aie::load_v<vec_factor>(pIn1);
        pIn1 += vec_factor;
    
        aie::accum<accfloat, vec_factor> acc1 = aie::mul(vA, vX);
    
        aie::vector<bfloat16, vec_factor> vYin = aie::load_v<vec_factor>(pIn1);
        pIn1 += vec_factor;
    
        aie::accum<accfloat, vec_factor> acc2 = aie::add(acc1, vYin);
    
        aie::store_v(pOut1, acc2.template to_vector<bfloat16>(0));
        pOut1 += vec_factor;
    }
}

} // extern "C"