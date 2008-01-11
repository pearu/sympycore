
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
    def convert(cls, obj, typeerror=True):
        if isinstance(obj, Integers):
            return obj
        if isinstance(obj, (int, long)):
            return IntegerNumber(obj)
        if isinstance(obj, (str, unicode)):
            obj = PrimitiveAlgebra(obj)
        if isinstance(obj, PrimitiveAlgebra):
            return obj.as_algebra(Integers)
        if isinstance(obj, BasicAlgebra):
            return obj.as_primitive().as_algebra(Integers)
        if typeerror:
            raise TypeError('%s.convert(<%s object>)' % (cls.__name__, type(obj)))
        return obj

    @classmethod
    def Pow(cls, base, exponent):
        base = cls.algebra_class(base)
        exponent = cls.exponent_class(exponent)
        if exponent is cls.one_e or base is cls.one:
            return base
        head = base.head
        terms, num =exponent.as_terms_intcoeff()
        if isinstance(num, IntegerNumber) and terms is cls.one_e and num < cls.zero_e:
            raise HintExtendAlgebraTo('Rationals')
        if head is NUMBER:
            if terms is one:
                return IntegerNumber(base.value ** num.value)
            if num is cls.one_e:
                b, e = base, terms
            else:
                b, e = IntegerNumber(base.value ** num.value), terms
        else:
            if num is cls.one_e:
                b, e = base, terms
            else:
                b, e = base ** terms, num
        head = b.head
        if head is MUL:
            result = IntegerFactors(iter(b))
        else:
            result = IntegerFactors([(b, cls.one_e)])
        result._multiply_values(e, 1, 0)
        return result.canonize_mul()

    def as_terms_intcoeff(self):
        head = self.head
        one = self.one
        if head is NUMBER:
            return one, self
        if head is ADD:
            pairs = self.pairs
            if len(pairs)==1:
                t, c = pairs.items()[0]
                if isinstance(c, IntegerNumber):
                    return t, c
                return self, one
        return self, one
        
    def __pos__(self):
        return self



@singleton
def makeinteger(p):
    obj = object.__new__(IntegerNumber)
    obj.value = p
    return obj
    
class IntegerNumber(Integers):

    head = NUMBER

    def __new__(cls, p):
        if p==0: return makeinteger(0)
        if p==1: return makeinteger(1)
        o = object.__new__(cls)
        o.value = p
        return o

    def __eq__(self, other):
        other = self.convert(other, False)
        if isinstance(other, IntegerNumber):
            return self.value==other.value
        return False

    def __hash__(self):
        return hash(self.value)

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self.value)

    def as_primitive(self):
        value = self.value
        if value<0:
            return -PrimitiveAlgebra((NUMBER, -value))
        return PrimitiveAlgebra((NUMBER, value))

    def __neg__(self):
        return IntegerNumber(-self.value)

    def __add__(self, other):
        other = Integers(other)
        if isinstance(other, Integers):
            head = other.head
            if head is NUMBER:
                return IntegerNumber(self.value + other.value)
            return self.Add([self, other])
        return NotImplemented

    def __mul__(self, other):
        other = Integers(other)
        if isinstance(other, Integers):
            head = other.head
            if head is NUMBER:
                return IntegerNumber(self.value * other.value)
            return self.Mul([self, other])
        return NotImplemented

    def __pow__(self, other):
        other = Integers(other)
        if isinstance(other, Integers):
            head = other.head
            if head is NUMBER:
                return IntegerNumber(self.value ** other.value)
            return self.Pow(self, other)
        return NotImplemented

class IntegerSymbol(Integers):

    head = SYMBOL

    def __new__(cls, obj):
        o = object.__new__(cls)
        o.data = obj
        return o

    def __hash__(self):
        return hash(self.data)

    def __eq__(self, other):
        other = self.convert(other, False)
        if isinstance(other, IntegerSymbol):
            return self.data==other.data
        return False

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self.data)

    def as_primitive(self):
        return PrimitiveAlgebra((SYMBOL, self.data))

class IntegerTerms(CommutativePairs, Integers):

    head = ADD

    __str__ = Integers.__str__
    as_primitive = CommutativePairs.as_primitive_add

    def __eq__(self, other):
        other = self.convert(other, False)
        if isinstance(other, IntegerTerms):
            return self.pairs==other.pairs
        return False

class IntegerFactors(CommutativePairs, Integers):

    head = MUL

    __str__ = Integers.__str__
    as_primitive = CommutativePairs.as_primitive_mul

    def __eq__(self, other):
        other = self.convert(other, False)
        if isinstance(other, IntegerFactors):
            return self.pairs==other.pairs
        return False

zero = IntegerNumber(0)
one = IntegerNumber(1)

Integers.algebra_class = Integers
Integers.exponent_class = Integers
Integers.zero = zero
Integers.zero_e = zero
Integers.zero_c = zero
Integers.one = one
Integers.one_c = one
Integers.one_e = one
Integers.algebra_c = (int, long)

Integers.element_classes = {SYMBOL: IntegerSymbol,
                            NUMBER: IntegerNumber,
                            ADD: IntegerTerms,
                            MUL: IntegerFactors
                            }

