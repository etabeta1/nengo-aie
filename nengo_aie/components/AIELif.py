import pyxrt as xrt  # type: ignore
import nengo.neurons

from ..AIEManager import AIEManager, AIEContext
from ..aie_kernels import LIFNeuronBuilder
from ..rc import DEFAULT_DEVICE, ITEMTYPE, ITEMSIZE
import numpy as np


class AIELif(nengo.neurons.LIF):
    """Wraps a nengo LIF neuron type. Refer to nengo documentation for properties, methods and parameters.
    """

    def __init__(self, size, dt, tau_rc=0.02, tau_ref=0.002, min_voltage=0, amplitude=1, initial_state=None):
        super().__init__(tau_rc=tau_rc, tau_ref=tau_ref,
                         amplitude=amplitude, initial_state=initial_state)

        # For size and dt parameters, we had two options:
        # a) we pass them as parameters in the constructor duplicating information (double source of truth)
        # b) we program the NPU during the first step
        # both options are viable and have their problems. The first option has been chosen at this moment.

        self.size = AIEManager.next_multiple_of(32)(size)
        self.dt = dt

        builder = LIFNeuronBuilder()
        (insts_path, xclbin_path) = builder.build(DEFAULT_DEVICE(1), self.size, tau_rc=self.tau_rc,
                                                  tau_ref=self.tau_ref, min_voltage=self.min_voltage, dt=dt, amplitude=self.amplitude)
        (device, kernel) = AIEManager.init_aie(xclbin_path)
        (instr_v, instr_bo) = AIEManager.load_insts(insts_path, device, kernel)

        self.context = AIEContext(device, kernel, instr_v, instr_bo)

        self.input_bo = self.context.create_inout_bo(
            "input", 3 * self.size, ITEMSIZE)
        self.output_bo = self.context.create_inout_bo(
            "output", 3 * self.size, ITEMSIZE)

    def step(self, dt, J, output, voltage, refractory_time):
        # As per comment in the constructor, we now have two places from which to read the "dt" value.
        # The one we use is the parameter.
        assert dt == self.dt

        self.input_bo.write(np.ones((3 * self.size, )).astype(ITEMTYPE).view(np.uint8), 0)

        copy = np.concatenate([J, voltage, refractory_time])
        
        for i, buff in enumerate([J, voltage, refractory_time]):
            self.input_bo.write(buff.astype(ITEMTYPE).view(
                np.uint8), self.size * i * ITEMSIZE)

        self.input_bo.sync(xrt.xclBOSyncDirection.XCL_BO_SYNC_BO_TO_DEVICE)

        self.context.kernel_call(self.input_bo, self.output_bo)  # type: ignore

        self.output_bo.sync(xrt.xclBOSyncDirection.XCL_BO_SYNC_BO_FROM_DEVICE)

        output_v = self.output_bo.read(self.size * ITEMSIZE * 3, 0).view(ITEMTYPE)

        try:
            output[...] = output_v[0:output.size]
            voltage[...] = output_v[self.size:self.size+voltage.size]
            refractory_time[...] = output_v[2*self.size:2*self.size+refractory_time.size]
        except:
            np.savetxt("in.txt", copy)
            np.savetxt("out.txt", output_v)
            raise

        # output[...] = self.output_bo.read(self.size * ITEMSIZE, 0).view(ITEMTYPE)[:output.size]
        # voltage[...] = self.output_bo.read(self.size * ITEMSIZE, self.size * ITEMSIZE).view(ITEMTYPE)[:voltage.size]
        # refractory_time[...] = self.output_bo.read(self.size * ITEMSIZE, 2 * self.size * ITEMSIZE).view(ITEMTYPE)[:refractory_time.size]
