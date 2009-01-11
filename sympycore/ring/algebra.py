
from ..basealgebra import Algebra

def init_module(m):
    from ..core import heads
    for n,h in heads.iterNameValue(): setattr(m, n, h)

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
        cls = type(self)
        tother = type(other)
        if cls is not tother:
            other = cls.convert(other)
        return self.head.sub(cls, self, other)

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

    def expand(self):
        return self.head.expand(type(self), self)

    @classmethod
    def try_ncmul_combine(cls, lhs, rhs):
        """ Try combining lhs, rhs in non-commutative lhs*rhs operation.
        Return new expression or None.
        """
        b1, e1 = lhs.head.base_exp(cls, lhs)
        b2, e2 = rhs.head.base_exp(cls, rhs)
        if b1==b2:
            return b1 ** (e1 + e2)
        return # combining not possible
