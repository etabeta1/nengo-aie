import nengo.builder

from nengo.builder.operator import Reset as AIEReset, DotInc as AIEDotInc

from ..builder import AIEBuilder
from ..components import AIEDense
from ..operators import AIEElementwiseInc

import numpy as np


@AIEBuilder.register(AIEDense)
def build_aie_dense(model: nengo.builder.Model, dense, sig_in: nengo.builder.Signal, decoders: np.ndarray | None = None, encoders: np.ndarray | None = None, rng=np.random):
    weights = dense.sample(rng=rng).astype(nengo.rc.float_dtype)

    if decoders is not None:
        weights = nengo.builder.transforms.multiply(
            weights, decoders.astype(nengo.rc.float_dtype))
    if encoders is not None:
        weights = nengo.builder.transforms.multiply(
            encoders.astype(nengo.rc.float_dtype).T, weights)

    weight_sig = nengo.builder.Signal(weights, readonly=True, name=f"{dense}.weights")
    weighted = nengo.builder.Signal(
        shape=dense.size_out if encoders is None else weights.shape[0], name=f"{dense}.weighted")

    model.add_op(AIEReset(weighted))

    op = AIEElementwiseInc if weights.ndim < 2 else AIEDotInc
    model.add_op(op(weight_sig, sig_in, weighted, tag=f"{dense}.apply_weights"))

    return weighted, weight_sig
