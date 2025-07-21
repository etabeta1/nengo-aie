import nengo
import atexit
from .builder import AIEBuilder

import logging
logger = logging.getLogger(__name__)

class AIESimulator(nengo.simulator.Simulator):
    def __init__(self, network, dt=0.001, seed=None, progress_bar=True, optimize=True):
        logger.info("Initializing simulator")
        super().__init__(
            network,
            dt = dt,
            seed = seed,
            model = nengo.builder.Model(
                dt = float(dt),
                label = f"{network}, dt={dt:f}",
                decoder_cache=nengo.cache.get_default_decoder_cache(),
                builder = AIEBuilder(),
            ),
            progress_bar = progress_bar,
            optimize = optimize,
        )