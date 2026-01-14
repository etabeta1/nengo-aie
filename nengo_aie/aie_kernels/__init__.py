from ..OpNames import *
from .MlirBuilder import MlirBuilder as MlirBuilderBase

from .ElementwiseInc import ElementwiseIncBuilder
from .LIFNeuron import LIFNeuronBuilder

from .KernelManager import KernelManager

KernelManager.register_inc_folder("aie_math")

KernelManager.register_kernel_source(
    OpNames.ELEMENTWISE_INC, "ElementwiseInc", "kernel.cc")
KernelManager.register_kernel_source(
    OpNames.LIF_NEURON, "LIFNeuron", "kernel.cc")

KernelManager.compile_all()
