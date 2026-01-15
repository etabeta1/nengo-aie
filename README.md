# nengo-aie

A [nengo](https://nengo.ai) backend to deploy spiking neural network on RyzenAI NPUs.

The aim of this project is to determine how big of a speedup it's possible to get from running nengo models on NPUs instead of on CPUs.

## Example usage

After installing this library, replace all the objects you want to deploy on NPU with the AIE-equivalent ones.

```python
import nengo
import nengo_aie

model = nengo.Network()

dt = 0.001

with model:
    # Instantiantes two ensembles and connects them
    A = nengo.Ensemble(100, dimensions=1)
    B = nengo.Ensemble(100, dimensions=1)
    conn = nengo.Connection(A, B)

    # The same but everything on the NPU
    npu_A = nengo.Ensemble(100, dimensions=1, neuron_type=AIELif(100, dt))
    npu_B = nengo.Ensemble(100, dimensions=1, neuron_type=AIELif(100, dt))
    npu_conn = nengo_aie.AIEConnection(npu_A, npu_B)

    # You can even put something on the NPU and something on the CPU
    A = nengo.Ensemble(100, dimensions=1)
    npu_B = nengo.Ensemble(100, dimensions=1, neuron_type=AIELif(100, dt))
    npu_conn = nengo_aie.AIEConnection(A, npu_B)

# Nengo default simulator - won't work with AIE stuff
with nengo.Simulator(model) as sim:
    sim.run(20)

# If you have AIE stuff, use the AIESimulator - this works even without AIE stuff but won't perform any of the optimization performed by the nengo default
with nengo_aie.AIESimulator(model, dt=dt) as sim:
    sim.run(20)
```

## Project structure

At the moment, this project is structured almost 1:1 to the original nengo library (except for the folder structure) and overrides only the minimun subset of the logic that is necessary to delegate computation on the NPU.

The [nengo documentation](https://www.nengo.ai/nengo/v4.0.0/examples/usage/rectified-linear.html) explains how to extend nengo adding new objects. [nengo/nengo-fpga] is also a good example of a nengo extension.

In particular, the `nengo.Simulator` class and the `nengo.builder.Builder` class are extended to force some specific options into the default simulator and to patch the default builder. All the components like neurons, ensembles, synaplses and whatever can be instantiated will receive an equivalent AIE implementation where possible and the same will happen with the operators.

The following tables describes the current status of the project.

### Operators

| Name               | Accelerable | Notes                                                                                                      |
| ------------------ | ----------- | ---------------------------------------------------------------------------------------------------------- |
| `TimeUpdate`       | No          |                                                                                                            |
| `Reset`            | No          |                                                                                                            |
| `Copy`             | Partially   |                                                                                                            |
| `ElementwiseInc`   | Done        | Accelerated but still slower that the CPU implementation.                                                  |
| `DotInc`           | Yes         |                                                                                                            |
| `SparseDotInc`     | Maybe       | Same as `DotInc` but with different input encoding. Maybe better to just accelerate and use `DotInc`.      |
| `BsrDotInc`        | Maybe       | Same as `DotInc` but with different input encoding. Maybe better to just accelerate and use `DotInc`.      |
| `SimPyFunc`        | No          | It is possible to replace the lambda parameter with a function that calls NPU kernels.                     |
| `SimProbe`         | No          |                                                                                                            |
| `SimProcess`       | No          | Identical to `SymPyFunc` except that some state is preserved between calls.                                |
| `GeneralConvInc`   | Yes         |                                                                                                            |
| `ConvInc`          | Yes         |                                                                                                            |
| `ConvTransposeInc` | Yes         |                                                                                                            |
| `SimPES`           | Yes         |                                                                                                            |
| `SimBCM`           | Yes         |                                                                                                            |
| `SimOJA`           | Yes         |                                                                                                            |
| `SimVoja`          | Yes         |                                                                                                            |
| `SimRLS`           | Yes         |                                                                                                            |
| `SimNeurons`       | No          | Calls the `step` method of a neuron type. That is the method that sould be accelerated, not this operator. |

### Neuron types

| Name                      | Accelerable | Notes                                                       |
| ------------------------- | ----------- | ----------------------------------------------------------- |
| `Direct`                  | No          | Should not be simulated                                     |
| `RectifiedLinear`         | Yes         |                                                             |
| `SpikingRectifiedLinear`  | Yes         |                                                             |
| `Sigmoid`                 | Yes         |                                                             |
| `Tanh`                    | Yes         |                                                             |
| `LIFRate`                 | Yes         |                                                             |
| `LIF`                     | Done        | Accelerated but faster than the CPU only for larger inputs. |
| `AdaptiveLIFRate`         | Yes         |                                                             |
| `AdaptiveLIF`             | Yes         |                                                             |
| `Izikevich`               | Yes         |                                                             |
| `RatesToSpikesNeuronType` | No          | Base class                                                  |
| `RegularSpiking`          | Yes         |                                                             |
| `StochasticSpiking`       | Yes         |                                                             |
| `PoissonSpiking`          | Yes         |                                                             |

## Contributing

### Adding new kernels

New kernels are created when there is something that can be sped up using the capabilities of the NPU.

1. Create a new folder inside `nengo_aie/aie_kernels` containing three files:
   - `__init__.py`: exports the `MlirBuilder` from the `<something>.py` file;
   - `<something>.cc`: contains all the c/c++ logic to link with the MLIR module;
   - `<something>.py`: contains the definition and the implementation of the `MlirBuilder` that is used to create and compile the MLIR module;
2. Add a new entry in `nengo_aie/OpNames.py`: the entry will be used to track and identify all the files related to the newly created kernel;
3. Register the `.cc` source in `nengo_aie/aie_kernels/__init__.py`.

As of now, every kernel must be composed of a single MLIR
module and a single `.cc` source with no exception. No linking with
other files is supported.
 
### Adding new builders

1. Create a new `nengo_aie/builders/<something>_builder.py` using the template;
2. Fill-in the template with all the parameters, signals and
operators instantiations, when in doubt, the default nengo
builder functions are a good starting point;
3. Export the file in the `__init__.py` so that the builder function
is registered.

```python
import nengo.builder
import numpy as np

# Useful so that when a new operator is implemented on the NPU we
# just need to change the import to use it in this builder
from nengo.builder.operator import Reset as AIEReset, DotInc as AIEDotInc

# A copy of the default nengo builder so that the original is still intact
from ..builder import AIEBuilder

from ..components import <AIE version of the component whose builder is to register> 
from ..operators import <AIE version of the operators to use>


@AIEBuilder.register(<AIE version of the component whose builder is to register>)
def build_aie_<component name>(model: nengo.builder.Model, <other parameters>):
    <param checks>
    
    <instantiation, initialization and sub-builds>

    <optional returns>
```

### Adding new components (except for neuron types)

Components are nothing more that a class used to store information about a part of the model to be simulated. Almost nothing but properties and the constructor are present in component definitions.

1. Create a new `nengo_aie/components/<component name>.py` containing a class definition and implementation. The class should be part of the nengo `NengoObject` inheritance tree (if in doubt, inheriting from the default nengo implementation should be a safe choice);
2. If inheriting from the default nengo implementation, the `__init__` parameters should match the `super()`'s one and call it; other initializations may be done here;
3. If inheriting from the default nengo implementation, all the `@property`-ies should be overridden to return the `super()`'s ones; other `@property`-ies may be defined as needed;

### Adding new neuron types

1. Create a new `nengo_aie/components/<neuron type>.py` with a class definition and implementation. Said class should be part of the Nengo `NeuronType` inheritance tree;
2. the `__init__.py` method should at least initialize `super` and upload the corresponding kernel to the NPU;
3. Override the `step` method to call the NPU kernel and save the results to the correct signals.

### Adding new operators

Operators are the objects that describe what operations are applied to signals. Signals are basically numpy arrays that describe the internal state of the model that is being simulated.

1. Create a new `nengo-aie/nengo_aie/operators/<operator name>.py` containing a class definition. The class should be part of the nengo `Operator` inheritance tree (if in doubt, inheriting from the default nengo implementation should be a safe choice);
2. If inheriting from the default nengo implementation, the `__init__` parameters should match the `super()`'s one and call it; other initializations may be done here;
3. If inheriting from the default nengo implementation, all the `@property`-ies should be overridden to return the `super()`'s ones; other `@property`-ies may be defined as needed;
4. Override `make_step`, a method that perform checks on the signals used/affected by the operator and returns a `step` function that effectively modify the signals;
5. Export the operator in `__init__.py`.

## Useful links

| Name                                            | Link                                                                                                         |
| ----------------------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| Nengo documentation                             | [nengo.ai](https://www.nengo.ai/nengo/)                                                                      |
| nengo/nengo repo                                | [GitHub](https://github.com/nengo/nengo)                                                                     |
| xilinx/mlir-aie repo                            | [GitHub](https://github.com/Xilinx/mlir-aie)                                                                 |
| AI Engine API User Guide                        | [UG1529](https://download.amd.com/docnav/aiengine/xilinx2025_1/aiengine_api/aie_api/doc/index.html)          |
| AIE-ML Architecture Manual                      | [AM020](https://docs.amd.com/r/en-US/am020-versal-aie-ml)                                                    |
| AIE Kernel Programming Guide                    | [UG1079](https://docs.amd.com/r/en-US/ug1079-ai-engine-kernel-coding)                                        |
| AIE-ML Intrinsics User Guide                    | [UG1583](https://download.amd.com/docnav/aiengine/xilinx2025_1/aiengine_ml_intrinsics/intrinsics/index.html) |
| XRT Architecture                                | [docs](https://xilinx.github.io/XRT/master/html/index.html)                                                  |
| AI Engine-ML Kernel and Graph Programming Guide | [UG1603](https://docs.amd.com/r/en-US/ug1603-ai-engine-ml-kernel-graph/)                                     |

