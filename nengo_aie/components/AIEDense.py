import nengo


class AIEDense(nengo.Dense):
    """Wraps a nengo dense. Refer to nengo documentation for properties, methods and parameters.
    """

    def __init__(self, shape: tuple, init: float = 1):
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
