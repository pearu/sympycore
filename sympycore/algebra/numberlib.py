"""
This module implements "low-level" number types which may be used
by algebras to represent coefficients internally, for purely numerical
calculations, etc. In the interest of speed, the classes implemented
here have some quirks which make them unsuitable to be exposed
directly to (non-expert) users.

In particular, we want fractions to normalize back to Python ints
when they become integer-valued, and we want complex numbers to
normalize back to their real parts when the imaginary parts disappear.
This means code like

    a = mpq(2)
    b = mpq(3)
    a / b

should not be expected to work. Instead, the div() function can be used
to safely divide numbers (it checks for integers). However, +, - and *,
as well as positive integer powers, are always safe.

Powers, except when the exponent is a positive integer, should be
computed with the try_power() function which detects when the result is
not exact.

In addition to the number types mpq (rationals), mpf (floats) and mpc
(complexes), the extended_number type can be used to represent infinities
and indeterminate/undefined (nan) results.

Some issues:
* Rational hashing is not compatible with floats (however, mixing floats
  and rationals is generally not a good idea).
* Extended numbers are not fully handled yet.
* try_power does not yet know how to compute fractional powers
  (and square roots in particular)

"""
#
# Author: Fredrik Johansson
# Created: January 2008

import math

__all__ = ['mpq', 'mpf', 'mpc', 'div', 'int_root', 'try_power',
    'extended_number', 'nan', 'undefined', 'oo', 'moo', 'zoo']

from .primitive import PrimitiveAlgebra, NUMBER, SYMBOL
from .utils import get_object_by_name
from .utils import RedirectOperation

inttypes = (int, long)

#----------------------------------------------------------------------------#
#                                                                            #
#                              Rational numbers                              #
#                                                                            #
#----------------------------------------------------------------------------#

class mpq(tuple):
    __slots__ = []
    
    def __new__(cls, p, q=1, tnew=tuple.__new__):
        x, y = p, q
        while y:
            x, y = y, x % y
        if x != 1:
            p //= x
            q //= x
        if q == 1:
            return p
        return tnew(cls, (p, q))

    def as_primitive(self):
        p, q = self
        if p<0:
            return -(PrimitiveAlgebra(-p, head=NUMBER) / PrimitiveAlgebra(q, head=NUMBER))
        return PrimitiveAlgebra(p, head=NUMBER) / PrimitiveAlgebra(q, head=NUMBER)

    def __str__(self):
        return "(%i/%i)" % self

    def __repr__(self):
        return "mpq(%i, %i)" % (self[0], self[1])

    # not needed when __new__ normalizes to ints
    # __nonzero__
    # __eq__
    # __hash__

    def __cmp__(self, other):
        p, q = self
        if isinstance(other, inttypes):
            return p - q*other
        if isinstance(other, mpq):
            r, s = other
            return p*s - q*r
        return NotImplemented

    def __float__(self):
        p, q = self
        return float(p) / q

    def __neg__(self, tnew=tuple.__new__):
        p, q = self
        return tnew(mpq, (-p, q))

    def __pos__(self):
        return self

    def __abs__(self, tnew=tuple.__new__):
        p, q = self
        if p < 0:
            return tnew(mpq, (-p, q))
        return self

    def __add__(self, other, check=isinstance, inttypes=inttypes):
        p, q = self
        if check(other, inttypes):
            return mpq(p+q*other, q)
        if check(other, mpq):
            r, s = other
            return mpq(p*s+q*r, q*s)
        return NotImplemented

    __radd__ = __add__

    def __sub__(self, other, check=isinstance, inttypes=inttypes):
        p, q = self
        if check(other, inttypes):
            return mpq(p-q*other, q)
        if check(other, mpq):
            r, s = other
            return mpq(p*s - q*r, q*s)
        return NotImplemented

    def __rsub__(self, other, check=isinstance, inttypes=inttypes):
        p, q = self
        if check(other, inttypes):
            return mpq(q*other-p, q)
        return NotImplemented

    def __mul__(self, other, check=isinstance, inttypes=inttypes):
        p, q = self
        if check(other, inttypes):
            return mpq(p*other, q)
        if check(other, mpq):
            r, s = other
            return mpq(p*r, q*s)
        return NotImplemented

    __rmul__ = __mul__

    def __div__(self, other, check=isinstance, inttypes=inttypes):
        p, q = self
        if check(other, inttypes):
            if not other:
                return cmp(p, 0) * oo
            return mpq(p, q*other)
        if check(other, mpq):
            r, s = other
            return mpq(p*s, q*r)
        return NotImplemented

    def __rdiv__(self, other, check=isinstance, inttypes=inttypes):
        p, q = self
        if check(other, inttypes):
            return mpq(q*other, p)
        return NotImplemented

    def __pow__(self, n):
        assert isinstance(n, inttypes)
        p, q = self
        if n >= 0:
            return mpq(p**n, q**n)
        else:
            return mpq(q**n, p**n)


#----------------------------------------------------------------------------#
#                                                                            #
#                          Floating-point numbers                            #
#                                                                            #
#----------------------------------------------------------------------------#

from mpmath.lib import from_int, from_rational, to_str, fadd, fsub, fmul, \
  round_half_even, from_float, to_float, to_int, fpow, from_str, feq, \
  fhash, fcmp, fdiv

rounding = round_half_even

class mpf(object):

    __slots__ = ['val', 'prec']

    def __init__(self, val, prec=53):
        self.prec = prec
        if type(val) != tuple:
            val = self.convert(val)
        self.val = val

    def convert(self, x):
        if isinstance(x, mpf):
            return x.val
        if isinstance(x, inttypes):
            return from_int(x, self.prec, rounding)
        if isinstance(x, mpq):
            return from_rational(x[0], x[1], self.prec, rounding)
        if isinstance(x, float):
            return from_float(x, self.prec, rounding)
        if isinstance(x, basestring):
            return from_str(x, self.prec, rounding)
        return NotImplemented

    def __str__(self):
        return to_str(self.val, int((self.prec/3.33) - 3))

    def __repr__(self):
        return "mpf(%s)" % to_str(self.val, int((self.prec/3.33)))

    def __int__(self): return to_int(self.val)
    def __float__(self): return to_float(self.val)
    def __hash__(self): return fhash(self.val)
    def __pos__(self): return self
    def __neg__(self): return mpf(fneg(self.val), self.prec)

    # XXX: these should handle rationals exactly
    def __eq__(self, other):
        other = self.convert(other)
        if other is NotImplemented:
            return other
        return feq(self.val, other)

    def __cmp__(self, other):
        other = self.convert(other)
        if other is NotImplemented:
            return other
        return fcmp(self.val, other)

    def __add__(self, other):
        other = self.convert(other)
        if other is NotImplemented:
            return other
        return mpf(fadd(self.val, other, self.prec, rounding), self.prec)

    __radd__ = __add__

    def __sub__(self, other):
        other = self.convert(other)
        if other is NotImplemented:
            return other
        return mpf(fsub(self.val, other, self.prec, rounding), self.prec)

    def __rsub__(self, other):
        other = self.convert(other)
        if other is NotImplemented:
            return other
        return mpf(fsub(other, self.val, self.prec, rounding), self.prec)

    def __mul__(self, other):
        other = self.convert(other)
        if other is NotImplemented:
            return other
        return mpf(fmul(self.val, other, self.prec, rounding), self.prec)

    __rmul__ = __mul__

    def __div__(self, other):
        # XXX: check for divide by zero
        other = self.convert(other)
        if other is NotImplemented:
            return other
        return mpf(fdiv(self.val, other, self.prec, rounding), self.prec)

    def __rdiv__(self, other):
        # XXX: check for divide by zero
        other = self.convert(other)
        if other is NotImplemented:
            return other
        return mpf(fdiv(other, self.val, self.prec, rounding), self.prec)

    def __pow__(self, n):
        # XXX: check for divide by zero
        assert isinstance(n, inttypes)
        return mpf(fpow(self.val, n, self.prec, rounding))


#----------------------------------------------------------------------------#
#                                                                            #
#                              Complex numbers                               #
#                                                                            #
#----------------------------------------------------------------------------#

def innerstr(x):
    if isinstance(x, mpq):
        return "%s/%s" % x
    return str(x)


class mpc(object):

    __slots__ = ['real', 'imag']

    def __new__(cls, real, imag=0):
        if not imag:
            return real
        self = object.__new__(mpc)
        self.real = real
        self.imag = imag
        return self

    def __repr__(self):
        return "mpc(%r, %r)" % (self.real, self.imag)

    def __hash__(self):
        return hash((self.real, self.imag))

    def __str__(self):
        re, im = self.real, self.imag
        if not re:
            if im == 1: return "I"
            if im == -1: return "-I"
            return str(self.imag) + "*I"
        restr = innerstr(self.real)
        if im == 1: return "(%s + I)" % restr
        if im == -1: return "(%s - I)" % restr
        if im > 0: return "(%s + %s*I)" % (restr, innerstr(self.imag))
        if im < 0: return "(%s - %s*I)" % (restr, innerstr(-self.imag))

    def as_primitive(self):
        re, im = self.real, self.imag
        if re < 0: 
            r = -PrimitiveAlgebra(-self.real)
        else:
            r = PrimitiveAlgebra(self.real)
        if im < 0:
            i = -PrimitiveAlgebra(-self.imag)
            ni = PrimitiveAlgebra(-self.imag)
        else:
            i = PrimitiveAlgebra(self.imag)
        I = PrimitiveAlgebra(mpc(0,1), head=NUMBER)
        if not re:
            if im == 1: return I
            if im == -1: return -I
            return i * I
        if im == 1: return r + I
        if im == -1: return r - I
        if im < 0:
            return r - ni * I
        else:
            return r + i * I
    
    def __eq__(self, other):
        if isinstance(other, mpc):
            return self.real == other.real and self.imag == other.imag
        if isinstance(other, complex):
            return self.real, self.imag == self.convert(other)
        return False

    def convert(self, x):
        if isinstance(x, mpc):
            return x.real, x.imag
        if isinstance(x, complex):
            return mpc(mpf(x.real), mpf(x.imag))
        if isinstance(x, extended_number):
            return NotImplemented, 0
        return x, 0

    def __pos__(self): return self
    def __neg__(self): return mpc(-self.real, -self.imag)

    def __add__(self, other):
        a, b = self.real, self.imag
        c, d = self.convert(other)
        if c is NotImplemented:
            return c
        return mpc(a+c, b+d)

    __radd__ = __add__

    def __sub__(self, other):
        a, b = self.real, self.imag
        c, d = self.convert(other)
        if c is NotImplemented:
            return c
        return mpc(a-c, b-d)

    def __rsub__(self, other):
        a, b = self.real, self.imag
        c, d = self.convert(other)
        if c is NotImplemented:
            return c
        return mpc(c-a, d-b)

    def __mul__(self, other):
        a, b = self.real, self.imag
        c, d = self.convert(other)
        if c is NotImplemented:
            return c
        return mpc(a*c-b*d, b*c+a*d)

    __rmul__ = __mul__

    def __div__(self, other):
        a, b = self.real, self.imag
        c, d = self.convert(other)
        if c is NotImplemented:
            return c
        mag = c*c + d*d
        re = div(a*c+b*d, mag)
        im = div(b*c-a*d, mag)
        return mpc(re, im)

    def __rdiv__(self, other):
        c, d = self.real, self.imag
        a, b = self.convert(other)
        if a is NotImplemented:
            return a
        mag = c*c + d*d
        re = div(a*c+b*d, mag)
        im = div(b*c-a*d, mag)
        return mpc(re, im)

    def __pow__(self, n):
        assert isinstance(n, (int, long))
        if not n: return 1
        if n == 1: return self
        if n == 2: return self * self
        if n < 0:
            return (1 / self) ** (-n)
        a, b = self.real, self.imag
        if not a:
            case = n % 4
            if case == 0: return b**n
            if case == 1: return mpc(0, b**n)
            if case == 2: return -(b**n)
            if case == 3: return mpc(0, -b**n)
        c, d = 1, 0
        while n:
            if n & 1:
                c, d = a*c-b*d, b*c+a*d
                n -= 1
            a, b = a*a-b*b, 2*a*b
            n //= 2
        return mpc(c, d)


#----------------------------------------------------------------------------#
#                                                                            #
#                             Extended numbers                               #
#                                                                            #
#----------------------------------------------------------------------------#

def as_direction(x):
    if isinstance(x, (mpc, complex)):
        return mpc(cmp(x.real, 0), cmp(x.imag, 0))
    return cmp(x, 0)

cmp_error = "no ordering relation is defined for complex numbers"

class extended_number:

    def __init__(self, infinite, direction):
        self.infinite = infinite
        self.direction = direction

    def __repr__(self):
        if not self.infinite: return 'undefined'
        if not self.direction: return 'zoo'
        if self.direction == 1: return 'oo'
        if self.direction == -1: return '-oo'
        return "%s*oo" % self.direction

    def __nonzero__(self):
        if get_object_by_name('redirect_operation', 'ignore_redirection')=='ignore_redirection':
            return True
        raise RedirectOperation(self)

    def __abs__(self):
        if not self.infinite: return self
        return oo

    def __eq__(self, other):
        if isinstance(other, extended_number):
            return self.infinite == other.infinite and \
                self.direction == other.direction
        return False

    def __lt__(self, other):
        if self.direction == 0:
            return False
        if self.direction not in (1, -1):
            raise TypeError(cmp_error)
        if isinstance(other, extended_number):
            if other.direction not in (1, -1):
                raise TypeError(cmp_error)
            return (self.direction, other.direction) == (-1, 1)
        if isinstance(other, (complex, mpc)):
            raise TypeError(cmp_error)
        return self.direction == -1

    def __gt__(self, other):
        if self.direction == 0:
            return False
        if self.direction not in (1, -1):
            raise TypeError(cmp_error)
        if isinstance(other, extended_number):
            if other.direction not in (1, -1):
                raise TypeError(cmp_error)
            return (self.direction, other.direction) == (1, -1)
        if isinstance(other, (complex, mpc)):
            raise TypeError(cmp_error)
        return self.direction == 1

    def __le__(self, other):
        return self == other or self.__lt__(other)

    def __ge__(self, other):
        return self == other or self.__gt__(other)

    def __hash__(self):
        return hash(('extended_number', infinite, direction))

    def __neg__(self):
        return extended_number(self.infinite, -self.direction)

    def __pos__(self):
        return self

    def __add__(self, other):
        if isinstance(other, extended_number):
            if self.direction != other.direction:
                return nan
            return extended_number(self.infinite*other.infinite, self.direction)
        if not isinstance(other, numbertypes):
            return NotImplemented
        return self

    __radd__ = __add__

    def __sub__(self, other):
        return self + (-other)

    def __rsub__(self, other):
        return (-self) + other

    def __mul__(self, other):
        if isinstance(other, extended_number):
            return extended_number(self.infinite*other.infinite,
                                   as_direction(self.direction*other.direction))
        if not isinstance(other, numbertypes):
            return NotImplemented
        if not other:
            return undefined
        return extended_number(self.infinite, as_direction(self.direction*other))

    __rmul__ = __mul__


undefined = nan = extended_number(0, 0)
oo = extended_number(1, 1)
moo = extended_number(1, -1)
zoo = extended_number(1, 0)
numbertypes = (int, long, float, complex, mpq, mpf, mpc, extended_number)


#----------------------------------------------------------------------------#
#                                                                            #
#                            Interface functions                             #
#                                                                            #
#----------------------------------------------------------------------------#

def div(a, b):
    """Safely compute a/b (if a or b is an integer, this function makes sure
    to convert it to a rational)."""
    if isinstance(b, inttypes):
        return mpq(1,b) * a
    return a / b

def int_root(y, n):
    """
    Given integers y and n, return a tuple containing x = floor(y**(1/n))
    and a boolean indicating whether x**n == y exactly.
    """
    if y < 0: raise ValueError, "y must not be negative"
    if n < 1: raise ValueError, "n must be positive"
    if y in (0, 1): return y, True
    if n == 1: return y, True
    # Get initial estimate for Newton's method. Care must be taken to
    # avoid overflow
    try:
        guess = int(y ** (1./n)+0.5)
    except OverflowError:
        try:
            guess = int(math.exp(math.log(y)/n)+0.5)
        except OverflowError:
            guess = 1 << int(math.log(y, 2)/n)
    # Newton iteration
    xprev, x = -1, guess
    while abs(x - xprev) > 1:
        t = x**(n-1)
        xprev, x = x, x - (t*x-y)//(n*t)
    # Compensate
    while x**n > y:
        x -= 1
    return x, x**n == y

def try_power(x, y):
    """
    Attempt to compute x**y where x and y must be of the types int,
    long, mpq, mpf, mpc or extended_number. The function returns

      z, symbolic

    where z is a number (i.e. a complex rational) and symbolic is
    either None (if z is the exact answer) or a pair (b, e) representing
    the symbolic product b**e. For example, this function should return:

      try_power(3, 2) --> (9, None)
      try_power(2, 1/2) --> (1, (2, 1/2))
      try_power(45, 1/2) --> (3, (5, 1/2))

    """
    if isinstance(x, extended_number) or isinstance(y, extended_number):
        raise NotImplementedError
    if isinstance(y, inttypes):
        if y >= 0: return x**y, None
        if not x: return oo, None
        if isinstance(x, inttypes): return mpq(1, x**(-y)), None
        if isinstance(x, (mpq, mpf, mpc)): return x**y, None
    if isinstance(x, inttypes) and isinstance(y, mpq):
        p, q = y
        r, exact = int_root(abs(x), q)
        if exact:
            if p > 0:
                g = r**p
            else:
                g = mpq(1, r**(-p))
            if x > 0:
                return g, None
            else:
                return mpc(0, g), None
    return 1, (x, y)


