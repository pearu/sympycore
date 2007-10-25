"""
This package provides:
  - arithmetic set support: sets
  
"""




from ..core import Basic
from .number import (Number, Real, Rational, Float, Fraction, Integer,
                     Interval)
from .add import Add, MutableAdd
from .mul import Mul, MutableMul, Pow, sqrt
from .sets import (Complexes, Reals, Rationals, Integers, Primes,
                   Evens, Odds,
                   Positive, Negative, Divisible, Shifted,
                   Range, RangeOO, RangeOC, RangeCO, RangeCC)


from .constants import (Exp1, Pi, Infinity, NaN, ComplexInfinity,
                        GoldenRatio, EulerGamma, ImaginaryUnit)

__all__ = ['Number','Real','Rational','Float', 'Fraction', 'Integer',
           'Interval','Add','Mul',
           'Complexes', 'Reals', 'Rationals', 'Integers', 'Primes',
           'Evens', 'Odds',
           'Positive', 'Negative', 'Divisible', 'Shifted',
           'Range', 'RangeOO', 'RangeOC', 'RangeCO', 'RangeCC',
           'sqrt',
           'E','pi','oo','nan','I'
           ]

E = Exp1()
pi = Pi()
oo = Infinity()
nan = NaN()
zoo = ComplexInfinity()
I = ImaginaryUnit()

Basic.oo = oo
Basic.nan = nan
Basic.zoo = zoo
Basic.I = I
