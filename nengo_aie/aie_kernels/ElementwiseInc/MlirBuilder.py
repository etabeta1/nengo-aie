from .. import MlirBuilderBase

class MlirBuilder(MlirBuilderBase.MlirBuilder):
    def __init__(self):
        MlirBuilderBase.MlirBuilder.__init__(self, "ElementwiseInc.mlir")

    def build(self):
        pass