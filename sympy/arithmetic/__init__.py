"""
This package provides:
  - arithmetic set support: sets
  
"""


from ..core import Basic, objects
from .basic import BasicArithmetic
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

from .constants import initialize_constants

__all__ = ['BasicArithmetic',
           'Number','Real','Rational','Float', 'Fraction', 'Integer',
           'Interval',
           'Symbol','Dummy','Wild',
           'Function','Lambda','FunctionType','WildFunctionType',
           'Add', 'Mul', 'Pow','Sub','Div','Sqrt',
           'Equal','Less',
           'Complexes', 'Reals', 'Rationals', 'Integers', 'Primes',
           'Evens', 'Odds',
           'Positive', 'Negative', 'Divisible', 'Shifted',
           'Range', 'RangeOO', 'RangeOC', 'RangeCO', 'RangeCC',
           ]

initialize_constants()
objects.moo = -objects.oo
