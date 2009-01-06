
from ..basealgebra import Algebra

class Ring(Algebra):
    """
    Ring represents algebraic ring (R, +, *) where (R, +) is abelian
    group, (R,*) is monoid, with distributivity.
    """

    def __str__(self):
        h, d = self.pair
        return h.data_to_str_and_precedence(type(self), d)[0]

    def __pos__(self):
        return self

    def __neg__(self):
        return self.head.neg(type(self), self)

    def __add__(self, other):
        cls = type(self)
        tother = type(other)
        if cls is not tother:
            other = cls.convert(other)
        return self.head.add(cls, self, other)

    __radd__ = __add__

    def __sub__(self, other):
        return self + (-other)

    def __rsub__(self, other):
        return other + (-self)

    def __mul__(self, other):
        cls = type(self)
        tother = type(other)
        if cls is not tother:
            other = cls.convert(other)
        return self.head.ncmul(cls, self, other)

    def __rmul__(self, other):
        cls = type(self)
        tother = type(other)
        if cls is not tother:
            other = cls.convert(other)
        return other.head.ncmul(cls, other, self)

    def __pow__(self, other):
        cls = type(self)
        tother = type(other)
        if cls is not tother:
            other = cls.convert(other)
        return self.head.pow(cls, self, other)

    def __rpow__(self, other):
        cls = type(self)
        tother = type(other)
        if cls is not tother:
            other = cls.convert(other)
        return other.head.pow(cls, other, self)

    def __div__(self, other):
        cls = type(self)
        tother = type(other)
        if cls is not tother:
            other = cls.convert(other)
        return self * other**-1

    def __rdiv__(self, other):
        cls = type(self)
        tother = type(other)
        if cls is not tother:
            other = cls.convert(other)
        return other * self**-1
