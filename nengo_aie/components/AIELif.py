import pyxrt as xrt  # type: ignore
import nengo.neurons

from ..AIEManager import AIEManager, AIEContext
from ..aie_kernels import LIFNeuronBuilder
from ..rc import DEFAULT_DEVICE, ITEMTYPE


class AIELif(nengo.neurons.LIF):
    def __init__(self, size, dt, tau_rc=0.02, tau_ref=0.002, min_voltage=0, amplitude=1, initial_state=None):
        super().__init__(tau_rc=tau_rc, tau_ref=tau_ref,
                         amplitude=amplitude, initial_state=initial_state)

        # For size and dt parameters, we had two options:
        # a) we pass them as parameters in the constructor duplicating information (double source of truth)
        # b) we program the NPU during the first step
        # both options are viable and have their problems. The first option has been chosen at this moment.

        self.size = AIEManager.next_multiple_of(16)(size)
        self.dt = dt
        self.min_voltage = min_voltage

        builder = LIFNeuronBuilder()
        (insts_path, xclbin_path) = builder.build(DEFAULT_DEVICE, self.size, tau_rc=self.tau_rc,
                                                  tau_ref=self.tau_ref, min_voltage=self.min_voltage, dt=dt, amplitude=self.amplitude)
        (device, kernel) = AIEManager.init_aie(xclbin_path)
        (instr_v, instr_bo) = AIEManager.load_insts(insts_path, device, kernel)

        self.context = AIEContext(device, kernel, instr_v, instr_bo)

        self.input_bo = self.context.create_inout_bo(
            "input", 3 * self.size, ITEMTYPE().itemsize)
        self.output_bo = self.context.create_inout_bo(
            "output_bo", 3 * self.size, ITEMTYPE().itemsize)

    def step(self, dt, J, output, voltage, refractory_time):
        # As per comment in the constructor, we now have two places from which to read the "dt" value.
        # The one we use is the parameter.
        assert dt == self.dt

        for i, buff in enumerate([J, voltage, refractory_time]):
            self.input_bo.write(buff.astype(ITEMTYPE), self.size *
                                i * ITEMTYPE().itemsize)
            self.input_bo.sync(xrt.xclBOSyncDirection.XCL_BO_SYNC_BO_TO_DEVICE)

        self.context.kernel_call(self.input_bo, self.output_bo)  # type: ignore

        self.output_bo.sync(xrt.xclBOSyncDirection.XCL_BO_SYNC_BO_FROM_DEVICE)

        output[...] = self.output_bo.read(
            self.size * ITEMTYPE().itemsize, 0).view(ITEMTYPE)[:output.size]
        voltage[...] = self.output_bo.read(
            self.size * ITEMTYPE().itemsize, self.size * ITEMTYPE().itemsize).view(ITEMTYPE)[:voltage.size]
        refractory_time[...] = self.output_bo.read(
            self.size * ITEMTYPE().itemsize, 2 * self.size * ITEMTYPE().itemsize).view(ITEMTYPE)[:refractory_time.size]
