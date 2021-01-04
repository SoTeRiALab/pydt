import numpy as np
from enum import Enum, auto
from scipy.stats import norm

class EstimateTypes(Enum):
    UNIFORM='UNIFORM'
    NORMAL='NORMAL'

class Estimate:
    def __init__(self, estimate_type: EstimateTypes, a: float, b: float, sample_size: int=10000):
        self.estimate_type = estimate_type
        self.rng = np.random.default_rng()
        self.a = a
        self.b = b
        self.sample_size = int(sample_size)

    def __call__(self) -> np.array:
        if self.estimate_type == EstimateTypes.NORMAL:
            print('asdda')
            return self.normal()
        elif self.estimate_type == EstimateTypes.UNIFORM:
            return self.uniform()
        print(self.a, self.b, self.estimate_type, self.sample_size)

    def uniform(self) -> np.array:
        return self.rng.uniform(self.a, self.b, self.sample_size)
    
    def normal(self) -> np.array:
        mp = (self.b - self.a) / 2
        z = norm.ppf(.95)
        sd = (self.b - mp) / z
        return self.rng.normal(mp, sd, self.sample_size)


    def to_tuple(self):
        return (self.estimate_type.value, self.a, self.b, self.sample_size)
