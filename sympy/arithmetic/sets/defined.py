
from ...core import Basic, classes, objects
from ...core.utils import memoizer_immutable_args, singleton
from ...logic.sets import Empty
from ..primetest import isprime
from .basic import ArithmeticSetSymbol


class Field(ArithmeticSetSymbol):
    """ Represents abstract field.
    """

class ComplexSet(Field):
    """ Represents a field of complex numbers.
    """

    @singleton
    def __new__(cls):
        return str.__new__(cls, 'Complexes')
    def try_element(self, other):
        if other.is_Number:
            return True
        if other.is_ImaginaryUnit:
            return True
    @property
    def superset(self): return Universal
    def try_positive(self):
        return Positive(Reals)
    def try_negative(self):
        return Negative(Reals)
    def try_subset(self, set):
        if isinstance(set.domain, (RealSet, RationalSet, IntegerSet, PrimeSet)):
            return True
        if set.domain.is_UniversalSet:
            return False
        if set.is_ComplexSet:
            return True

class RealSet(Field):
    """ Represents a field of real numbers.
    """

    @singleton
    def __new__(cls):
        return str.__new__(cls, 'Reals')

    @property
    def superset(self):
        return Complexes 
    def try_element(self, other):
        if other.is_Number:
            if other.is_Real:
                return True
            return False
    def try_supremum(self):
        return objects.oo
    def try_infimum(self):
        return -objects.oo
    def try_positive(self):
        return classes.RangeOO(0, objects.oo, self)
    def try_negative(self):
        return classes.RangeOO(-objects.oo, 0, self)
    def try_subset(self, set):
        if isinstance(set.domain, (RationalSet, IntegerSet, PrimeSet)):
            return True
        if isinstance(set.domain, ComplexSet):
            return False
        if set.is_RealSet:
            return True
        return classes.BasicSet.try_subset(self, set)

    def as_range(self):
        return classes.RangeOO(-objects.oo, objects.oo, self)

class RationalSet(Field):
    """ Field of rational numbers.
    """
    @singleton
    def __new__(cls):
        return str.__new__(cls, 'Rationals')
    @property
    def superset(self):
        return Reals
    def try_element(self, other):
        if other.is_Number:
            if other.is_Rational:
                return True
            return False
    def try_supremum(self):
        return objects.oo
    def try_infimum(self):
        return -objects.oo
    def try_positive(self):
        return classes.RangeOO(0, objects.oo, self)
    def try_negative(self):
        return classes.RangeOO(-objects.oo, 0, self)
    def try_subset(self, set):
        if isinstance(set.domain, (IntegerSet, PrimeSet)):
            return True
        if isinstance(set.domain, (ComplexSet, RealSet)):
            return False
        if set.is_RationalSet:
            return True
        return classes.BasicSet.try_subset(self, set)

    def as_range(self):
        return classes.RangeOO(-objects.oo, objects.oo, self)

class IntegerSet(ArithmeticSetSymbol):
    """ Field of integers.
    """
    @singleton
    def __new__(cls):
        return str.__new__(cls, 'Integers')

    @property
    def superset(self):
        return Rationals
    @property
    def domain(self):
        return self
    def try_element(self, other):
        if other.is_Number:
            if other.is_Integer:
                return True
            return False
    def try_supremum(self):
        return objects.oo
    def try_infimum(self):
        return -objects.oo
    def try_positive(self):
        return classes.RangeOO(0, objects.oo, self)
    def try_negative(self):
        return classes.RangeOO(-objects.oo, 0, self)
    def try_subset(self, set):
        if isinstance(set.domain, PrimeSet):
            return True
        if isinstance(set.domain, (ComplexSet, RealSet, RationalSet)):
            return False
        if set.is_IntegerSet:
            return True
        return classes.BasicSet.try_subset(self, set)

    def as_range(self):
        return classes.RangeOO(-objects.oo, objects.oo, self)

class PrimeSet(ArithmeticSetSymbol):
    """ Set of positive prime numbers.
    """
    @singleton
    def __new__(cls):
        return str.__new__(cls, 'Primes')
    @property
    def superset(self):
        return self
    @property
    def domain(self):
        return Integers
    def try_element(self, other):
        if other.is_Number:
            if other.is_Integer and other.is_positive:
                return isprime(other)
            return False
    def try_supremum(self):
        return classes.oo
    def try_infimum(self):
        return classes.Number(2)
    def try_positive(self):
        return self
    def try_negative(self):
        return Empty

    def as_range(self):
        return classes.RangeCO(2, objects.oo, self)

