import numpy as np
import nengo
import sys

import logging
# logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, format="[%(name)s/%(levelname)s]: %(message)s")
logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="[%(name)s/%(levelname)s]: %(message)s")

import nengo_aie

model = nengo.Network()

dt = 1e-3

with model:
    A = nengo.Ensemble(100, dimensions=1, neuron_type=nengo_aie.AIELif(100, dt))
    A_squared = nengo.Ensemble(100, dimensions=1)
    error = nengo.Ensemble(100, dimensions=1)

    conn = nengo.Connection(A, A_squared)

    conn.learning_rule_type = nengo.PES(learning_rate=3e-4)

    nengo.Connection(error, conn.learning_rule)

    nengo.Connection(A_squared, error)

    nengo.Connection(A, error, function=lambda x: x**2, transform=-1)

with model:
    input_node = nengo.Node(output=lambda t: int(6 * t / 5) / 3.0 % 2 - 1)

    nengo_aie.AIEConnection(input_node, A)

    stop_learning = nengo.Node(output=lambda t: t >= 15)

    nengo.Connection(stop_learning, error.neurons, transform = -20 * np.ones((error.n_neurons, 1))) # This one is the one that calls elementwise inc
    # nengo_aie.AIEConnection(stop_learning, error.neurons, transform = -20 * np.ones((error.n_neurons, 1)))

with model:
    input_node_probe = nengo.Probe(input_node)
    A_probe = nengo.Probe(A, synapse=0.01)
    A_squared_probe = nengo.Probe(A_squared, synapse=0.01)
    error_probe = nengo.Probe(error, synapse=0.01)
    learn_probe = nengo.Probe(stop_learning, synapse=None)

with nengo_aie.AIESimulator(model, dt=dt) as sim:
    sim.run(20)


