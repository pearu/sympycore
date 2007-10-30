
from ...core import Basic
from ...core.function import FunctionSignature
from ...logic.sets import SetFunction, set_classes
from .basic import ArithmeticSetFunction

class Positive(ArithmeticSetFunction):
    """ Set of positive values in a set S.

    x in Positive(S) <=> x>0 and x in S
    """

    @classmethod
    def canonize(cls, (set,)):
        return set.try_positive()
    def try_positive(self):
        return self
    def try_negative(self):
        return Empty
    def try_element(self, other):
        set = self.args[0]
        r = set.try_element(other)
        if isinstance(r, bool):
            if r:
                r = other.is_positive
            if isinstance(r, bool):
                return r
    def is_subset_of(self, other):
        set = self.args[0]
        if set==other:
            return True
    def try_infimum(self):
        m = 0
        if self.domain==Integers:
            m = 1
        return Basic.Max(Basic.Min(self[0]), m)
    def try_supremum(self):
        m = 0
        if self.domain==Integers:
            m = 1
        return Basic.Max(Basic.Max(self[0]), m)


class Negative(ArithmeticSetFunction):
    """ Set of negative values in a set S.

    x in Negative(S) <=> x<0 and x in S
    """
    @classmethod
    def canonize(cls, (set,)):
        return set.try_negative()
    def try_negative(self):
        return self
    def try_positive(self):
        return Empty
    def try_element(self, other):
        set = self.args[0]
        r = set.try_element(other)
        if isinstance(r, bool):
            if r:
                r = other.is_negative
            if isinstance(r, bool):
                return r
    def is_subset_of(self, other):
        set = self.args[0]
        if set==other:

            return True
    def try_infimum(self):
        m = 0
        if self.domain==Integers:
            m = -1
        return Basic.Min(Basic.Min(self[0]), m)
    def try_supremum(self):
        m = 0
        if self.domain==Integers:
            m = -1
        return Basic.Min(Basic.Max(self[0]), m)


class Shifted(ArithmeticSetFunction):
    """ Set of shifted values in S.

    x in Shifted(S, s) <=> x-s in S
    """    
    @property
    def shift(self):
        return self[1]

    @classmethod
    def canonize(cls, (set, shift)):
        if shift==0: return set
        if set.is_EmptySet: return set
        return set.try_shifted(shift)

    def try_shifted(self, shift):
        return Shifted(self[0], self.shift+shift)
    def try_element(self, other):
        set, shift = self.args
        r = set.try_element(other-shift)
        if isinstance(r, bool):
            return r
    def try_supremum(self):
        r = self[0].try_supremum()
        if r is not None:
            return r + self[1]
    def try_infimum(self):
        r = self[0].try_infimum()
        if r is not None:
            return r + self[1]


class Divisible(ArithmeticSetFunction):
    """ Set of values in S that divide by divisor.

    x in Divisible(S, d) <=> x in S & x/d in S
    """
    @property
    def superset(self):
        return self.args[0]

    @classmethod
    def canonize(cls, (set, divisor)):
        if divisor==1: return set
        if set.is_RealSet and divisor.is_Real:
            return set
        if set.is_RationalSet and divisor.is_Rational:
            return set
        return

    def try_element(self, other):
        set, divisor = self.args
        r = set.try_element(other)
        if isinstance(r, bool):
            if r:
                r = set.try_element(other/divisor)
            if isinstance(r, bool):
                return r
    def is_subset_of(self, other):
        set = self.args[0]
        if set==other:
            return True
        if other.is_Complementary and other.set==self:
            return False
    def try_infimum(self):
        set,divisor = self.args
        return Basic.Min(set) / divisor
    def try_supremum(self):
        set,divisor = self.args
        return Basic.Max(set) / divisor

