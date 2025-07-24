import nengo.builder

from .. import AIEManager

import logging
logger = logging.getLogger(__name__)


class AIEElementwiseInc(nengo.builder.operator.ElementwiseInc):
    def __init__(self, A, X, Y, tag=None):
        super().__init__(A, X, Y, tag=tag)

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
            pass

        return step
