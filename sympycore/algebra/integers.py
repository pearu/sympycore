
from ..core.utils import singleton
from ..core import classes

from .primitive import PrimitiveAlgebra, SYMBOL, NUMBER, ADD, MUL
from .pairs import CommutativePairs, PairsCommutativeRing

def gcd(a, b):
    while a:
        a, b = b%a, a
    return b

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
        if num is cls.one_e:
            return IntegerFactors([(base, exponent)])
        if num < cls.zero_e:
            return IntegerFactors([(base, exponent)])
        if head is NUMBER:
            if terms is cls.one_c:
                return IntegerNumber(base.value ** num.value)
            return IntegerFactors([(IntegerNumber(base.value ** num.value), terms)])
        if head is ADD:
            bb, nn = base.as_terms_intcoeff()
            return IntegerFactors([(bb**terms, num)]) * nn**num
        else:
            return IntegerFactors([(base**terms, num)])

    def as_terms_intcoeff(self):
        head = self.head
        one = self.one
        one_c = self.one_c
        if head is NUMBER:
            return one, self
        if head is ADD:
            pairs = self.pairs
            if len(pairs)==1:
                t, c = pairs.items()[0]
                if isinstance(c, IntegerNumber):
                    return t, c
                return self, one_c
            coeff = None
            sign = None
            l = []
            for t, c in pairs.iteritems():
                if isinstance(c, IntegerNumber):
                    if coeff is None:
                        coeff = abs(c.value)
                        sign = cmp(c.value, 0)
                        l.append((t, self.one_c * sign))
                    else:
                        coeff = gcd(abs(c.value), coeff)
                        if c.value > 0:
                            if sign==1 and coeff==1:
                                coeff = None
                                break
                            sign = 1
                        l.append((t, IntegerNumber(c.value/coeff)))
            if coeff is not None:
                if sign==-1:
                    l = [(t,-c) for (t,c) in l]
                    coeff = -coeff
                elif coeff==1:
                    return self, one_c
                return IntegerTerms(l), one_c * coeff
        return self, one_c
        
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

    def __lt__(self, other):
        return self.value < other
    def __le__(self, other):
        return self.value <= other
    def __gt__(self, other):
        return self.value > other
    def __ge__(self, other):
        return self.value >= other

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

