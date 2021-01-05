import numpy as np
from enum import Enum, auto
from scipy.stats import norm

class EstimateTypes(Enum):
    '''
    Enum representing all methods of uncertainty propagation.
    '''
    UNIFORM='UNIFORM'
    NORMAL='NORMAL'

class Estimate:
    '''
    Uses sampling to propagate uncertainty in an Estimate.

    Attributes
    ----------
    estimate_type (EstimateTypes) : an enum value representing the type of uncertainty propagation.
    rng (np.random.Generator) : a random number generator for sampling.
    a (float) : alpha parameter for the distribution.
    b (float) : beta parameter for the distribution.
    sample_size (int) : the sample size to generate.
    sample (np.array) : a numpy array with the sample
    '''
    sample_size = int(1e5)

    def __init__(self, estimate_type: EstimateTypes, a: float, b: float):
        '''
        Constructs an Estimate object.
        '''
        self.estimate_type = estimate_type
        self.rng = np.random.default_rng()
        self.a = a
        self.b = b
        if self.estimate_type == EstimateTypes.NORMAL:
            self.sample = self.normal()
        elif self.estimate_type == EstimateTypes.UNIFORM:
            self.sample = self.uniform()

    def uniform(self) -> np.array:
        '''
        Sampling function for a uniform distribution with (a, b) being the min and max parameters.
        '''
        return self.rng.uniform(self.a, self.b, Estimate.sample_size)
    
    def normal(self) -> np.array:
        '''
        Sampling function for a normal distribution with (a, b) being a 95% confidence interval.
        '''
        mp = (self.b - self.a) / 2
        z = norm.ppf(.95)
        sd = (self.b - mp) / z
        return self.rng.normal(mp, sd, Estimate.sample_size)

    def to_tuple(self) -> tuple:
        '''
        Returns a tuple representation of an Estimate.
        '''
        return (self.estimate_type.value, self.a, self.b)
