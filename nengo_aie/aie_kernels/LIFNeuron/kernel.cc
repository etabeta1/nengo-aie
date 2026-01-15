#include <aie_api/aie.hpp>

typedef bfloat16 dtype;
constexpr int vec_factor = 32;

#define EXPM1_PRECISION (11)
#define LOG1P_PRECISION (16)

extern "C"
{
    void lif_kernel_step_1(float _tau_rc, float _tau_ref, float _min_voltage, float _dt, float _amplitude, float _spike_height, dtype *_pIn, dtype *_pOut)
    {
        dtype *__restrict pIn = _pIn;
        dtype *__restrict pOut1 = _pOut;

        event0();

        dtype tau_rc = (dtype)_tau_rc;
        dtype tau_ref = (dtype)_tau_ref;
        dtype min_voltage = (dtype)_min_voltage;
        dtype dt = (dtype)_dt;
        dtype amplitude = (dtype)_amplitude;
        dtype spike_height = (dtype)_spike_height;

        aie::vector<dtype, vec_factor> input_currents = aie::load_v<vec_factor>(pIn);
        aie::store_v(pOut1, input_currents);
        aie::vector<dtype, vec_factor> voltages = aie::load_v<vec_factor>(pIn + vec_factor);
        aie::vector<dtype, vec_factor> refractory_times = aie::load_v<vec_factor>(pIn + 2 * vec_factor);

        refractory_times = aie::sub(refractory_times, dt);
        aie::store_v(pOut1 + 2 * vec_factor, refractory_times);

        aie::vector<dtype, vec_factor> delta_t = aie::clamp(aie::sub(dt, refractory_times), m::BF16_NULL, dt);
        aie::vector<dtype, vec_factor> delta_iv = aie::sub(input_currents, voltages);
        aie::vector<dtype, vec_factor> exponential = m::expm1(aie::div(aie::neg(delta_t), tau_rc).template to_vector<dtype>());

        voltages = aie::sub(voltages, aie::mul(delta_iv, exponential).template to_vector<dtype>());
        aie::store_v(pOut1 + vec_factor, voltages);

        event1();
    }

    void lif_kernel_step_2(float _tau_rc, float _tau_ref, float _min_voltage, float _dt, float _amplitude, float _spike_height, dtype *_pIn, dtype *_pOut)
    {
        dtype *__restrict pIn1 = _pIn;
        dtype *__restrict pOut = _pOut;

        event0();

        dtype tau_rc = (dtype)_tau_rc;
        dtype tau_ref = (dtype)_tau_ref;
        dtype min_voltage = (dtype)_min_voltage;
        dtype dt = (dtype)_dt;
        dtype amplitude = (dtype)_amplitude;
        dtype spike_height = (dtype)_spike_height;

        aie::vector<dtype, vec_factor> input_currents = aie::load_v<vec_factor>(pIn1);
        aie::vector<dtype, vec_factor> voltages = aie::load_v<vec_factor>(pIn1 + vec_factor);
        aie::vector<dtype, vec_factor> refractory_times = aie::load_v<vec_factor>(pIn1 + 2 * vec_factor);

        aie::mask<vec_factor> spike_mask = aie::gt(voltages, m::BF16_UNIT);

        aie::vector<dtype, vec_factor> vm1_ns = aie::sub(voltages, m::BF16_UNIT);
        aie::vector<dtype, vec_factor> vm1 = aie::select(m::BF16_UNIT, vm1_ns, spike_mask);

        aie::vector<dtype, vec_factor> im1_ns = aie::sub(input_currents, m::BF16_UNIT);
        aie::vector<dtype, vec_factor> im1 = aie::select(m::BF16_UNIT * 2, im1_ns, spike_mask);

        aie::vector<dtype, vec_factor> negdiv = aie::neg(aie::div(vm1, im1));
        aie::vector<dtype, vec_factor> t_spike = aie::add(aie::mul(tau_rc, m::log1p(negdiv)), dt);

        aie::vector<dtype, vec_factor> output = aie::select(m::BF16_NULL, spike_height, spike_mask);
        aie::store_v(pOut, output);

        voltages = aie::max(voltages, min_voltage);
        voltages = aie::select(voltages, m::BF16_NULL, spike_mask);
        aie::store_v(pOut + vec_factor, voltages);

        refractory_times = aie::select(refractory_times, aie::add(tau_ref, t_spike), spike_mask);
        aie::store_v(pOut + 2 * vec_factor, refractory_times);

        event1();
    }
}