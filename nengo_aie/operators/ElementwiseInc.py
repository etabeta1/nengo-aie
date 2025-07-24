import pyxrt as xrt  # type: ignore
import nengo.builder

from .. import AIEManager, AIEContext
from ..aie_kernels import ElementwiseIncBuilder
from .. import rc

import logging
logger = logging.getLogger(__name__)


class AIEElementwiseInc(nengo.builder.operator.ElementwiseInc):
    context = None
    MAX_SIZE = 8192

    def __init__(self, A: nengo.builder.Signal, X: nengo.builder.Signal, Y: nengo.builder.Signal, tag=None):
        super().__init__(A, X, Y, tag=tag)

        if AIEElementwiseInc.context is None:
            builder = ElementwiseIncBuilder()
            (insts_path, xclbin_path) = builder.build(
                rc.DEFAULT_DEVICE, AIEElementwiseInc.MAX_SIZE)
            (device, kernel) = AIEManager.init_aie(xclbin_path)
            (instr_v, instr_bo) = AIEManager.load_insts(insts_path, device, kernel)

            AIEElementwiseInc.context = AIEContext(device, kernel, instr_v, instr_bo)

            input_bo = AIEElementwiseInc.context.create_inout_bo(
                "input", 3 * AIEElementwiseInc.MAX_SIZE)
            output_bo = AIEElementwiseInc.context.create_inout_bo(
                "output", AIEElementwiseInc.MAX_SIZE)

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

            # TODO: sistemare con tensor access pattern
            # TODO: capire l'unità di misura degli offset

            for i, buff in enumerate([self.A, self.X, self.Y]):
                in_bo = AIEElementwiseInc.context.get_bo("input")  # type: ignore
                in_bo.write(signals[buff], AIEElementwiseInc.MAX_SIZE * i * 2)
                in_bo.sync(xrt.xclBOSyncDirection.XCL_BO_SYNC_BO_TO_DEVICE)

            out_bo = AIEElementwiseInc.context.get_bo("output")  # type: ignore

            AIEElementwiseInc.context.kernel_call(in_bo, out_bo)  # type: ignore

            out_bo.sync(xrt.xclBOSyncDirection.XCL_BO_SYNC_BO_FROM_DEVICE)

            signals[self.Y][...] = out_bo.read(AIEElementwiseInc.MAX_SIZE, 0)[
                :signals[self.Y].size]

        return step
