from enum import Enum

from aie_kernels import ElementwiseInc


class OpNames(Enum):
    ELEMENTWISE_INC = ElementwiseInc.__name__
