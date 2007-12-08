from ..core.utils import memoizer_immutable_args, singleton, memoizer_Integer
from ..core import Basic, sympify, classes, objects
from .number import Rational

def integer_nthroot(y, n):
    """
    Usage
    =====
        Return a tuple containing x = floor(y**(1/n))
        and a boolean indicating whether the result is exact (that is,
        whether x**n == y).

    Examples
    ========

        >>> integer_nthroot(16,2)
        (4, True)
        >>> integer_nthroot(26,2)
        (5, False)
        >>> integer_nthroot(1234567**7, 7)
        (1234567L, True)
        >>> integer_nthroot(1234567**7+1, 7)
        (1234567L, False)
    """

    y = int(y); n = int(n)
    if y < 0: raise ValueError, "y must not be negative"
    if n < 1: raise ValueError, "n must be positive"
    if y in (0, 1): return y, True
    if n == 1: return y, True

    # Search with Newton's method, starting from floating-point
    # approximation. Care must be taken to avoid overflow.
    from math import log as _log
    guess = 2**int(_log(y, 2)/n)
    xprev, x = -1, guess
    while abs(x - xprev) > 1:
        t = x**(n-1)
        xprev, x = x, x - (t*x-y)//(n*t)
    # Compensate
    while x**n > y:
        x -= 1
    return x, x**n == y


pyint = long
pyint_0 = pyint(0)
pyint_1 = pyint(1)
makeinteger = lambda p: pyint.__new__(Integer, p)

@singleton
def makezero(p):
    obj = pyint.__new__(Integer, p)
    obj.is_zero = True
    obj.p = p
    obj.q = pyint_1
    objects.zero = obj
    return obj

@singleton
def makeone(p):
    obj = pyint.__new__(Integer, p)
    obj.is_one = True
    obj.p = p
    obj.q = pyint_1
    objects.one = obj
    return obj

@singleton
def makemone(p):
    obj = pyint.__new__(Integer, p)
    obj.p = p
    obj.q = pyint_1
    objects.mone = obj
    return obj

def makeinteger(p):
    obj = pyint.__new__(Integer, p)
    obj.p = p
    obj.q = pyint_1
    return obj

class Integer(Rational, pyint):

    is_integer = True
    is_zero = False
    is_one = False

    @memoizer_Integer
    def __new__(cls, p):
        if p==0: return makezero(p)
        if p==1: return makeone(p)
        if p==-1: return makemone(p)
        return makeinteger(p)

    make = staticmethod(makeinteger)

    @property
    def is_two(self):
        return self==2

    # relational methods

    def instance_compare(self, other):
        return pyint.__cmp__(self, other)

    def __eq__(self, other):
        if isinstance(other, bool):
            return False
        if isinstance(other,(int, long)):
            return pyint(self)==other
        other = sympify(other)
        if isinstance(other, Basic):
            if other.is_Integer:
                return not pyint.__cmp__(self, other)
            if other.is_Number:
                return NotImplemented
        return False

    __hash__ = pyint.__hash__

    def __ne__(self, other):
        other = sympify(other)
        if self is other:
            return False
        if isinstance(other, Basic):
            if other.is_Integer:
                return pyint.__cmp__(self, pyint(other))!=0
        elif isinstance(other, bool):
            return True
        return NotImplemented

    def __lt__(self, other):
        other = sympify(other)
        if self is other: return False
        if other.is_Integer:
            return pyint.__cmp__(self, pyint(other))==-1
        return NotImplemented

    def __le__(self, other):
        other = sympify(other)
        if self is other: return True
        if other.is_Integer:
            return pyint.__cmp__(self, pyint(other))<=0
        return NotImplemented

    def __gt__(self, other):
        other = sympify(other)
        if self is other: return False
        if other.is_Integer:
            return pyint.__cmp__(self, pyint(other))==1
        return NotImplemented

    def __ge__(self, other):
        other = sympify(other)
        if self is other: return True
        if other.is_Integer:
            return pyint.__cmp__(self, pyint(other))>=0
        return NotImplemented

    # converter methods

    __int__ = pyint.__int__
    __long__ = pyint.__long__
    __float__ = pyint.__float__

    def evalf(self):
        return classes.Float(pyint(self))

    # mathematical properties

    @property
    def is_even(self):
        return pyint.__mod__(self,2)==0

    @property
    def is_odd(self):
        return pyint.__mod__(self,2)==1

    @property
    def is_positive(self):
        return pyint.__cmp__(self, pyint_0)==1

    @property
    def is_negative(self):
        return pyint.__cmp__(self, pyint_0)==-1

    # algorithms

    @staticmethod
    def gcd(a, b):
        """
        Returns the Greatest Common Divisor, implementing Euclid's algorithm.
        """
        while a:
            a, b = b%a, a
        return b

    @staticmethod
    def factor_trial_division(n):
        """
        Factor any integer into a product of primes, 0, 1, and -1.
        Returns a dictionary {<prime: exponent>}.
        """
        if not n:
            return {0:1}
        factors = {}
        if n < 0:
            factors[-1] = 1
            n = -n
        if n==1:
            factors[1] = 1
            return factors
        d = 2
        while n % d == 0:
            try:
                factors[d] += 1
            except KeyError:
                factors[d] = 1
            n //= d
        d = 3
        while n > 1 and d*d <= n:
            if n % d:
                d += 2
            else:
                try:
                    factors[d] += 1
                except KeyError:
                    factors[d] = 1
                n //= d
        if n>1:
            try:
                factors[n] += 1
            except KeyError:
                factors[n] = 1
        return factors

    @staticmethod
    def collect_powers(seq_base_exp, exp=1):
        p = None
        d = {}
        for b,e in seq_base_exp:
            e = e * exp
            if p is None:
                p, q = e.p, e.q
                if p < 0:
                    sign = -1
                else:
                    sign = 1
            else:
                if e.p>0 and sign==-1:
                    sign = 1
                p = classes.Integer.gcd(abs(e.p), p)
                q = classes.Integer.gcd(e.q, q)
        c = classes.Fraction(sign*p, q)
        if c==1:
            return seq_base_exp, c
        r = []
        for b,e in seq_base_exp:
            r.append((b, e * exp / c))
        return r, c

    def __pos__(self):
        return self

    def __neg__(self):
        return Integer(pyint.__neg__(self))

    def __add__(self, other):
        other = sympify(other)
        if other.is_Integer:
            return Integer(pyint.__add__(self, other))
        return NotImplemented

    def __sub__(self, other):
        other = sympify(other)
        if other.is_Integer:
            return Integer(pyint.__sub__(self, other))
        return NotImplemented

    def __mul__(self, other):
        other = sympify(other)
        if other.is_Integer:
            return Integer(pyint.__mul__(self, other))
        return NotImplemented

    def __div__(self, other):
        other = sympify(other)
        if other.is_Integer:
            return classes.Fraction(self.p, other.p)
        return NotImplemented

    def __pow__(self, other):
        other = sympify(other)
        r = self.try_power(other)
        if r is not None:
            return r
        return NotImplemented

    #@memoizer_immutable_args('Integer.try_power')
    def try_power(self, other):
        if self.is_zero:
            if other.is_Number:
                if other.is_negative:
                    return objects.oo
                if other.is_positive:
                    return self
            if other.is_Infinity or other.is_ComplexInfinity:
                return self
            if other.is_NaN:
                return other
            return
        if self.is_one:
            return self
        if other.is_Integer:
            if other.is_one:
                return self
            if other.is_negative:
                return classes.Fraction(1, pyint.__pow__(self, -other.p))
            return Integer(pyint.__pow__(self, other))
        if other.is_Float:
            return self.as_Float ** other.as_Float
        if other.is_Fraction:
            if self==-1:
                if other.q==2:
                    return objects.I ** other.p
                return
            if self.is_negative:
                return (-1)**other * (-self)**other
            r, exact = integer_nthroot(self.p, other.q)
            if exact:
                if other.p < 0:
                    return classes.Fraction(1, r ** (-other.p))
                return Integer(r ** other.p)
            if other.is_negative:
                p = self.try_power(-other)
                if p is not None:
                    return 1/p
                return p
            factors = self.as_factors()
            f1 = 1
            f2 = 1
            r = Integer.collect_powers(factors, other)
            #print '>>>',self, other, r, factors
            for b,e in factors:
                # e = q + r such that q = p/other is integer (p=floor(e*other)) and abs(r)<1. 
                pn = other * e 
                p = pn.p // pn.q
                if p:
                    r = e - p / other
                    f1 *= b ** p
                    f2 *= b ** r
                else:
                    f2 *= b ** e
            if f1==1:
                return
            if f2.is_Pow and f1==f2.base:
                # avoid recursions like:
                # Sqrt(8) -> 2 * 2 ** (1/2) -> 2 ** (1+1/2) -> 2 ** (3/2) -> 8 ** (1/2) 
                return
            return f1 * classes.Pow(f2, other, normalized=False)
        if other.is_Infinity or other.is_ComplexInfinity:
            if self.is_one:
                return self
            if self.is_negative:
                return objects.nan
            return other
        if other.is_NaN:
            return other

    @singleton
    def as_factors(self):
        dp = Integer.factor_trial_division(self.p)
        eb = {}
        for (b,e) in dp.items():
            v = eb.get(e, None)
            if v is None:
                eb[e] = Integer(b)
            else:
                eb[e] = v * b
        if len(eb)>1 and eb.get(1)==1:
            del eb[1]
        return [(b,Integer(e)) for (e,b) in eb.iteritems()]

    # __r*__ methods are defined in methods.py

    def normalized_power(self, exp):
        # exp must be positive rational
        dp = Integer.factor_trial_division(self.p)
        eb = {}
        for (b,e) in dp.items():
            e = exp * e
            v = eb.get(e, None)
            if v is None:
                eb[e] = Integer(b)
            else:
                eb[e] = v * b
        if len(eb)>1 and eb.get(1)==1:
            del eb[1]        

        #print eb
