from .MlirBuilder import MlirBuilder as MlirBuilderBase
from .ElementwiseInc import ElementwiseIncBuilder

from .Managers import KernelManager, MlirManager

KernelManager.register_kernel_source(ElementwiseInc.__name__, "ElementwiseInc", "kernel.cc")
KernelManager.compile_all()