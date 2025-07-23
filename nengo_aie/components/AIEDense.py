import nengo


class AIEDense(nengo.Dense):
    def __init__(self, shape, init=1):
        super().__init__(shape, init)

    @property
    def _argreprs(self):
        return super()._argreprs

    @property
    def init_shape(self):
        return super().init_shape

    @property
    def size_in(self):
        return super().size_in

    @property
    def size_out(self):
        return super().size_out
