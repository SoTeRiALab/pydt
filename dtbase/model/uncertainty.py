import numpy as np
from scipy.stats import norm

class Estimate:
    def __init__(self, a: float, b: float, sample_size: int=10000, seed: int=None):
        if seed:
            self.rng = np.random.default_rng(seed)
        else:
            self.rng = np.random.default_rng()
        self.point_estimate = None
        self.a = a
        self.b = b
        self.sample_size = sample_size
        self.seed = seed
    
    def sample(self) -> np.array:
        pass

class Uniform(Estimate):
    def __init__(self, a: float, b: float, sample_size: int=10000, seed: int=None):
        # a and b are the maximum and minimum
        Estimate.__init__(self, a, b, sample_size, seed)
        self.point_estimate = (a + b) / 2.0

    def sample(self) -> np.array:
        return self.rng.uniform(self.a, self.b, self.sample_size)

class Normal(Estimate):
    def __init__(self, a: float, b: float, sample_size: int=10000, seed: int=None, confidence_level: float = .95):
        # a and b form a 95% confidence interval
        Estimate.__init__(self, sample_size, seed)
        self.point_estimate = (a + b) / 2
        self.sd = (b - self.point_estimate) / norm.ppf(confidence_level)
    
    def sample(self) -> np.array:
        return self.rng.uniform(self.point_estimate, self.sd, self.sample_size)