
from ..core.utils import singleton
from ..core import classes

from .primitive import PrimitiveAlgebra, SYMBOL, NUMBER, ADD, MUL
from .pairs import CommutativePairs, PairsCommutativeRing

class Integers(PairsCommutativeRing):
    """ Represents a set of integers.

    The set of integers is a commutative ring.

    The / operation is not closed and the result will
    be a rational if the rhs operand does not divide with lhs.
    """

    @classmethod
    def get_kind(cls, obj):
        if isinstance(obj, (int, long)):
            return NUMBER
        return SYMBOL

    element_classes = {SYMBOL: 'IntegerSymbol',
                       NUMBER: 'IntegerNumber',
                       ADD: 'IntegerTerms',
                       MUL: 'IntegerFactors'
                       }

    def __pos__(self):
        return self

@singleton
def makeinteger(p):
    obj = object.__new__(IntegerNumber)
    obj.value = p
    return obj
    
class IntegerNumber(Integers):

    kind = NUMBER

    def __new__(cls, p):
        if p==0: return makeinteger(0)
        if p==1: return makeinteger(1)
        o = object.__new__(cls)
        o.value = p
        return o

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self.value)

    def as_primitive(self):
        # XXX: -2 -> NEG 2
        return PrimitiveAlgebra((NUMBER, self.value))

    def __add__(self, other):
        other = Integers(other)
        if isinstance(other, Integers):
            kind = other.kind
            if kind is NUMBER:
                return IntegerNumber(self.value + other.value)
        return NotImplemented

    def __mul__(self, other):
        other = Integers(other)
        if isinstance(other, Integers):
            kind = other.kind
            if kind is NUMBER:
                return IntegerNumber(self.value * other.value)
        return NotImplemented

class IntegerSymbol(Integers):

    kind = SYMBOL

    def __new__(cls, obj):
        o = object.__new__(cls)
        o.data = obj
        return o

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self.data)

    def as_primitive(self):
        return PrimitiveAlgebra((SYMBOL, self.data))

class IntegerTerms(CommutativePairs, Integers):

    kind = ADD

    __str__ = Integers.__str__
    as_primitive = CommutativePairs.as_primitive_add

class IntegerFactors(CommutativePairs, Integers):

    kind = MUL

    __str__ = Integers.__str__
    as_primitive = CommutativePairs.as_primitive_mul

zero = IntegerNumber(0)
one = IntegerNumber(1)

Integers.algebra_class = Integers
Integers.zero = zero
Integers.zero_e = zero
Integers.zero_c = zero
Integers.one = one
Integers.one_c = one
Integers.one_e = one
