import nengo
import nengo.builder
import nengo.cache
import atexit
from .builder import AIEBuilder

import logging
logger = logging.getLogger(__name__)


class AIESimulator(nengo.Simulator):
    def __init__(self, network, dt=0.001, seed=None, progress_bar=True, recompile_kernels=True):
        logger.info("Initializing simulator")
        super().__init__(
            network,
            dt=dt,
            seed=seed,
            model=nengo.builder.Model(
                dt=float(dt),
                label=f"{network}, dt={dt:f}",
                decoder_cache=nengo.cache.get_default_decoder_cache(),
                builder=AIEBuilder(),
            ),
            progress_bar=progress_bar,
            optimize=False,  # We do not optimize otherwise the optimizer would optimize out the AIE operators
                             # TODO: We now have two choices:
                             # - we create a custom optimizer that merges operators into AIE operators giving the user less control on which operators are run on the NPU
                             # - we do not do anything and prevent any optimization
        )
