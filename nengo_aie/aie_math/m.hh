#ifndef _AIE_MATH_HH_
#define _AIE_MATH_HH_

#include <aie_api/aie.hpp>
#include <array>
#include <cstddef>

namespace m
{

    template <typename T, std::size_t N>
    constexpr std::array<T, N> inverse_factorials()
    {
        std::array<T, N> results{};
        unsigned long long int accum = 1;

        if (N > 0)
        {
            results[0] = static_cast<T>(1);
        }

        for (std::size_t i = 1; i < N; ++i)
        {
            accum *= i;
            results[i] = static_cast<T>(1) / static_cast<T>(accum);
        }

        return results;
    }

    template <typename T, std::size_t N>
    constexpr std::array<T, N> alt_signed_inverses()
    {
        std::array<T, N> results{};

        for (std::size_t i = 1; i <= N; ++i)
        {
            results[i - 1] = static_cast<T>(1) / static_cast<T>(i) * static_cast<T>(i % 2 == 0 ? -1 : 1);
        }

        return results;
    }

    constexpr bfloat16 BF16_NULL = (bfloat16)0.0f;
    constexpr bfloat16 BF16_UNIT = (bfloat16)1.0f;

    // Computes exp(x) - 1 using taylor series expansion
    template <typename dtype, typename acctype, std::size_t vec_factor, std::size_t precision>
    __attribute__((inline)) aie::accum<acctype, vec_factor> expm1(aie::vector<dtype, vec_factor> xs)
    {
        event0();

        // dtype inv_factorials[EXPM1_PRECISION] = {
        //     1.0f,
        //     1.0f,
        //     0.5f,
        //     0.16666666666666666f,
        //     0.041666666666666664f,
        //     0.008333333333333333f,
        //     0.001388888888888889f,
        //     0.0001984126984126984f,
        //     2.48015873015873e-05f,
        //     2.7557319223985893e-06f,
        //     2.755731922398589e-07f};

        constexpr std::array<dtype, precision> inv_factorials = inverse_factorials<dtype, precision>();

        aie::accum<acctype, vec_factor> xs_exp(aie::broadcast<dtype, vec_factor>(1.0));
        aie::accum<acctype, vec_factor> xs_sum(aie::broadcast<dtype, vec_factor>(0.0));

        for (int i = 0; i < precision; i++)
            chess_prepare_for_pipelining chess_loop_range(precision, )
            {
                xs_sum = aie::mac(xs_sum, xs_exp.template to_vector<dtype>(), inv_factorials[i]);
                xs_exp = aie::mul(xs_exp.template to_vector<dtype>(), xs);
            }

        event1();

        return aie::sub(xs_sum, 1.0f);
    }

    template <typename dtype, typename acctype, std::size_t vec_factor, std::size_t precision>
    __attribute__((inline)) aie::vector<dtype, vec_factor> log1p(aie::vector<dtype, vec_factor> xs)
    {
        /*
            We know that
                f(x) = ln(1 + x) = \sum_{i=1}^\infty \frac{x^i}{i} \cdot (-1)^{i+1}
            but we also know that this is accurate for -1 < x < 1 so, if x is outside said range,
            we make use of the following property
                ln(x) = -ln(1/x)
            to write that
                f(x) = ln(1 + x) = -ln(1 / (1 + x)) = -ln((1 + x - x) / (1 + x)) = -ln(1 - x / (1 + x)) = -f(-x / (1 + x))
            so we substitute x with -x / (1 + x) when it's the case and then we negate the result.
        */

        // dtype signed_inv[LOG1P_PRECISION] = {
        //     1.0f,
        //     -0.5f,
        //     0.3333333333333333f,
        //     -0.25f,
        //     0.2f,
        //     -0.16666666666666666f,
        //     0.14285714285714285f,
        //     -0.125f,
        //     0.1111111111111111f,
        //     -0.1f,
        //     0.09090909090909091f,
        //     -0.08333333333333333f,
        //     0.07692307692307693f,
        //     -0.07142857142857142f,
        //     0.06666666666666667f,
        //     -0.0625f};

        constexpr std::array<dtype, precision> signed_inv = alt_signed_inverses<dtype, precision>();

        event0();

        aie::mask<vec_factor> flip_mask = aie::gt(aie::abs(xs), (dtype)1.0f);

        aie::vector<dtype, vec_factor> negdiv = aie::neg(aie::div(xs, aie::add(xs, (dtype)1.0f)));

        xs = aie::select(xs, negdiv, flip_mask);

        aie::accum<acctype, vec_factor> xs_exp(aie::broadcast<dtype, vec_factor>(1.0f));
        aie::accum<acctype, vec_factor> xs_sum(aie::broadcast<dtype, vec_factor>(0.0f));

        for (int i = 0; i < precision; i++)
            chess_prepare_for_pipelining chess_loop_range(precision, )
            {
                xs_exp = aie::mul(xs_exp.template to_vector<dtype>(), xs);
                xs_sum = aie::mac(xs_sum, xs_exp.template to_vector<dtype>(), signed_inv[i]);
            }

        event1();

        return aie::select(xs_sum.template to_vector<dtype>(), aie::neg(xs_sum).template to_vector<dtype>(), flip_mask);
    }

}

#endif