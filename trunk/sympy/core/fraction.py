from utils import memoizer_immutable_args
from basic import Basic, sympify
from number import Rational

@memoizer_immutable_args('makefraction')
def makefraction(p,q):
    return tuple.__new__(Fraction, (p, q))

def makefraction_from_man_exp(man, exp):
    if exp > 0:
        return makefraction(man * 2 ** exp, 1)
    obj = Fraction(man, 2** -exp)
    if obj.is_Fraction: return obj
    return obj.as_Fraction

class Fraction(Rational, tuple):
    """
    Represents a ratio p/q of two integers.

    This implementation relies completely on the implementation
    of Integer.
    """


    def __new__(cls, p, q):
        if q<0:
            p, q = -p, -q
        r = Basic.Integer.gcd(abs(p), q)
        if r>1:
            p //= r
            q //= r
        if q==1:
            return Basic.Integer(p)
        return makefraction(p,q)

    make = staticmethod(makefraction)
    make_from_man_exp = staticmethod(makefraction_from_man_exp)

    @property
    def p(self): return self[0]
    
    @property
    def q(self): return self[1]

    __hash__ = tuple.__hash__

    def __eq__(self, other):
        if isinstance(other, Basic):
            if other.is_Integer:
                other = other.as_Fraction
            if other.is_Fraction:
                return tuple.__eq__(self, other)
            if other.is_Number:
                return NotImplemented
            return False
        return self == sympify(other)

    def __ne__(self, other):
        other = Basic.sympify(other)
        if self is other: return False
        if other.is_Integer:
            other = other.as_Fraction
        if other.is_Fraction:
            return tuple.__ne__(self, other)
        return NotImplemented

    def __lt__(self, other):
        other = Basic.sympify(other)
        if self is other: return False
        if other.is_Integer:
            other = other.as_Fraction
        if other.is_Fraction:
            return self.p * other.q < self.q * other.p
        return NotImplemented

    def __le__(self, other):
        other = Basic.sympify(other)
        if self is other: return True
        if other.is_Integer:
            other = other.as_Fraction
        if other.is_Fraction:
            return self.p * other.q <= self.q * other.p
        return NotImplemented

    def __gt__(self, other):
        other = Basic.sympify(other)
        if self is other: return False
        if other.is_Integer:
            other = other.as_Fraction
        if other.is_Fraction:
            return self.p * other.q > self.q * other.p
        return NotImplemented

    def __ge__(self, other):
        other = Basic.sympify(other)
        if self is other: return True
        if other.is_Integer:
            other = other.as_Fraction
        if other.is_Fraction:
            return self.p * other.q >= self.q * other.p
        return NotImplemented

    def __pos__(self):
        return self

    def __neg__(self):
        return self.make(-self.p, self.q)

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

    @memoizer_immutable_args('Fraction.try_power')
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
                return Basic.zero
            if self==1:
                return self
            if self > 1:
                return other
            return Basic.nan
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
            return Basic.Add(other, self)
        return sympify(other) + self

    def __rsub__(self, other):
        if isinstance(other, Basic):
            if other.is_Integer:
                return Fraction(-self.p + self.q * other.p,
                                self.q)
            if other.is_Fraction:
                return Fraction(-self.p * other.q + self.q * other.p,
                                self.q * other.q)
            return Basic.Add(other, -self)
        return sympify(other) - self

    def __rmul__(self, other):
        if isinstance(other, Basic):
            if other.is_Integer:
                return Fraction(self.p * other.p, self.q)
            if other.is_Fraction:
                return Fraction(self.p * other.p, self.q * other.q)
            return Basic.Mul(other, self)
        return sympify(other) * self

    def __rdiv__(self, other):
        if isinstance(other, Basic):
            if other.is_Integer:
                return Fraction(self.q * other.p, self.p)
            if other.is_Fraction:
                return Fraction(self.q * other.p, self.p * other.q)
            return Basic.Mul(other, 1/self)
        return sympify(other) / self

    def __rpow__(self, other):
        if isinstance(other, Basic):
            return Basic.Pow(other, self)
        return sympify(other) ** self

