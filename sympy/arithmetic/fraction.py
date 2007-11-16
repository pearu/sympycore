from ..core.utils import memoizer_immutable_args, memoizer_Fraction
from ..core import Basic, sympify, classes, objects
from .number import Rational

#@memoizer_immutable_args('makefraction')
def makefraction(p,q):
    obj = object.__new__(Fraction)
    obj.p = p
    obj.q = q
    obj._hashvalue = None
    return obj

def makefraction_from_man_exp(man, exp):
    if exp > 0:
        return classes.Integer(man * 2 ** exp)
    obj = Fraction(man, 2** -exp)
    if obj.is_Fraction: return obj
    return obj.as_Fraction


class Fraction(Rational):
    """
    Represents a ratio p/q of two integers.

    This implementation relies completely on the implementation
    of Integer.
    """

    # strangely caching Fraction instances has no noticable effect on speed..
    #@memoizer_Fraction
    def __new__(cls, p, q):
        if q<0:
            p, q = -p, -q
        r = classes.Integer.gcd(abs(p), q)
        if r>1:
            p //= r
            q //= r
        if q==1:
            return classes.Integer(p)
        return makefraction(p,q)

    make = staticmethod(makefraction)
    make_from_man_exp = staticmethod(makefraction_from_man_exp)

    def __hash__(self):
        if self._hashvalue is None:
            self._hashvalue = hash((self.p, self.q))
        return self._hashvalue

    @property
    def is_half(self):
        return (self.p,self.q)==(1,2)

    def __eq__(self, other):
        if isinstance(other, Basic):
            if self is other:
                return True
            if other.is_Integer:
                other = other.as_Fraction
            if other.is_Fraction:
                return self.p==other.p and self.q==other.q
            if other.is_Number:
                return NotImplemented
            return False
        if isinstance(other, bool):
            return False
        return self == sympify(other)

    def __ne__(self, other):
        other = sympify(other)
        if isinstance(other, Basic):
            if self is other:
                return False
            if other.is_Integer:
                other = other.as_Fraction
            if other.is_Fraction:
                return self.p!=other.p or self.q!=other.q
        if isinstance(other, bool):
            return True
        return NotImplemented

    def __lt__(self, other):
        other = sympify(other)
        if self is other: return False
        if isinstance(other, Basic):
            if other.is_Integer:
                other = other.as_Fraction
            if other.is_Fraction:
                return self.p * other.q < self.q * other.p
        return NotImplemented

    def __le__(self, other):
        other = sympify(other)
        if self is other: return True
        if isinstance(other, Basic):
            if other.is_Integer:
                other = other.as_Fraction
            if other.is_Fraction:
                return self.p * other.q <= self.q * other.p
        return NotImplemented

    def __gt__(self, other):
        if isinstance(other, bool):
            return False
        other = sympify(other)
        if self is other: return False
        if isinstance(other, Basic):
            if other.is_Integer:
                other = other.as_Fraction
            if other.is_Fraction:
                return self.p * other.q > self.q * other.p
        return NotImplemented

    def __ge__(self, other):
        other = sympify(other)
        if self is other: return True
        if isinstance(other, Basic):
            if other.is_Integer:
                other = other.as_Fraction
            if other.is_Fraction:
                return self.p * other.q >= self.q * other.p
        return NotImplemented

    def __pos__(self):
        return self

    def __neg__(self):
        return self.make(-self.p, self.q)

    def __abs__(self):
        return self.make(abs(self.p), self.q)

    def __add__(self, other):
        other = sympify(other)
        if other.is_Integer:
            return Fraction(self.p + self.q * other.p,
                            self.q)
        if other.is_Fraction:
            return Fraction(self.p * other.q + self.q * other.p,
                            self.q * other.q)
        return NotImplemented

    def __sub__(self, other):
        other = sympify(other)
        if other.is_Integer:
            return Fraction(self.p - self.q * other.p,
                            self.q)
        if other.is_Fraction:
            return Fraction(self.p * other.q - self.q * other.p,
                            self.q * other.q)
        return NotImplemented

    def __mul__(self, other):
        other = sympify(other)
        if other.is_Integer:
            return Fraction(self.p * other.p, self.q)
        if other.is_Fraction:
            return Fraction(self.p * other.p, self.q * other.q)
        return NotImplemented

    def __div__(self, other):
        other = sympify(other)
        if other.is_Integer:
            return Fraction(self.p, self.q * other.p)
        if other.is_Fraction:
            return Fraction(self.p * other.q, self.q * other.p)
        return NotImplemented

    def __pow__(self, other):
        other = sympify(other)
        r = self.try_power(other)
        if r is not None:
            return r
        return NotImplemented

    #@memoizer_immutable_args('Fraction.try_power')
    def try_power(self, other):
        if other.is_Integer:
            if other.is_negative:
                p = -other.p
                return Fraction.make(self.q ** p, self.p ** p)
            p = other.p
            return Fraction.make(self.p ** p, self.q ** p)
        if other.is_Fraction:
            return self.p ** other * self.q ** -other
        if other.is_Float:
            return self.as_Float ** other
        if other.is_Infinity or other.is_ComplexInfinity:
            if -1 < self < 1:
                return objects.zero
            if self==1:
                return self
            if self > 1:
                return other
            return objects.nan
        if other.is_NaN:
            if self==0:
                return self
            return other

    def __radd__(self, other):
        if isinstance(other, Basic):
            if other.is_Integer:
                return Fraction(self.p + self.q * other.p,
                                self.q)
            if other.is_Fraction:
                return Fraction(self.p * other.q + self.q * other.p,
                                self.q * other.q)
            return classes.Add(other, self)
        return sympify(other) + self

    def __rsub__(self, other):
        if isinstance(other, Basic):
            if other.is_Integer:
                return Fraction(-self.p + self.q * other.p,
                                self.q)
            if other.is_Fraction:
                return Fraction(-self.p * other.q + self.q * other.p,
                                self.q * other.q)
            return classes.Add(other, -self)
        return sympify(other) - self

    def __rmul__(self, other):
        if isinstance(other, Basic):
            if other.is_Integer:
                return Fraction(self.p * other.p, self.q)
            if other.is_Fraction:
                return Fraction(self.p * other.p, self.q * other.q)
            return classes.Mul(other, self)
        return sympify(other) * self

    def __rdiv__(self, other):
        if isinstance(other, Basic):
            if other.is_Integer:
                return Fraction(self.q * other.p, self.p)
            if other.is_Fraction:
                return Fraction(self.q * other.p, self.p * other.q)
            return classes.Mul(other, 1/self)
        return sympify(other) / self

    def __rpow__(self, other):
        if isinstance(other, Basic):
            return classes.Pow(other, self)
        return sympify(other) ** self

