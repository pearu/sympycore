"""
This package provides:
  - arithmetic set support: sets
  
"""


from ..core import Basic
from .number import (Number, Real, Rational, Float, Fraction, Integer,
                     Interval)
from .symbol import Symbol, Dummy, Wild
from .function import Function, Lambda, FunctionType, WildFunctionType
from .add import Add, MutableAdd, Sub
from .mul import Mul, MutableMul, Div, Pow, Sqrt
from .relational import Equal, Less
from .sets import (Complexes, Reals, Rationals, Integers, Primes,
                   Evens, Odds,
                   Positive, Negative, Divisible, Shifted,
                   Range, RangeOO, RangeOC, RangeCO, RangeCC)

from .constants import (Exp1, Pi, Infinity, NaN, ComplexInfinity,
                        GoldenRatio, EulerGamma, ImaginaryUnit)

__all__ = ['Number','Real','Rational','Float', 'Fraction', 'Integer',
           'Interval',
           'Symbol','Dummy','Wild',
           'Function','Lambda','FunctionType','WildFunctionType',
           'Add','Sub','Mul', 'Div', 'Pow', 'Sqrt',
           'Equal','Less',
           'Complexes', 'Reals', 'Rationals', 'Integers', 'Primes',
           'Evens', 'Odds',
           'Positive', 'Negative', 'Divisible', 'Shifted',
           'Range', 'RangeOO', 'RangeOC', 'RangeCO', 'RangeCC',
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
Basic.pi = pi
Basic.E = E

