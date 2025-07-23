import nengo

import nengo.builder
import nengo.ensemble
import nengo.transforms
import numpy as np

from nengo.builder.node import SimPyFunc as AIESimPyFunc
from nengo.builder.operator import Copy as AIECopy, Reset as AIEReset

from ..builder import AIEBuilder
from ..components import AIEConnection, AIEDense
from ..operators import AIEElementwiseInc


@AIEBuilder.register(AIEConnection)
def build_aie_connection(model: nengo.builder.Model, conn: AIEConnection):
    rng = np.random.RandomState(model.seeds[conn])

    def get_prepost_signal(is_pre: bool) -> nengo.builder.Signal:
        target = conn.pre_obj if is_pre else conn.post_obj
        key = "out" if is_pre else "in"

        if target not in model.sig:
            raise nengo.exceptions.BuildError(
                f"Building {conn}: the '{'pre' if is_pre else 'post'}' object {target} "
                "is not in the model, or has a size of zero."
            )
        signal = model.sig[target].get(key, None)
        if signal is None or signal.size == 0:
            raise nengo.exceptions.BuildError(
                f"Building {conn}: the '{'pre' if is_pre else 'post'}' object {target} "
                f"has a '{key}' size of zero."
            )

        return signal

    model.sig[conn]["in"] = get_prepost_signal(is_pre=True)
    model.sig[conn]["out"] = get_prepost_signal(is_pre=False)

    decoders = None
    encoders = None
    eval_points = None
    solver_info = None
    post_slice = conn.post_slice

    in_signal = model.sig[conn]["in"]

    if isinstance(conn.pre_obj, nengo.Node) or (isinstance(conn.pre_obj, nengo.Ensemble) and isinstance(conn.pre_obj.neuron_type, nengo.Direct)):
        sliced_in = nengo.builder.connection.slice_signal(
            model, in_signal, conn.pre_slice)
        if conn.function is None:
            in_signal = sliced_in
        elif isinstance(conn.function, np.ndarray):
            raise nengo.exceptions.BuildError(
                "Cannot use function points in direct connection")
        else:
            in_signal = nengo.builder.Signal(shape=conn.size_mid, name=f"{conn}.func")
            model.add_op(AIESimPyFunc(in_signal, conn.function, None, sliced_in))
    elif isinstance(conn.pre_obj, nengo.Ensemble):
        eval_points, decoders, solver_info = model.build(
            conn.solver, conn, rng) or (None, None, None)
        if isinstance(conn.post_obj, nengo.Ensemble) and conn.solver.weights:  # type: ignore
            model.sig[conn]["out"] = model.sig[conn.post_obj.neurons]["in"]
            encoders = model.params[conn.post_obj].scaled_encoders.T
            encoders = encoders[conn.post_slice]

            post_slice = None
    else:
        in_signal = nengo.builder.connection.slice_signal(
            model, in_signal, conn.pre_slice)

    if conn.solver.weights and not conn.solver.compositional:  # type: ignore
        weighted, weights = model.build(
            AIEDense(decoders.shape, init=decoders), in_signal, rng=rng) or (None, None)  # type: ignore
    else:
        weighted, weights = model.build(
            conn.transform, in_signal, decoders=decoders, encoders=encoders, rng=rng) or (None, None)

    model.sig[conn]["weights"] = weights

    if conn.synapse is not None:
        weighted = model.build(conn.synapse, weighted, mode="update")

    model.sig[conn]["weighted"] = weighted

    if isinstance(conn.post_obj, nengo.ensemble.Neurons):
        gains = nengo.builder.Signal(
            model.params[conn.post_obj.ensemble].gain[post_slice], name=f"{conn}.gains")

        if nengo.utils.numpy.is_integer(post_slice) or isinstance(post_slice, slice):
            sliced_out = model.sig[conn]["out"][post_slice]
        else:
            sliced_out = nengo.builder.Signal(
                shape=gains.shape, name=f"{conn}.sliced_out")
            model.add_op(AIEReset(sliced_out))
            model.add_op(
                AIECopy(sliced_out, model.sig[conn]["out"], dst_slice=post_slice, inc=True))

        model.add_op(AIEElementwiseInc(gains, weighted, sliced_out,
                     tag=f"{conn}.gains_elementwiseinc"))
    else:
        model.add_op(
            AIECopy(weighted, model.sig[conn]["out"], dst_slice=post_slice, inc=True, tag=f"{conn}"))

    if conn.learning_rule is not None:
        if not isinstance(conn.transform, (nengo.Dense, nengo.transforms.NoTransform)):
            raise NotImplementedError(
                f"Learning on connections with {type(conn.transform).__name__} "
                "transforms is not supported"
            )

        rule = conn.learning_rule
        rule = [rule] if not nengo.utils.numpy.is_iterable(rule) else rule
        targets = []

        for r in rule.values() if isinstance(rule, dict) else rule:
            model.build(r)
            targets.append(r.modifies)  # type: ignore

        if "encoders" in targets:
            encoder_sig = model.sig[conn.post_obj]["encoders"]
            encoder_sig.readonly = False

        if "decoders" in targets or "weights" in targets:
            if weights.ndim < 2:  # type: ignore
                raise nengo.exceptions.BuildError(
                    "'transform' must be a 2-dimensional array for learning"
                )
            model.sig[conn]["weights"].readonly = False

        model.params[conn] = nengo.builder.connection.BuiltConnection(eval_points=eval_points, solver_info=solver_info,
                                                                      transform=conn.transform, weights=getattr(weights, "initial_value", None))
