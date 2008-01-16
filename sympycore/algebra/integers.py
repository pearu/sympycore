
from ..core.utils import singleton
from ..core import classes

from .algebraic_structures import BasicAlgebra
from .primitive import PrimitiveAlgebra, SYMBOL, NUMBER, ADD, MUL
#from .pairs import (CommutativePairs, PairsCommutativeRing, CommutativeTerms,
#                    CommutativeFactors, PairsCommutativeSymbol, PairsNumber)

from .pairs import CommutativeRingWithPairs

def gcd(a, b):
    while a:
        a, b = b%a, a
    return b

# Optimization ideas:
# 1) in multiplication can exponents grow, so one could avoid checking for zeros

class Integers(CommutativeRingWithPairs):
    """ Represents a symbolic algebra of integers.

    The set of integers is a commutative ring.

    See
      http://code.google.com/p/sympycore/wiki/Algebra
    """

    @classmethod
    def Number(cls, num):
        if isinstance(num, (int,long)):
            return cls(num, head=NUMBER)
        raise TypeError(`num`)

    @classmethod
    def Symbol(cls, obj):
        return cls(obj, head=SYMBOL)

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
            return Integers(base.data ** exponent, head=NUMBER)
        if head is ADD:
            bb, nn = base.as_terms_intcoeff()
            return Integers({bb: exponent}, head=MUL) * nn**exponent
        return Integers({base: exponent}, head=MUL)

    def as_terms_intcoeff(self):
        """ Split expression into (<subexpr>, <integer coeff>) such that
        <self> == <subexpr> * <integer coeff>.
        """
        head = self.head
        if head is NUMBER:
            return one, self.data
        if head is ADD:
            pairs = self.data
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
                return Integers(l, head=ADD), coeff
        if head is MUL:
            pairs = self.data
            l = []
            coeff = 1
            for t, c in pairs.iteritems():
                tt, cc = t.as_terms_intcoeff()
                l.append((tt, c))
                coeff *= cc ** c
            if coeff != 1:
                return Integers(l, head=MUL), coeff
        return self, 1
        
    
class IntegerNumber(Integers): # XXX: to be removed

    def __pow__(self, other):
        if isinstance(other, (int, long, IntegerNumber)):
            if other>=0:
                return IntegerNumber(self.data ** other)
        return NotImplemented

one = Integers(1, head=NUMBER)
zero = Integers(0, head=NUMBER)

Integers.algebra_numbers = (int, long)   # these types are converted to NUMBER
Integers.algebra_class = Integers  # used in pairs to define Add, Mul class methods
Integers.zero = zero               # zero element of symbolic integer algebra
Integers.one = one                 # one element of symbolic integer algebra
