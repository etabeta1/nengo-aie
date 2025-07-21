import nengo
import atexit

#class AIESimulator(nengo.simulator.Simulator):
class AIESimulator:
    def __init__(self, network, dt=0.001, seed=None, model=None, progress_bar=True, optimize=True):
        self.closed = True
        self.progress_bar = progress_bar
        self.optimize = optimize
        
        self.dt = dt
        self.n_steps = 0

        if model is None:
            self.model = Model(
                dt = float(dt),
                label = "%s, dt= %f" % (network, dt),
                decoder_cache = get_default_decoder_cache(),
                builder = AIEBuilder()
            )
        else:
            self.model = model

        pt = ProgressTracker(progress_bar, Progress("Building", "Build"))

        with pt:
            if network is not None:
                self.model.build(network, progress=pt.next_stage("Building", "Build"))
            self.dg = operator_dependency_graph(self.model.operators)

            if optimize:
                with pt.next_stage("Building (running optimizer)", "Optimization"):
                    opmerge_optimize(self.model, self.dg)

        self._step_order = [op for op in toposort(self.dg) if hasattr(op, "make_step")]

        self.signals = SignalDict()
        for op in self.model.operators:
            op.init_signals(self.signals)

        self._sim_data = self.model.params

        self.data = SimulationData(self._sim_data)

        if seed is None:
            if network is not None and network.seed is not None:
                seed = network.seed + 1
            else:
                seed = np.random.randint(npext.maxint)

        self.closed = False
        self.reset(seed=seed)
        
        
    def run(self, time_in_seconds):
        steps = int(np.round(float(time_in_seconds) / self.dt))
        self.run_steps(steps)
        
    
    def run_steps(self, steps):
        for i in range(steps):
            self.step()
            
    
    def reset(self, seed=None):
        if self.closed:
            raise SimulatorClosed("Cannot reset closed Simulator.")

        if seed is not None:
            self.seed = seed

        for key in self.signals:
            self.signals.reset(key)

        self.rng = np.random.RandomState(self.seed)
        self._steps = [
            op.make_step(self.signals, self.dt, self.rng) for op in self._step_order
        ]

        self.clear_probes()

        self._probe_step_time()
        

    def clear_probes(self):
        for probe in self.model.probes:
            self._sim_data[probe] = []
        self.data.reset()


    def _probe_step_time(self):
        self._n_steps = self.signals[self.model.step].item()
        self._time = self.signals[self.model.time].item()

    
    def trange(self, dt=None):
        dt = self.dt if dt is None else dt
        n_steps = int(self.n_steps * (self.dt / dt))
        return dt * np.arange(1, n_steps + 1)

    
    def step(self):
        pass

    
    def close(self):
        pass

    
    def __del__(self):
        pass

    
    def __enter__(self):
        return self

    
    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    