
__all__ = ['Ring', 'CommutativeRing']

from ..basealgebra import Algebra
from .interface import RingInterface

from ..core import init_module
init_module.import_heads()

@init_module
def _init(m):
    from ..arithmetic import mpq
    Ring.coefftypes = (int, long, mpq)

class Ring(Algebra, RingInterface):
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
        if type(other) is not cls:
            other = cls.convert(other, typeerror=False)
            if other is NotImplemented:
                return NotImplemented
        return self.head.add(cls, self, other)

    __radd__ = __add__

    def __sub__(self, other):
        cls = type(self)
        tother = type(other)
        if cls is not tother:
            other = cls.convert(other, typeerror=False)
            if other is NotImplemented:
                return NotImplemented
        return self.head.sub(cls, self, other)

    def __rsub__(self, other):
        return other + (-self)

    def __mul__(self, other):
        cls = type(self)
        tother = type(other)
        if cls is not tother:
            other = cls.convert(other, typeerror=False)
            if other is NotImplemented:
                return NotImplemented
        return self.head.non_commutative_mul(cls, self, other)

    def __rmul__(self, other):
        cls = type(self)
        tother = type(other)
        if cls is not tother:
            other = cls.convert(other, typeerror=False)
            if other is NotImplemented:
                return NotImplemented
        return other.head.non_commutative_mul(cls, other, self)

    def __pow__(self, other):
        cls = type(self)
        tother = type(other)
        if cls is not tother:
            other = cls.convert(other, typeerror=False)
            if other is NotImplemented:
                return NotImplemented
        return self.head.pow(cls, self, other)

    def __rpow__(self, other):
        cls = type(self)
        tother = type(other)
        if cls is not tother:
            other = cls.convert(other, typeerror=False)
            if other is NotImplemented:
                return NotImplemented
        return other.head.pow(cls, other, self)

    def __div__(self, other):
        cls = type(self)
        tother = type(other)
        if cls is not tother:
            other = cls.convert(other, typeerror=False)
            if other is NotImplemented:
                return NotImplemented
        return self * other**-1

    def __rdiv__(self, other):
        cls = type(self)
        tother = type(other)
        if cls is not tother:
            other = cls.convert(other, typeerror=False)
            if other is NotImplemented:
                return NotImplemented
        return other * self**-1

    def expand(self):
        return self.head.expand(type(self), self)

class CommutativeRing(Ring):

    def __mul__(self, other):
        cls = type(self)
        tother = type(other)
        if cls is not tother:
            other = cls.convert(other, typeerror=False)
            if other is NotImplemented:
                return NotImplemented
        return self.head.commutative_mul(cls, self, other)

    def __rmul__(self, other):
        cls = type(self)
        tother = type(other)
        if cls is not tother:
            other = cls.convert(other, typeerror=False)
            if other is NotImplemented:
                return NotImplemented
        return other.head.commutative_mul(cls, other, self)

    def to(self, target, *args):
        """ Convert expression to target representation.

        The following targets are recognized:

          EXP_COEFF_DICT - convert expression to exponents-coefficient
                           representation, additional arguments are
                           variables. When no arguments are specified,
                           variables will be all symbols used in the
                           expression.
        
        """
        head, data = self.pair
        if target is EXP_COEFF_DICT:
            return head.to_EXP_COEFF_DICT(type(self), data, self, args or None)
        raise NotImplementedError('%s.convert(target=%r)' % (type(self), target))

