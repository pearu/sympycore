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
from .operator import Operator, OperatorType, D

from .constants import initialize_constants

initialize_constants() # operations in add.py,mul.py uses oo,nan,etc.

from .add import Add, Sub
from .mul import Mul, Div
from .pow import Pow, Log, Root, Ln, Exp, Sqrt, Lg, Lb

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
           'Operator','OperatorType','D',
           'Add', 'Mul', 'Pow','Sub','Div','Sqrt',
           'Root','Exp','Log','Ln','Lg','Lb',
           'Equal','Less',
           'Complexes', 'Reals', 'Rationals', 'Integers', 'Primes',
           'Evens', 'Odds',
           'Positive', 'Negative', 'Divisible', 'Shifted',
           'Range', 'RangeOO', 'RangeOC', 'RangeCO', 'RangeCC',
           ]

objects.moo = -objects.oo
