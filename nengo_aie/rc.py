from aie.iron.device import NPU1Col1, NPU1Col2, NPU1Col3  # type: ignore
# from aie.dialects.aie import *
import nengo
import numpy as np
import ml_dtypes

#DEFAULT_DEVICE = NPU1Col1()
DEFAULT_DEVICE = lambda cols: [NPU1Col1, NPU1Col2, NPU1Col3][cols-1]()
# DEFAULT_DEVICE = AIEDevice.npu1_1col
# ITEMTYPE = nengo.rc.float_dtype
# ITEMTYPE = np.float32
ITEMTYPE = ml_dtypes.bfloat16
ITEMSIZE = 2
