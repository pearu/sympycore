"""
This package provides:

  - arithmetic sets: Complexes, Reals, Rationals, Integers, Evens,
                    Odds, Primes
  - arithmetic set operations: Positive, Negative, Divisible, Shifted
  - ranges: Range, RangeOO, RangeOC, RangeCO, RangeCC

"""

from .defined import ComplexSet, RealSet, RationalSet, IntegerSet, PrimeSet
from .operations import Positive, Negative, Divisible, Shifted
from .ranges import Range, RangeOO, RangeOC, RangeCO, RangeCC

from ...core import Basic
from ...core.function import FunctionSignature
from ...logic.sets import Complementary, set_classes

Positive.signature = FunctionSignature((set_classes,), set_classes)
Negative.signature = FunctionSignature((set_classes,), set_classes)
Shifted.signature = FunctionSignature((set_classes,Basic), set_classes)
Divisible.signature = FunctionSignature((set_classes,Basic), set_classes)

Complexes = ComplexSet()
Reals = RealSet()
Rationals = RationalSet()
Integers = IntegerSet()
Primes = PrimeSet()
Evens = Divisible(Integers,2)
Evens.__doc__ = ' Set of even integers.'
Odds = Complementary(Evens, Integers)
Odds.__doc__ = ' Set of odd integers.'
del Complementary
