import nengo
from ..builder import AIEBuilder

import numpy as np
from nengo.builder.ensemble import gen_eval_points, get_activities
from nengo.builder.node import SimPyFunc
from nengo.builder.operator import Copy, ElementwiseInc, Reset
from nengo.builder.signal import Signal
from nengo.connection import Connection
from nengo.ensemble import Ensemble, Neurons
from nengo.exceptions import BuildError
from nengo.neurons import Direct
from nengo.node import Node
from nengo.rc import rc
from nengo.solvers import NoSolver, Solver
from nengo.transforms import Dense, NoTransform
from nengo.utils.numpy import is_integer, is_iterable

@AIEBuilder.register(nengo.connection.Connection)
def build_connection(model, conn):
    rng = np.random.RandomState(model.seeds[conn])
    
    def get_prepost_signal(is_pre):
        target = conn.pre_obj if is_pre else conn.post_obj
        key = "out" if is_pre else "in"

        if target not in model.sig:
            raise BuildError(
                f"Building {conn}: the '{'pre' if is_pre else 'post'}' object {target} "
                "is not in the model, or has a size of zero."
            )
        signal = model.sig[target].get(key, None)
        if signal is None or signal.size == 0:
            raise BuildError(
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

    # Figure out the signal going across this connection
    in_signal = model.sig[conn]["in"]
    if isinstance(conn.pre_obj, Node) or (
        isinstance(conn.pre_obj, Ensemble)
        and isinstance(conn.pre_obj.neuron_type, Direct)
    ):
        # Node or Decoded connection in directmode
        sliced_in = nengo.builder.connection.slice_signal(model, in_signal, conn.pre_slice)
        if conn.function is None:
            in_signal = sliced_in
        elif isinstance(conn.function, np.ndarray):
            raise BuildError("Cannot use function points in direct connection")
        else:
            in_signal = Signal(shape=conn.size_mid, name=f"{conn}.func")
            model.add_op(SimPyFunc(in_signal, conn.function, None, sliced_in))
    elif isinstance(conn.pre_obj, Ensemble):  # Normal decoded connection
        eval_points, decoders, solver_info = model.build(conn.solver, conn, rng)
        if isinstance(conn.post_obj, Ensemble) and conn.solver.weights:
            model.sig[conn]["out"] = model.sig[conn.post_obj.neurons]["in"]

            encoders = model.params[conn.post_obj].scaled_encoders.T
            encoders = encoders[conn.post_slice]

            # post slice already applied to encoders (either here or in
            # `build_decoders`), so don't apply later
            post_slice = None
    else:
        in_signal = nengo.builder.connection.slice_signal(model, in_signal, conn.pre_slice)

    # Build transform
    if conn.solver.weights and not conn.solver.compositional:
        # special case for non-compositional weight solvers, where
        # the solver is solving for the full weight matrix. so we don't
        # need to combine decoders/transform/encoders.
        weighted, weights = model.build(
            Dense(decoders.shape, init=decoders), in_signal, rng=rng
        )
    else:
        weighted, weights = model.build(
            conn.transform, in_signal, decoders=decoders, encoders=encoders, rng=rng
        )

    model.sig[conn]["weights"] = weights

    # Build synapse
    if conn.synapse is not None:
        weighted = model.build(conn.synapse, weighted, mode="update")

    # Store the weighted-filtered output in case we want to probe it
    model.sig[conn]["weighted"] = weighted

    if isinstance(conn.post_obj, Neurons):
        # Apply neuron gains (we don't need to do this if we're connecting to
        # an Ensemble, because the gains are rolled into the encoders)
        gains = Signal(
            model.params[conn.post_obj.ensemble].gain[post_slice],
            name=f"{conn}.gains",
        )

        if is_integer(post_slice) or isinstance(post_slice, slice):
            sliced_out = model.sig[conn]["out"][post_slice]
        else:
            # advanced indexing not supported on Signals, so we need to set up an
            # intermediate signal and use a Copy op to perform the indexing
            sliced_out = Signal(shape=gains.shape, name=f"{conn}.sliced_out")
            model.add_op(Reset(sliced_out))
            model.add_op(
                Copy(sliced_out, model.sig[conn]["out"], dst_slice=post_slice, inc=True)
            )

        model.add_op(
            ElementwiseInc(
                gains, weighted, sliced_out, tag=f"{conn}.gains_elementwiseinc"
            )
        )
    else:
        # Copy to the proper slice
        model.add_op(
            Copy(
                weighted,
                model.sig[conn]["out"],
                dst_slice=post_slice,
                inc=True,
                tag=f"{conn}",
            )
        )

    # Build learning rules
    if conn.learning_rule is not None:
        # TODO: provide a general way for transforms to expose learnable params
        if not isinstance(conn.transform, (Dense, NoTransform)):
            raise NotImplementedError(
                f"Learning on connections with {type(conn.transform).__name__} "
                "transforms is not supported"
            )

        rule = conn.learning_rule
        rule = [rule] if not is_iterable(rule) else rule
        targets = []
        for r in rule.values() if isinstance(rule, dict) else rule:
            model.build(r)
            targets.append(r.modifies)

        if "encoders" in targets:
            encoder_sig = model.sig[conn.post_obj]["encoders"]
            encoder_sig.readonly = False
        if "decoders" in targets or "weights" in targets:
            if weights.ndim < 2:
                raise BuildError(
                    "'transform' must be a 2-dimensional array for learning"
                )
            model.sig[conn]["weights"].readonly = False

    model.params[conn] = nengo.builder.connection.BuiltConnection(
        eval_points=eval_points,
        solver_info=solver_info,
        transform=conn.transform,
        weights=getattr(weights, "initial_value", None),
    )