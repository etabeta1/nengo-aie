from enum import Enum

from .MlirBuilder import MlirBuilder as MlirBuilderBase
from .ElementwiseInc import ElementwiseIncBuilder

from .KernelManager import KernelManager

class OpNames(Enum):
    ELEMENTWISE_INC = ElementwiseInc.__name__

KernelManager.register_kernel_source(OpNames.ELEMENTWISE_INC, "ElementwiseInc", "kernel.cc")
KernelManager.compile_all()