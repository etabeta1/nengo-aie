# nengo-aie

A [nengo](https://nengo.ai) backend to deploy spiking neural network on RyzenAI NPUs.

The aim of this project is to determine how big of a speedup it's possible to get from running nengo models on NPUs instead of on CPUs.

## Example usage

After installing this library, replace all the objects you want to deploy on NPU with the AIE-equivalent ones.

```python
import nengo
import nengo_aie

model = nengo.Network()

with model:
    # Instantiantes two ensembles and connects them
    A = nengo.Ensemble(100, dimensions=1)
    B = nengo.Ensemble(100, dimensions=1)
    conn = nengo.Connection(A, B)

    # The same but everything on the NPU
    npu_A = nengo_aie.AIEEnsemble(100, dimensions=1)
    npu_B = nengo_aie.AIEEnsemble(100, dimensions=1)
    npu_conn = nengo_aie.AIEConnection(npu_A, npu_B)

    # You can even put something on the NPU and something on the CPU
    A = nengo.Ensemble(100, dimensions=1)
    npu_B = nengo_aie.AIEEnsemble(100, dimensions=1)
    npu_conn = nengo_aie.AIEConnection(A, npu_B)

# Nengo default simulator - won't work with AIE stuff
with nengo.Simulato(model) as sim:
    sim.run(20)

# If you have AIE stuff, use the AIESimulator - this works even without AIE stuff but won't perform any of the optimization performed by the nengo default
with nengo_aie.AIESimulator(model) as sim:
    sim.run(20)
```

## Project structure

At the moment, this project is structured almost 1:1 to the original nengo library (except for the folder structure) and overrides only the minimun subset of the logic that is necessary to delegate computation on the NPU.

The [nengo documentation](https://www.nengo.ai/nengo/v4.0.0/examples/usage/rectified-linear.html) explains how to extend nengo adding new objects. [nengo/nengo-fpga] is also a good example of a nengo extension.

In particular, the `nengo.Simulator` class and the `nengo.builder.Builder` class are extended to force some specific options into the default simulator and to patch the default builder. All the components like neurons, ensembles, synaplses and whatever can be instantiated will receive an equivalent AIE implementation where possible and the same will happen with the operators.

The following tables describes the current status of the project.

### Components

TODO

### Operators

| Name | Status | Notes |
| ---- | ------ | ----- |

TODO

## Contributing

### Adding new kernels

New kernels are created when there is something that can be sped up using the capabilities of the NPU.

1.  Create a new folder inside `nengo-aie/nengo_aie/aie_kernels` containing the following three files:
    - `__init__.py`: exports the MlirBuilder from the `<something>.py` file;
    - `<something>.cc`: contains all the c++ logic to link with;
    - `<something>.py`: contains the definition of the MlirBuilder used to compile the kernel.
2.  Add a new `OpName` in `nengo-aie/nengo_aie/OpNames.py` to uniquely identify all the files related to the kernel.
3.  Register the `.cc` source in `nengo-aie/nengo_aie/aie_kernels/__init__.py`.
 
### Adding new builders

Builders are functions used by the nengo builder to instantiate components/nodes. To use the new operators/kernels, a new builder must be created and registered.

1.  Create a new `nengo-aie/nengo_aie/builders/<something>_builder.py` using the template at the bottom of this subsection;
2.  Fill-in the template with all the parameters, signal instantiation and operator instantiation;
3.  Export the builder in `__init__.py`. This is needed so that when the library is imported, all the builders are registered.

The builder template is as follows:
```python
import nengo.builder

from nengo.builder.operator import Reset as AIEReset, DotInc as AIEDotInc  # Useful so that when a new operator is implemented on the NPU we just need to change the import to use it in this builder

from ..builder import AIEBuilder  # A copy of the default nengo builder so that the original is still intact
from ..components import <AIE version of the component whose builder is to register> 
from ..operators import <AIE version of the operators to use>

import numpy as np


@AIEBuilder.register(<AIE version of the component whose builder is to register>)
def build_aie_<component name>(model: nengo.builder.Model, <other parameters>):
    <param checks>
    
    <instantiation, initialization and sub-builds>

    <optional returns>
```

### Adding new components

Components are nothing more that a class used to store information about a part of the model to be simulated. Almost nothing but properties and the constructor are present in component definitions (except for neurons that also contains a `step` method).

1. Create a new `nengo-aie/nengo_aie/components/<component name>.py` containing a class definition. The class should be part of the nengo `NengoObject` inheritance tree (if in doubt, inheriting from the default nengo implementation should be a safe choice);
2.  If inheriting from the default nengo implementation, the `__init__` parameters should match the `super()`'s one and call it; other initializations may be done here;
3.  If inheriting from the default nengo implementation, all the `@property`-ies should be overridden to return the `super()`'s ones; other `@property`-ies may be defined as needed;

### Adding new operators

Operators are the objects that describe what operations are applied to signals. Signals are basically numpy arrays that describe the internal state of the model that is being simulated.

1.  Create a new `nengo-aie/nengo_aie/operators/<operator name>.py` containing a class definition. The class should be part of the nengo `Operator` inheritance tree (if in doubt, inheriting from the default nengo implementation should be a safe choice);
2.  If inheriting from the default nengo implementation, the `__init__` parameters should match the `super()`'s one and call it; other initializations may be done here;
3.  If inheriting from the default nengo implementation, all the `@property`-ies should be overridden to return the `super()`'s ones; other `@property`-ies may be defined as needed;
4.  Override `make_step`, a method that perform checks on the signals used/affected by the operator and returns a `step` function that effectively modify the signals;
5.  Export the operator in `__init__.py`.

## Benchmarks

TODO

## Useful links

| Name                         | Link                                                                                                |
| ---------------------------- | --------------------------------------------------------------------------------------------------- |
| Nengo documentation          | [nengo.ai](https://www.nengo.ai/nengo/)                                                             |
| nengo/nengo repo             | [GitHub](https://github.com/nengo/nengo)                                                            |
| xilinx/mlir-aie repo         | [GitHub](https://github.com/Xilinx/mlir-aie)                                                        |
| AI Engine API User Guide     | [UG1529](https://download.amd.com/docnav/aiengine/xilinx2025_1/aiengine_api/aie_api/doc/index.html) |
| AIE-ML Architecture Manual   | [AM020](https://docs.amd.com/r/en-US/am020-versal-aie-ml)                                           |
| AIE Kernel Programming Guide | [UG1079](https://docs.amd.com/r/en-US/ug1079-ai-engine-kernel-coding)                               |
