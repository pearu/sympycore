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

    a = Fraction(2)
    b = Fraction(3)
    a / b

should not be expected to work. Instead, the div() function can be used
to safely divide numbers (it checks for integers). However, +, - and *,
as well as positive integer powers, are always safe.

Powers, except when the exponent is a positive integer, should be
computed with the try_power() function which detects when the result is
not exact.

In addition to the number types Fraction (rationals), Float (floats) and Complex
(complexes), the ExtendedNumber type can be used to represent infinities
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

__all__ = ['Fraction', 'Float', 'Complex', 'div', 'int_root', 'try_power',
    'ExtendedNumber', 'nan', 'undefined', 'oo', 'moo', 'zoo']

from ..basealgebra.primitive import PrimitiveAlgebra, NUMBER, SYMBOL
from ..basealgebra.utils import get_object_by_name
from ..basealgebra.utils import RedirectOperation

inttypes = (int, long)

#----------------------------------------------------------------------------#
#                                                                            #
#                              Rational numbers                              #
#                                                                            #
#----------------------------------------------------------------------------#

class Fraction(tuple):
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
        return "Fraction(%r, %r)" % (self[0], self[1])

    # not needed when __new__ normalizes to ints
    # __nonzero__
    # __eq__
    # __hash__

    def __cmp__(self, other):
        p, q = self
        if isinstance(other, inttypes):
            return cmp(p - q*other, 0)
        if isinstance(other, Fraction):
            r, s = other
            return cmp(p*s - q*r, 0)
        return NotImplemented

    def __float__(self):
        p, q = self
        return float(p) / q

    def __int__(self):
        p, q = self
        return p // q

    def __neg__(self, tnew=tuple.__new__):
        p, q = self
        return tnew(Fraction, (-p, q))

    def __pos__(self):
        return self

    def __abs__(self, tnew=tuple.__new__):
        p, q = self
        if p < 0:
            return tnew(Fraction, (-p, q))
        return self

    def __add__(self, other):
        p, q = self
        if isinstance(other, inttypes):
            return Fraction(p+q*other, q)
        if isinstance(other, Fraction):
            r, s = other
            return Fraction(p*s+q*r, q*s)
        return NotImplemented

    __radd__ = __add__

    def __sub__(self, other):
        p, q = self
        if isinstance(other, inttypes):
            return Fraction(p-q*other, q)
        if isinstance(other, Fraction):
            r, s = other
            return Fraction(p*s - q*r, q*s)
        return NotImplemented

    def __rsub__(self, other):
        p, q = self
        if isinstance(other, inttypes):
            return Fraction(q*other-p, q)
        return NotImplemented

    def __mul__(self, other):
        p, q = self
        if isinstance(other, inttypes):
            return Fraction(p*other, q)
        if isinstance(other, Fraction):
            r, s = other
            return Fraction(p*r, q*s)
        return NotImplemented

    __rmul__ = __mul__

    def __div__(self, other):
        p, q = self
        if isinstance(other, inttypes):
            if not other:
                return cmp(p, 0) * oo
            return Fraction(p, q*other)
        if isinstance(other, Fraction):
            r, s = other
            return Fraction(p*s, q*r)
        return NotImplemented

    def __rdiv__(self, other):
        p, q = self
        if isinstance(other, inttypes):
            return Fraction(q*other, p)
        return NotImplemented

    def __floordiv__(a, b):
        return int(a / b)

    def __rfloordiv__(a, b):
        return int(b / a)

    def __mod__(a, b):
        return a - (a//b)*b

    def __rmod__(a, b):
        return b - (b//a)*a

    def __divmod__(a, b):
        return (a-a%b)/b, a%b

    def __rdivmod__(a, b):
        return (b-b%a)/a, b%a

    def __pow__(self, n):
        assert isinstance(n, inttypes)
        p, q = self
        if n >= 0:
            return Fraction(p**n, q**n)
        else:
            return Fraction(q**-n, p**-n)


#----------------------------------------------------------------------------#
#                                                                            #
#                          Floating-point numbers                            #
#                                                                            #
#----------------------------------------------------------------------------#

from mpmath.lib import from_int, from_rational, to_str, fadd, fsub, fmul, \
  round_half_even, from_float, to_float, to_int, fpow, from_str, feq, \
  fhash, fcmp, fdiv, fabs, fcabs, fneg

rounding = round_half_even

class Float(object):

    __slots__ = ['val', 'prec']

    def __init__(self, val, prec=53):
        self.prec = prec
        if type(val) != tuple:
            val = self.convert(val)
        self.val = val

    def convert(self, x):
        if isinstance(x, Float):
            return x.val
        if isinstance(x, inttypes):
            return from_int(x, self.prec, rounding)
        if isinstance(x, Fraction):
            return from_rational(x[0], x[1], self.prec, rounding)
        if isinstance(x, float):
            return from_float(x, self.prec, rounding)
        if isinstance(x, basestring):
            return from_str(x, self.prec, rounding)
        return NotImplemented

    def __str__(self):
        return to_str(self.val, int((self.prec/3.33) - 3))

    def __repr__(self):
        return "Float(%s)" % to_str(self.val, int((self.prec/3.33)))

    def __int__(self): return to_int(self.val)
    def __float__(self): return to_float(self.val)
    def __hash__(self): return fhash(self.val)
    def __pos__(self): return self
    def __neg__(self): return Float(fneg(self.val), self.prec)
    def __abs__(self): return Float(fabs(self.val), self.prec)

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
        return Float(fadd(self.val, other, self.prec, rounding), self.prec)

    __radd__ = __add__

    def __sub__(self, other):
        other = self.convert(other)
        if other is NotImplemented:
            return other
        return Float(fsub(self.val, other, self.prec, rounding), self.prec)

    def __rsub__(self, other):
        other = self.convert(other)
        if other is NotImplemented:
            return other
        return Float(fsub(other, self.val, self.prec, rounding), self.prec)

    def __mul__(self, other):
        other = self.convert(other)
        if other is NotImplemented:
            return other
        return Float(fmul(self.val, other, self.prec, rounding), self.prec)

    __rmul__ = __mul__

    def __div__(self, other):
        # XXX: check for divide by zero
        other = self.convert(other)
        if other is NotImplemented:
            return other
        return Float(fdiv(self.val, other, self.prec, rounding), self.prec)

    def __rdiv__(self, other):
        # XXX: check for divide by zero
        other = self.convert(other)
        if other is NotImplemented:
            return other
        return Float(fdiv(other, self.val, self.prec, rounding), self.prec)

    def __pow__(self, n):
        # XXX: check for divide by zero
        assert isinstance(n, inttypes)
        return Float(fpow(self.val, n, self.prec, rounding), self.prec)


#----------------------------------------------------------------------------#
#                                                                            #
#                              Complex numbers                               #
#                                                                            #
#----------------------------------------------------------------------------#

def innerstr(x):
    if isinstance(x, Fraction):
        return "%s/%s" % x
    return str(x)


class Complex(object):

    __slots__ = ['real', 'imag']

    def __new__(cls, real, imag=0):
        if not imag:
            return real
        self = object.__new__(Complex)
        self.real = real
        self.imag = imag
        return self

    def __repr__(self):
        return "Complex(%r, %r)" % (self.real, self.imag)

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
        I = PrimitiveAlgebra(Complex(0,1), head=NUMBER)
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
        if isinstance(other, Complex):
            return self.real == other.real and self.imag == other.imag
        if isinstance(other, complex):
            return self.real, self.imag == self.convert(other)
        return False

    def convert(self, x):
        if isinstance(x, Complex):
            return x.real, x.imag
        if isinstance(x, complex):
            return Complex(Float(x.real), Float(x.imag))
        if isinstance(x, ExtendedNumber):
            return NotImplemented, 0
        return x, 0

    def __pos__(self): return self
    def __neg__(self): return Complex(-self.real, -self.imag)

    def __abs__(self):
        if not self.real:
            return abs(self.imag)
        if isinstance(self.real, Float) and isinstance(self.imag, Float):
            return Float(fcabs(self.real.val, self.imag.val,
                self.real.prec, rounding), self.real.prec)
        raise NotImplementedError

    def __add__(self, other):
        a, b = self.real, self.imag
        c, d = self.convert(other)
        if c is NotImplemented:
            return c
        return Complex(a+c, b+d)

    __radd__ = __add__

    def __sub__(self, other):
        a, b = self.real, self.imag
        c, d = self.convert(other)
        if c is NotImplemented:
            return c
        return Complex(a-c, b-d)

    def __rsub__(self, other):
        a, b = self.real, self.imag
        c, d = self.convert(other)
        if c is NotImplemented:
            return c
        return Complex(c-a, d-b)

    def __mul__(self, other):
        a, b = self.real, self.imag
        c, d = self.convert(other)
        if c is NotImplemented:
            return c
        return Complex(a*c-b*d, b*c+a*d)

    __rmul__ = __mul__

    def __div__(self, other):
        a, b = self.real, self.imag
        c, d = self.convert(other)
        if c is NotImplemented:
            return c
        mag = c*c + d*d
        re = div(a*c+b*d, mag)
        im = div(b*c-a*d, mag)
        return Complex(re, im)

    def __rdiv__(self, other):
        c, d = self.real, self.imag
        a, b = self.convert(other)
        if a is NotImplemented:
            return a
        mag = c*c + d*d
        re = div(a*c+b*d, mag)
        im = div(b*c-a*d, mag)
        return Complex(re, im)

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
            if case == 1: return Complex(0, b**n)
            if case == 2: return -(b**n)
            if case == 3: return Complex(0, -b**n)
        m = 1
        if isinstance(a, Fraction):
            if isinstance(b, Fraction):
                m = (a[1] * b[1]) ** n
                a, b = a[0]*b[1], a[1]*b[0]
            elif isinstance(b, inttypes):
                m = a[1] ** n
                a, b = a[0], a[1]*b
        elif isinstance(b, Fraction):
            if isinstance(a, inttypes):
                m = b[1] ** n
                a, b = a*b[1], b[0]
        c, d = 1, 0
        while n:
            if n & 1:
                c, d = a*c-b*d, b*c+a*d
                n -= 1
            a, b = a*a-b*b, 2*a*b
            n //= 2
        if m==1:
            return Complex(c, d)
        return Complex(div(c, m), div(d, m))

#----------------------------------------------------------------------------#
#                                                                            #
#                             Extended numbers                               #
#                                                                            #
#----------------------------------------------------------------------------#

def as_direction(x):
    if isinstance(x, (Complex, complex)):
        return Complex(cmp(x.real, 0), cmp(x.imag, 0))
    return cmp(x, 0)

cmp_error = "no ordering relation is defined for complex numbers"

class ExtendedNumber:

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
        if isinstance(other, ExtendedNumber):
            return self.infinite == other.infinite and \
                self.direction == other.direction
        return False

    def __lt__(self, other):
        if self.direction == 0:
            return False
        if self.direction not in (1, -1):
            raise TypeError(cmp_error)
        if isinstance(other, ExtendedNumber):
            if other.direction not in (1, -1):
                raise TypeError(cmp_error)
            return (self.direction, other.direction) == (-1, 1)
        if isinstance(other, (complex, Complex)):
            raise TypeError(cmp_error)
        return self.direction == -1

    def __gt__(self, other):
        if self.direction == 0:
            return False
        if self.direction not in (1, -1):
            raise TypeError(cmp_error)
        if isinstance(other, ExtendedNumber):
            if other.direction not in (1, -1):
                raise TypeError(cmp_error)
            return (self.direction, other.direction) == (1, -1)
        if isinstance(other, (complex, Complex)):
            raise TypeError(cmp_error)
        return self.direction == 1

    def __le__(self, other):
        return self == other or self.__lt__(other)

    def __ge__(self, other):
        return self == other or self.__gt__(other)

    def __hash__(self):
        return hash(('ExtendedNumber', self.infinite, self.direction))

    def __neg__(self):
        return ExtendedNumber(self.infinite, -self.direction)

    def __pos__(self):
        return self

    def __add__(self, other):
        if isinstance(other, ExtendedNumber):
            if self.direction != other.direction:
                return nan
            return ExtendedNumber(self.infinite*other.infinite, self.direction)
        if not isinstance(other, numbertypes):
            return NotImplemented
        return self

    __radd__ = __add__

    def __sub__(self, other):
        return self + (-other)

    def __rsub__(self, other):
        return (-self) + other

    def __mul__(self, other):
        if isinstance(other, ExtendedNumber):
            return ExtendedNumber(self.infinite*other.infinite,
                                   as_direction(self.direction*other.direction))
        if not isinstance(other, numbertypes):
            return NotImplemented
        if not other:
            return undefined
        return ExtendedNumber(self.infinite, as_direction(self.direction*other))

    __rmul__ = __mul__


undefined = nan = ExtendedNumber(0, 0)
oo = ExtendedNumber(1, 1)
moo = ExtendedNumber(1, -1)
zoo = ExtendedNumber(1, 0)
numbertypes = (int, long, float, complex, Fraction, Float, Complex, ExtendedNumber)


#----------------------------------------------------------------------------#
#                                                                            #
#                            Interface functions                             #
#                                                                            #
#----------------------------------------------------------------------------#

def div(a, b):
    """Safely compute a/b (if a or b is an integer, this function makes sure
    to convert it to a rational)."""
    if isinstance(b, inttypes):
        return Fraction(1,b) * a
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
    long, Fraction, Float, Complex or ExtendedNumber. The function returns

      z, symbolic

    where z is a number (i.e. a complex rational) and symbolic is a list
    of (b, e) pairs representing symbolic factors b**e.

      try_power(3, 2) --> (9, [])
      try_power(2, 1/2) --> (1, [(2, 1/2)])
      try_power(45, 1/2) --> (3, [(5, 1/2)])

    """
    if isinstance(x, ExtendedNumber) or isinstance(y, ExtendedNumber):
        if x == undefined or y == undefined:
            return undefined, []
        if x.infinite and isinstance(y, (int, long, Fraction, Float)):
            if y == 0: return undefined, []
            if y < 0: return 0, []
            if y > 0:
                if not x.direction:
                    return x, []
                z, sym = try_power(x.direction, y)
                return ExtendedNumber(1, z), sym
        raise NotImplementedError
    if isinstance(y, inttypes):
        if y >= 0: return x**y, []
        if not x: return oo, []
        if isinstance(x, inttypes):
            return Fraction(1, x**(-y)), []
        if isinstance(x, (Fraction, Float, Complex)):
            return x**y, []
    if isinstance(x, inttypes) and isinstance(y, Fraction):
        p, q = y
        r, exact = int_root(abs(x), q)
        if exact:
            if p > 0:
                g = r**p
            else:
                g = Fraction(1, r**(-p))
            if x > 0:
                return g, []
            else:
                return Complex(0, g), []
    if isinstance(x, Fraction) and isinstance(y, Fraction):
        a, b = x
        r, rsym = try_power(a, y)
        s, ssym = try_power(b, y)
        ssym = [(b, -e) for b, e in ssym]
        return (div(r,s), rsym + ssym)
    return 1, [(x, y)]


