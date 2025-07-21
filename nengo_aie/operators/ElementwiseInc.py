from nengo.builder.operator.ElementwiseInc

class AIEElementwiseInc(nengo.builder.operator.ElementwiseInc):
    def __init__(self, A, X, Y, tag=None):
        super().__init__(A, X, Y, tag=tag)

    @property
    def A(self):
        return self.reads[0]

    @property
    def X(self):
        return self.reads[1]

    @property
    def Y(self):
        return self.incs[0]

    def make_step(self):
        # TODO: check signal size, create callable to call kernel, return callable
        raise NotImplementedError

        
    