import pyxrt as xrt  # type: ignore
import nengo.builder

from ..AIEManager import AIEManager, AIEContext
from ..aie_kernels import ElementwiseIncBuilder
from ..rc import DEFAULT_DEVICE, ITEMTYPE

import logging
logger = logging.getLogger(__name__)


class AIEElementwiseInc(nengo.builder.operator.ElementwiseInc):
    def __init__(self, A: nengo.builder.Signal, X: nengo.builder.Signal, Y: nengo.builder.Signal, tag=None):
        super().__init__(A, X, Y, tag=tag)

        self.size = AIEManager.next_multiple_of(16)(Y.size)

        builder = ElementwiseIncBuilder()
        (insts_path, xclbin_path) = builder.build(DEFAULT_DEVICE, self.size)
        (device, kernel) = AIEManager.init_aie(xclbin_path)
        (instr_v, instr_bo) = AIEManager.load_insts(insts_path, device, kernel)

        self.context = AIEContext(device, kernel, instr_v, instr_bo)

        self.input_bo = self.context.create_inout_bo(
            "input", 3 * self.size, ITEMTYPE().itemsize)
        self.output_bo = self.context.create_inout_bo(
            "output", self.size, ITEMTYPE().itemsize)

    @property
    def A(self):
        return super().A

    @property
    def X(self):
        return super().X

    @property
    def Y(self):
        return super().Y

    @property
    def _descstr(self):
        return f"{self.A}, {self.X} -> {self.Y}"

    def make_step(self, signals, dt, rng):
        # We do signal size checks with the super() method without actually using the returning callable

        try:
            super().make_step(signals=signals, dt=dt, rng=rng)
        except nengo.exceptions.BuildError as e:
            logger.error(
                "Error while making \'AIEElementWise\' step. Nested Exception is " + str(e))
            raise nengo.exceptions.BuildError("AIEElementwiseInc: " + str(e))

        def step():
            for i, buff in enumerate([self.A, self.X, self.Y]):
                self.input_bo.write(signals[buff].astype(
                    ITEMTYPE), self.size * i * ITEMTYPE().itemsize)
                self.output_bo.sync(xrt.xclBOSyncDirection.XCL_BO_SYNC_BO_TO_DEVICE)

            self.context.kernel_call(self.input_bo, self.output_bo)  # type: ignore

            self.output_bo.sync(xrt.xclBOSyncDirection.XCL_BO_SYNC_BO_FROM_DEVICE)

            signals[self.Y][...] = self.output_bo.read(
                self.size * ITEMTYPE().itemsize, 0).view(ITEMTYPE)[:signals[self.Y].size]

        return step
