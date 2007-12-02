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
from .constants import initialize_constants

initialize_constants() # operations uses oo,nan,etc.

#from .operations import Add, Mul, Sub, Div
from .add import Add, Sub
from .mul import Mul, Div
from .pow import Pow, Sqrt
from .relational import Equal, Less
from .sets import (Complexes, Reals, Rationals, Integers, Primes,
                   Evens, Odds,
                   Positive, Negative, Divisible, Shifted,
                   Range, RangeOO, RangeOC, RangeCO, RangeCC)

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

objects.moo = -objects.oo
