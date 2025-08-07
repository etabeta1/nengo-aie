import nengo


class AIEConnection(nengo.Connection):
    """Wraps a nengo connection. Refer to nengo documentation for properties, methods and parameters.
    """

    def __init__(self,
                 #  pre: nengo.Ensemble | nengo.ensemble.Neurons | nengo.Node,
                 #  post: nengo.Ensemble | nengo.ensemble.Neurons | nengo.Node | nengo.connection.LearningRule,
                 #  synapse: nengo.synapses.Synapse | nengo.params.DefaultType | None = nengo.Default,
                 #  function: collections.abc.Callable | numpy.ndarray | nengo.params.DefaultType = nengo.Default,
                 #  transform: numpy.ndarray | nengo.params.DefaultType = nengo.Default,
                 #  solver: nengo.solvers.Solver | nengo.params.DefaultType = nengo.Default,
                 #  learning_rule_type: nengo.learning_rules.LearningRuleType | collections.abc.Iterable[
                 #      nengo.learning_rules.LearningRuleType] | nengo.params.DefaultType = nengo.Default,
                 #  eval_points: numpy.ndarray | int | nengo.params.DefaultType = nengo.Default,
                 #  scale_eval_points: bool | nengo.params.DefaultType = nengo.Default,
                 #  label: str | nengo.params.DefaultType = nengo.Default,
                 #  seed: str | nengo.params.DefaultType = nengo.Default,
                 *args, **kwargs
                 ):
        super().__init__(*args, **kwargs)

    @property
    def function(self):
        return super().function

    @function.setter
    def function(self, function):
        super().function = function

    @property
    def has_weights(self):
        return super().has_weights

    @property
    def is_decoded(self):
        return super().is_decoded

    @property
    def _to_neurons(self):
        return super()._to_neurons

    @property
    def learning_rule(self):
        return super().learning_rule

    @property
    def post_obj(self):
        return super().post_obj

    @property
    def post_slice(self):
        return super().post_slice

    @property
    def pre_obj(self):
        return super().pre_obj

    @property
    def pre_slice(self):
        return super().pre_slice

    @property
    def size_in(self):
        return super().size_in

    @property
    def size_mid(self):
        return super().size_mid

    @property
    def size_out(self):
        return super().size_out
