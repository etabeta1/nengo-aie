import nengo
import nengo.builder
import nengo.cache
from nengo.utils.progress import ProgressBar
import atexit
from .builder import AIEBuilder

import logging
logger = logging.getLogger(__name__)


class AIESimulator(nengo.Simulator):
    """Clone of the default nengo simulator that forces some parameters.

    Refer to nengo documentation for information about methods and parameters.
    """

    def __init__(self, network: nengo.Network, dt: float | None = 0.001, seed: int | None = None, progress_bar: bool | ProgressBar | None = True):
        logger.info("Initializing simulator")
        super().__init__(
            network,
            dt=dt,  # type: ignore
            seed=seed,
            model=nengo.builder.Model(
                dt=float(dt),  # type: ignore
                label=f"{network}, dt={dt:f}",
                decoder_cache=nengo.cache.get_default_decoder_cache(),
                builder=AIEBuilder(),
            ),
            progress_bar=progress_bar,  # type: ignore
            optimize=False,  # We do not optimize otherwise the optimizer would optimize out the AIE operators
                             # TODO: We now have three choices:
                             # - we create a custom optimizer that merges operators into AIE operators giving the user less control on which operators are run on the NPU
                             # - we do not do anything and prevent any optimization
                             # - we implement our custom AIEOptimizer
        )
