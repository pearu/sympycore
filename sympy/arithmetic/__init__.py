"""
This package provides:
  - arithmetic set support: sets
  
"""


from ..core import Basic, objects
from .number import (Number, Real, Rational, Float, Fraction, Integer,
                     Interval)
from .symbol import Symbol, Dummy, Wild
from .function import Function, Lambda, FunctionType, WildFunctionType
from .operations import Add, Mul, Pow, Sub, Div, Sqrt
from .relational import Equal, Less
from .sets import (Complexes, Reals, Rationals, Integers, Primes,
                   Evens, Odds,
                   Positive, Negative, Divisible, Shifted,
                   Range, RangeOO, RangeOC, RangeCO, RangeCC)

from .constants import (Exp1, Pi, Infinity, NaN, ComplexInfinity,
                        GoldenRatio, EulerGamma, ImaginaryUnit)

def Sqrt(x):
    return Pow(x,Fraction(1,2))

__all__ = ['Number','Real','Rational','Float', 'Fraction', 'Integer',
           'Interval',
           'Symbol','Dummy','Wild',
           'Function','Lambda','FunctionType','WildFunctionType',
           'Add', 'Mul', 'Pow','Sub','Div','Sqrt',
           'Equal','Less',
           'Complexes', 'Reals', 'Rationals', 'Integers', 'Primes',
           'Evens', 'Odds',
           'Positive', 'Negative', 'Divisible', 'Shifted',
           'Range', 'RangeOO', 'RangeOC', 'RangeCO', 'RangeCC',
           'E','pi','oo','nan','I','zoo','moo'
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

objects.oo = oo
objects.nan = nan
objects.zoo = zoo
objects.I = I
objects.pi = pi
objects.E = E

moo = -oo
objects.moo = moo
