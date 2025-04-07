#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <type_traits>
#include <aie_api/aie.hpp>

#define FACTOR 32

template<typename Tin, typename Tout>
void element_wise_prod_vec(Tin* A, Tin* B, Tout* Y, int32_t N) {
    for(int i = 0; i < N; i++) chess_prepare_for_pipelining {
        aie::vector<Tin, FACTOR> vA = aie::load_v<FACTOR>(A);
        aie::vector<Tin, FACTOR> vB = aie::load_v<FACTOR>(B);
    
        aie::vector<Tout, FACTOR> vY = aie::mul(vA, vB);

        aie::store_v(Y, vY);

        A += 32;
        B += 32;
        Y += 32;
    }    
}

template<typename Tin, typename Tout>
void element_wise_sum_vec(Tin* A, Tin* B, Tout* Y, int32_t N) {
    for(int i = 0; i < N; i++) chess_prepare_for_pipelining {
        aie::vector<Tin, FACTOR> vA = aie::load_v<FACTOR>(A);
        aie::vector<Tin, FACTOR> vB = aie::load_v<FACTOR>(B);
    
        aie::vector<Tout, FACTOR> vY = aie::add(vA, vB);

        aie::store_v(Y, vY);

        A += FACTOR;
        B += FACTOR;
        Y += FACTOR;
    }  
}

template<typename Tin, typename Tout>
void element_wise_increment_kernel(Tin* A, Tin* X, Tout* Yin, Tout* Yout, int32_t start, int32_t N) {
    for(int i = start; i < N; i++) chess_prepare_for_pipelining chess_loop_range(0, FACTOR - 1) {
        Yout[i] = Yin[i] + A[i] * X[i];
    }
}

template<typename T>
void merge_vec(T* A, T* B, T* Y, int32_t N) {
    for(int i = start; i < N; i++) chess_prepare_for_pipelining chess_loop_range(0, FACTOR - 1) {
        aie::vector<Tin, FACTOR> vA = aie::load_v<FACTOR>(A);
        aie::vector<Tin, FACTOR> vB = aie::load_v<FACTOR>(B);

        A += FACTOR;     
        B += FACTOR;

        aie::store_v(Y, vA);
        Y += FACTOR;
        
        aie::store_v(Y, vB);
        Y += FACTOR;
    }
}

extern "C" {
    void element_wise_prod_bfloat16_vec(bfloat16* A, bfloat16* B, bfloat16* Y, int32_t N) {
        element_wise_prod_vec<bfloat16, bfloat16>(A, B, Y, N);
    }

    void element_wise_sum_bfloat16_vec(bfloat16* A, bfloat16* B, bfloat16* Y, int32_t N) {
        element_wise_sum_vec<bfloat16, bfloat16>(A, B, Y, N);
    }

    void merge_bfloat16_vec(bfloat16* A, bfloat16* B, bfloat16* Y, int32_t N) {
        merge_vec<bfloat16>(A, B, Y, N);
    }
}