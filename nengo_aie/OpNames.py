from enum import Enum


class OpNames(Enum):
    """Enumeration used to identify and track all the files and compilation artifacts for each kernel.
    """
    ELEMENTWISE_INC = "aie_kernels.ElementwiseInc"
    LIF_NEURON = "aie_kernels.LIFNeuron"
