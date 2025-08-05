#include <aie_api/aie.hpp>

typedef bfloat16 dtype;
constexpr int vec_factor = 32;

namespace m {
    #define EXPM1_PRECISION (11)
    #define LOG1P_PRECISION (16)

    constexpr bfloat16 BF16_NULL = (bfloat16) 0.0f;
    constexpr bfloat16 BF16_UNIT = (bfloat16) 1.0f;

    // Computes exp(x) - 1 using taylor series expansion
    __attribute__((inline)) aie::accum<accfloat, vec_factor> expm1(aie::vector<dtype, vec_factor> xs) {
        event0();

        dtype inv_factorials[EXPM1_PRECISION] = {
            1.0f,
            1.0f,
            0.5f,
            0.16666666666666666f,
            0.041666666666666664f,
            0.008333333333333333f,
            0.001388888888888889f,
            0.0001984126984126984f,
            2.48015873015873e-05f,
            2.7557319223985893e-06f,
            2.755731922398589e-07f
        };

        aie::accum<accfloat, vec_factor> xs_exp(aie::broadcast<dtype, vec_factor>(1.0));
        aie::accum<accfloat, vec_factor> xs_sum(aie::broadcast<dtype, vec_factor>(0.0));

        for(int i = 0; i < EXPM1_PRECISION; i++) chess_prepare_for_pipelining chess_loop_range(EXPM1_PRECISION, ) {
            xs_sum = aie::mac(xs_sum, xs_exp.template to_vector<dtype>(), inv_factorials[i]);
            xs_exp = aie::mul(xs_exp.template to_vector<dtype>(), xs);
        }

        event1();

        return aie::sub(xs_sum, 1.0f);
    }

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

        dtype signed_inv[LOG1P_PRECISION] = {
            1.0f,
            -0.5f,
            0.3333333333333333f,
            -0.25f,
            0.2f,
            -0.16666666666666666f,
            0.14285714285714285f,
            -0.125f,
            0.1111111111111111f,
            -0.1f,
            0.09090909090909091f,
            -0.08333333333333333f,
            0.07692307692307693f,
            -0.07142857142857142f,
            0.06666666666666667f,
            -0.0625f
};

        event0();

        aie::mask<vec_factor> flip_mask = aie::gt(aie::abs(xs), (dtype)1.0f);

        aie::vector<dtype, vec_factor> negdiv = aie::neg(aie::div(xs, aie::add(xs, (dtype)1.0f)));

        xs = aie::select(xs, negdiv, flip_mask);

        aie::accum<accfloat, vec_factor> xs_exp(aie::broadcast<dtype, vec_factor>(1.0f));
        aie::accum<accfloat, vec_factor> xs_sum(aie::broadcast<dtype, vec_factor>(0.0f));

        for (int i = 0; i < LOG1P_PRECISION; i++)
            chess_prepare_for_pipelining chess_loop_range(LOG1P_PRECISION, )
            {
                xs_exp = aie::mul(xs_exp.template to_vector<dtype>(), xs);
                xs_sum = aie::mac(xs_sum, xs_exp.template to_vector<dtype>(), signed_inv[i]);
            }

        event1();

        return aie::select(xs_sum.template to_vector<dtype>(), aie::neg(xs_sum).template to_vector<dtype>(), flip_mask);
    }

    // __attribute__((inline)) aie::vector<dtype, vec_factor> load_2x16xf32_into_1x32xbf16(float* __restrict p) {
    //     aie::vector<float, 16> v1 = aie::load_v(p);
    //     aie::vector<float, 16> v2 = aie::load_v(p + 16);
    //     aie::vector<dtype, 32> out = aie::concat(
    //         aie::filter_odd(v1.cast_to<char>(), 2),
    //         aie::filter_odd(v2.cast_to<char>(), 2)
    //     ).cast_to<dtype>();
    //     return out;
    // }

    // __attribute__((inline)) void store_1x32xbf16_into_1x16xf32(float* __restrict p, aie::vector<dtype, 32> v) {
    //     aie::store_v(p, aie::interleave_zip(v, aie::broadcast<int16>(0).cast_to<dtype>(), 1).first.cast_to<float>());
    // }

}

extern "C" {
    void lif_kernel(dtype tau_rc_in, dtype tau_ref_in, dtype min_voltage_in, dtype dt_in, dtype amplitude_in,
                    dtype* in, dtype* out)
    {
        dtype* __restrict pIn = in;
        dtype* __restrict pOut = out;

        event0();
        dtype spike_height = amplitude_in / dt_in;

        aie::vector<dtype, vec_factor> input_currents = aie::load_v<vec_factor>(pIn);
        pIn += vec_factor;
        aie::vector<dtype, vec_factor> voltages = aie::load_v<vec_factor>(pIn);
        pIn += vec_factor;
        aie::vector<dtype, vec_factor> refractory_times = aie::load_v<vec_factor>(pIn);
        pIn += vec_factor;

        aie::vector<dtype, vec_factor> output;

        refractory_times = aie::sub(refractory_times, dt_in);
        
        aie::vector<dtype, vec_factor> delta_t = aie::clamp(aie::sub(dt_in, refractory_times), m::BF16_NULL, dt_in);
        aie::vector<dtype, vec_factor> delta_iv = aie::sub(input_currents, voltages);
        aie::vector<dtype, vec_factor> exponential = m::expm1(aie::div(aie::neg(delta_t), tau_rc_in).template to_vector<dtype>());
        
        voltages = aie::sub(voltages, aie::mul(delta_iv, exponential).template to_vector<dtype>());
        
        aie::mask<vec_factor> spike_mask = aie::gt(voltages, m::BF16_UNIT);
        
        output = aie::select(m::BF16_NULL, spike_height, spike_mask);

        aie::vector<dtype, vec_factor> vm1 = aie::select(m::BF16_UNIT, aie::sub(voltages, m::BF16_UNIT), spike_mask);
        aie::vector<dtype, vec_factor> im1 = aie::select(m::BF16_UNIT, aie::sub(input_currents, m::BF16_UNIT), spike_mask);
        aie::vector<dtype, vec_factor> t_spike = aie::add(aie::mul(tau_rc_in, m::log1p(aie::neg(aie::div(vm1, im1)))), dt_in);

        voltages = aie::max(voltages, min_voltage_in);
        voltages = aie::select(voltages, m::BF16_NULL, spike_mask);

        refractory_times = aie::select(refractory_times, aie::add(tau_ref_in, t_spike), spike_mask);
    
        aie::store_v(pOut, output);
        pOut += vec_factor;
        aie::store_v(pOut, voltages);
        pOut += vec_factor;
        aie::store_v(pOut, refractory_times);
        pOut += vec_factor;

        event1();
    }
}