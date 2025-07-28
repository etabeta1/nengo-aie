from aie.iron.device import NPU1Col1  # type: ignore
# from aie.dialects.aie import *
import nengo
import numpy as np

DEFAULT_DEVICE = NPU1Col1()
# DEFAULT_DEVICE = AIEDevice.npu1_1col
# ITEMTYPE = nengo.rc.float_dtype
ITEMTYPE = np.float32
