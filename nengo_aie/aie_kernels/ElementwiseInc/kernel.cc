#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <type_traits>
#include <aie_api/aie.hpp>

typedef float dtype;

extern "C" {

void elementwise_inc(dtype* in1, dtype* out1) {
    dtype* __restrict pIn1 = in1;
    dtype* __restrict pOut1 = out1;

    constexpr int vec_factor = 16;

    aie::vector<dtype, vec_factor> vA = aie::load_v<vec_factor>(pIn1);
    pIn1 += vec_factor;

    aie::vector<dtype, vec_factor> vX = aie::load_v<vec_factor>(pIn1);
    pIn1 += vec_factor;

    aie::accum<accfloat, vec_factor> acc1 = aie::mul(vA, vX);
    
    aie::vector<dtype, vec_factor> vYin = aie::load_v<vec_factor>(pIn1);
    pIn1 += vec_factor;

    aie::accum<accfloat, vec_factor> acc2 = aie::add(acc1, vYin);

    aie::store_v(pOut1, acc2.template to_vector<dtype>(0));

    pOut1 += vec_factor;
}
 
} // extern "C"