
from ..core.utils import singleton
from ..core import classes

from .algebraic_structures import BasicAlgebra
from .primitive import PrimitiveAlgebra, SYMBOL, NUMBER, ADD, MUL
from .pairs import CommutativePairs, PairsCommutativeRing

def gcd(a, b):
    while a:
        a, b = b%a, a
    return b

# Optimization ideas:
# 1) in multiplication exponents grow, so one could avoid checking for zeros

class Integers(PairsCommutativeRing):
    """ Represents a symbolic algebra of integers.

    The set of integers is a commutative ring.

    See
      http://code.google.com/p/sympycore/wiki/Algebra
    """

    @classmethod
    def convert(cls, obj, typeerror=True):
        """
        """
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
        else:
            return NotImplemented
        return obj

    @classmethod
    def Pow(cls, base, exponent):
        if exponent==0:
            return cls.one
        if exponent==1 or cls.one==base:
            return base
        head = base.head
        if exponent < 0:
            raise HintExtendAlgebraTo('Rationals')
        if head is NUMBER:
            return IntegerNumber(base.value ** exponent)
        if head is ADD:
            bb, nn = base.as_terms_intcoeff()
            return IntegerFactors({bb: exponent}) * nn**exponent
        return IntegerFactors({base: exponent})

    def as_terms_intcoeff(self):
        """ Split expression into (<expr-monoid>, <integer coefficient>)
        """
        head = self.head
        if head is NUMBER:
            return one, self.value
        if head is ADD:
            pairs = self.pairs
            if len(pairs)==1:
                t, c = pairs.items()[0]
                tt, cc = t.as_terms_intcoeff()
                return tt, cc * c
            coeff = None
            sign = None
            l = []
            for t, c in pairs.iteritems():
                t, cc = t.as_terms_intcoeff()
                value = c * cc
                l.append((t, value))
                if coeff is None:
                    coeff = abs(value)
                    sign = cmp(value, 0)
                else:
                    coeff = gcd(abs(value), coeff)
                    if value > 0:
                        if sign==1 and coeff==1:
                            coeff = None
                            break
                        sign = 1
            if coeff is not None:
                if sign==-1:
                    l = [(t,-c/coeff) for (t,c) in l]
                    coeff = -coeff
                elif coeff==1:
                    return self, 1
                else:
                    l = [(t,c/coeff) for (t,c) in l]
                return IntegerTerms(l), coeff
        if head is MUL:
            pairs = self.pairs
            l = []
            coeff = 1
            for t, c in pairs.iteritems():
                tt, cc = t.as_terms_intcoeff()
                l.append((tt, c))
                coeff *= cc ** c
            if coeff != 1:
                return IntegerFactors(l), coeff
        return self, 1
        
    def __pos__(self):
        return self

    
class IntegerNumber(Integers):

    head = NUMBER

    def __new__(cls, p):
        o = object.__new__(cls)
        o.value = p
        return o

    def __eq__(self, other):
        if self is other:
            return True
        other = self.convert(other, False)
        if isinstance(other, IntegerNumber):
            return self.value==other.value
        return False

    def __hash__(self):
        return hash(self.value)

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self.value)

    def __int__(self):
        return int(self.value)
    def __long__(self):
        return long(self.value)

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

    def __abs__(self):
        return IntegerNumber(abs(self.value))
    def __neg__(self):
        return IntegerNumber(-self.value)

    def __add__(self, other):
        other = self.convert(other, False)
        if isinstance(other, Integers):
            if self.value==0:
                return other
            head = other.head
            if head is NUMBER:
                return IntegerNumber(self.value + other.value)
            if head is SYMBOL:
                return IntegerTerms({one: self.value, other: 1})
            if head is ADD:
                result = other.copy()
                result._add_value(one, self.value, 0)
                return result.canonize_add()
            if head is MUL:
                return IntegerTerms({one: self.value, other: 1})
            return self.Add([self, other])
        return NotImplemented

    def __mul__(self, other):
        other = self.convert(other, False)
        if isinstance(other, Integers):
            value = self.value
            if value==1:
                return other
            if value==0:
                return self
            head = other.head
            if head is NUMBER:
                return IntegerNumber(value * other.value)
            if head is SYMBOL:
                return IntegerTerms({other:value})
            if head is ADD:
                result = other.copy()
                result._multiply_values(value, 1, 0)
                return result
            if head is MUL:
                return IntegerTerms({other:value})
            return self.Mul([self, other])
        return NotImplemented

    def __pow__(self, other):
        if isinstance(other, (int, long, IntegerNumber)):
            if other>=0:
                return IntegerNumber(self.value ** other)
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
        if self is other:
            return True
        other = self.convert(other, False)
        if isinstance(other, IntegerSymbol):
            return self.data==other.data
        return False

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self.data)

    def as_primitive(self):
        return PrimitiveAlgebra((SYMBOL, self.data))

    def __add__(self, other):
        other = self.convert(other, False)
        if isinstance(other, Integers):
            head = other.head
            if head is NUMBER:
                value = other.value
                if value==0:
                    return self
                return IntegerTerms({self:1, one:value})
            if head is SYMBOL:
                if self.data == other.data:
                    return IntegerTerms({self: 2})
                return IntegerTerms({self: 1, other: 1})
            if head is ADD:
                result = other.copy()
                result._add_value(self, 1, 0)
                return result.canonize_add()
            if head is MUL:
                return IntegerTerms({self: 1, other: 1})
            return self.Add([self, other])
        return NotImplemented

    def __mul__(self, other):
        other = self.convert(other, False)
        if isinstance(other, Integers):
            head = other.head
            if head is NUMBER:
                value = other.value
                if value==1:
                    return self
                if value==0:
                    return other
                return IntegerTerms({self:value})                
            if head is SYMBOL:
                if self.data==other.data:
                    return IntegerFactors({self: 2})
                return IntegerFactors({self: 1, other: 1})
            if head is ADD:
                if other.length()>1:
                    return IntegerFactors({self:1, other: 1})
                t, c = other.pairs.items()[0]
                if t==self:
                    return IntegerTerms({IntegerFactors({t: 2}): c})
                return IntegerTerms({IntegerFactors({t: 1, self:1}): c})
            if head is MUL:
                result = other.copy()
                result._add_value(self, 1, 0)
                return result.canonize_mul()
            return self.Mul([self, other])
        return NotImplemented

class IntegerTerms(CommutativePairs, Integers):

    head = ADD

    __str__ = Integers.__str__
    as_primitive = CommutativePairs.as_primitive_add

    def __eq__(self, other):
        if self is other:
            return True
        other = self.convert(other, False)
        if isinstance(other, IntegerTerms):
            return self.pairs==other.pairs
        return False

    def __add__(self, other):
        other = self.convert(other, False)
        if isinstance(other, Integers):
            head = other.head
            if head is NUMBER:
                value = other.value
                if value==0:
                    return self
                result = self.copy()
                result._add_value(one, value, 0)
                return result.canonize_add()
            if head is SYMBOL:
                result = self.copy()
                result._add_value(other, 1, 0)
                return result.canonize_add()
            if head is ADD:
                if self.length() < other.length():
                    result = other.copy()
                    result._add_values(self, 1, 0)
                else:
                    result = self.copy()
                    result._add_values(other, 1, 0)
                return result.canonize_add()
            if head is MUL:
                result = self.copy()
                result._add_value(other, 1, 0)
                return result.canonize_add()
            return self.Add([self, other])
        return NotImplemented

    def __mul__(self, other):
        other = self.convert(other, False)
        if isinstance(other, Integers):
            head = other.head
            if head is NUMBER:
                value = other.value
                if value==1:
                    return self
                if value==0:
                    return other
                result = self.copy()
                result._multiply_values(value, 1, 0)
                return result
            if head is SYMBOL:
                if self.length()>1:
                    return IntegerFactors({self:1, other: 1})
                pairs = self.pairs
                t, c = pairs.items()[0]
                if t==other:
                    return IntegerTerms({IntegerFactors({t: 2}): c})
                return IntegerTerms({IntegerFactors({t: 1, other:1}): c})
            if head is ADD:
                if self.pairs==other.pairs:
                    return IntegerFactors({self: 2})
                return IntegerFactors({self: 1, other: 1})
            if head is MUL:
                result = other.copy()
                result._add_value(self, 1, 0)
                return result.canonize_mul()
            return self.Mul([self, other])
        return NotImplemented


class IntegerFactors(CommutativePairs, Integers):

    head = MUL

    __str__ = Integers.__str__
    as_primitive = CommutativePairs.as_primitive_mul

    def __eq__(self, other):
        if self is other:
            return True
        other = self.convert(other, False)
        if isinstance(other, IntegerFactors):
            return self.pairs==other.pairs
        return False

    def __add__(self, other):
        other = self.convert(other, False)
        if isinstance(other, Integers):
            head = other.head
            if head is NUMBER:
                value = other.value
                if value==0:
                    return self
                return IntegerTerms({one: value, self: 1})
            if head is SYMBOL:
                return IntegerTerms({self: 1, other: 1})
            if head is ADD:
                result = other.copy()
                result._add_value(self, 1, 0)
                return result.canonize_add()
            if head is MUL:
                if self.pairs == other.pairs:
                    return IntegerTerms({self:2})
                return IntegerTerms({self: 1, other: 1})
            return self.Add([self, other])
        return NotImplemented

    def __mul__(self, other):
        other = self.convert(other, False)
        if isinstance(other, Integers):
            head = other.head
            if head is NUMBER:
                value = other.value
                if value==1:
                    return self
                if value==0:
                    return other
                return IntegerTerms({self:value})
            if head is SYMBOL:
                result = self.copy()
                result._add_value(other, 1, 0)
                return result.canonize_mul()
            if head is ADD:
                result = self.copy()
                result._add_value(other, 1, 0)
                return result.canonize_mul()
            if head is MUL:
                if self.length() < other.length():
                    result = other.copy()
                    result._add_values(self, 1, 0)
                else:
                    result = self.copy()
                    result._add_values(other, 1, 0)
                return result.canonize_mul()
            return self.Mul([self, other])
        return NotImplemented

one = IntegerNumber(1)
zero = IntegerNumber(0)

Integers.algebra_c = (int, long)   # these types are converted to NUMBER
Integers.algebra_class = Integers  # used in pairs to define Add, Mul class methods
Integers.zero = zero               # zero element of symbolic integer algebra
Integers.zero_c = 0                # zero element of coefficient algebra
Integers.zero_e = 0                # zero element of exponent algebra
Integers.one = one                 # one element of symbolic integer algebra
Integers.one_c = 1                 # one element of coefficient algebra
Integers.one_e = 1                 # one element of exponent algebra

Integers.element_classes = {\
    SYMBOL: IntegerSymbol,
    NUMBER: IntegerNumber,
    ADD: IntegerTerms,
    MUL: IntegerFactors
    }

