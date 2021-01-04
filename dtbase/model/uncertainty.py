import numpy as np
from scipy.stats import norm

class Estimate:
    def __init__(self, a: float, b: float, sample_size: int=10000):
        self.rng = np.random.default_rng()
        self.a = a
        self.b = b
        self.sample_size = sample_size
    
    def to_tuple(self):
        return (self.a, self.b, self.sample_size)

    def __call__(self) -> tuple:
        pass

class Uniform(Estimate):
    def __init__(self, a: float, b: float, sample_size: int=10000):
        # a and b are the maximum and minimum
        Estimate.__init__(self, a, b, sample_size)

    def __call__(self) -> np.array:
        return self.rng.uniform(self.a, self.b, self.sample_size)

class Normal(Estimate):
    def __init__(self, a: float, b: float, sample_size: int=10000):
        # a and b form a 95% confidence interval
        Estimate.__init__(self, a, b, sample_size)
    
    def __call__(self) -> np.array:
        return self.rng.uniform(self.a, self.b, self.sample_size)