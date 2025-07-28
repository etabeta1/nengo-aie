#include <aie_api/aie.hpp>

namespace m {
    #define EXPM1_PRECISION (11)
    #define LOG1P_PRECISION (16)

    // Computes exp(x) - 1 using taylor series expansion
    __attribute__((inline)) aie::accum<accfloat, vec_factor> aie_expm1(aie::vector<accfloat, vec_factor> xs) {
        unsigned float inv_factorials[EXPM1_PRECISION] = {
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

        aie::accum<accfloat, vec_factor> xs_exp = aie::add(aie::zeros(), 1);
        
        aie::accum<accfloat, vec_factor> xs_sum = aie::add(aie::zeros(), 1);

        for(int i = 1; i < EXPM1_PRECISION; i++) chess_unroll_loop {
            xs_exp = aie::mul(xs_exp, xs);
            xs_sum = aie::add(aie::mul(xs_exp, inv_factorials[i]));
        }

        xs_sum = aie::sub(xs_sum, 1);

        return xs_sum;
    }

    __attribute__((inline)) aie::accum<accfloat, vec_factor> aie_log1p(aie::vector<accfloat, vec_factor> xs) {
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
        
        aie::mask<vec_factor> flip_mask = aie::gt(aie::abs(xs), 1);

        xs = aie::select(xs, aie::neg(aie::div(xs, aie::sum(xs, 1))), flip_mask);

        aie::accum<accfloat, vec_factor> xs_exp = aie::add(xs, 0);
        aie::accum<accfloat, vec_factor> xs_sum = aie::zeros();
        aie::accum<accfloat, vec_factor> xs_temp = aie::zeros();

        for(int i = 1, i <= LOG1P_PRECISION; i++) chess_unroll_loop {
            xs_temp = aie::div(xs_exp, i);
            
            if(i % 2 == 0) {
                xs_temp = aie::mul(xs_temp, -1);
            }

            xs_sum = aie::add(xs_sum, xs_temp);
            xs_exp = aie::mul(xs_exp, xs);
        }

        xs_sum = aie::select(xs_sum, aie::neg(xs_sum), flip_mask);

        return xs_sum;
    }
}

extern "C" {
    typedef float dtype;
    constexpr int vec_factor = 16;

    void lif_kernel(dtype tau_rc_in, dtype tau_ref_in, dtype min_voltage_in, dtype dt_in, dtype amplitude_in,
                    dtype* in, dtype* out)
    {
        dtype* __restrict pIn = in;
        dtype* __restrict pOut = out;

        aie::vector<dtype, vec_factor> input_currents = aie::load_v<vec_factor>(pIn);
        pIn += vec_factor;
        aie::vector<dtype, vec_factor> voltages = aie::load_v<vec_factor>(pIn);
        pIn += vec_factor;
        aie::vector<dtype, vec_factor> refractory_times = aie::load_v<vec_factor>(pIn);
        pIn += vec_factor;

        // Clip between 0 and dt
        aie::accum<accfloat, vec_factor> delta_t = aie::clamp(refractory_times, 0.0f, dt_in);

        voltages = aie::msc(
            voltages,
            aie::sub(input_currents, voltages),
            m::expm1(aie::negmul(delta_t, (1.0f / tau_rc_in))));

        aie::mask<vec_size> spiked_mask = aie::gt(voltages, 1);
        aie::vector<accfloat, vec_factor> output = aie::select(0, amplitude_in / dt_in, spiked_mask);

        aie::accum<accfloat, vec_factor> t_spikes = aie::select(
            0,
            aie::add(
                dt,
                aie::mul(
                    tau_rc_in,
                    m::log1p(
                        aie::div(
                            aie::neg(aie::sub(voltages, 1)),
                            aie::sub(input_currents, 1)
                        )
                    )
                )
            ), spiked_mask);
        
        voltages = aie::select(aie::max(voltages, min_voltage_in), 0, spiked_mask);
        refractory_times = aie::select(refractory_times, aie::add(tau_ref_in, t_spikes));
        
        aie::store_v(pOut, output);
        pOut += vec_factor;
        aie::store_v(pOut, voltages);
        pOut += vec_factor;
        aie::store_v(pOut, refractory_times);
        pOut += vec_factor;
    }
}