from aie.iron.device import NPU1Col1  # type: ignore
import nengo
import numpy as np

DEFAULT_DEVICE = NPU1Col1()
# ITEMTYPE = nengo.rc.float_dtype
ITEMTYPE = np.float32
