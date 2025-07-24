
from OpNames import *
from MlirBuilder import MlirBuilder as MlirBuilderBase
from ElementwiseInc import ElementwiseIncBuilder

from KernelManager import KernelManager

KernelManager.register_kernel_source(
    OpNames.ELEMENTWISE_INC, "ElementwiseInc", "kernel.cc")

KernelManager.compile_all()
