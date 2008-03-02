"""Provides low-level numbers support.

This module implements "low-level" number types which may be used
by algebras to represent coefficients internally, for purely numerical
calculations, etc. In the interest of speed, the classes implemented
here have some quirks which make them unsuitable to be exposed
directly to (non-expert) users.

In addition to the number types FractionTuple (for rationals), Float
(floats) and Complex (complexes), the Infinity (defined in
infinity.py) type can be used to represent infinities and
indeterminate/undefined (nan) results.

Important notes:

FractionTuples are more of a kind of tuple specialized for representing
fractions, than a user-friendly rational number type. The goal is to
make hashing, equality testing and instance creation as fast as
possible.

  * FractionTuple.__init__ does *not* validate its input.

  * A FractionTuple instance *should only* be created from a fully
    normalized (p, q) pair and p/q *should not* be integer-valued.

  * To safely create a fraction from two integers, use the function
    normalized_fraction().

  * Arithmetic operations on FractionTuples automatically normalize back
    to Python ints when the results are integer valued.

Note that ``Fraction(2)/Fraction(3)`` does *not* work as expected; it
does the same thing as ``2/3`` in Python. To perform safe division,
use the div function provided by this module instead.

Fractions can be compared with Python ints, but cannot be (correctly)
compared with Python floats. If you need to mix approximate and
exact fractions, use the Float class instead.

Powers, except when the exponent is a positive integer, should be
computed with the ``try_power()`` function which detects when the
result is not exact.

In a similar manner to how integer-valued rationals become Python
ints, complex numbers automatically normalize to their real parts when
they become real.
"""
#
# Author: Fredrik Johansson
# Created: January 2008

import math

from . import mpmath

__docformat__ = "restructuredtext"
__all__ = ['FractionTuple', 'Float', 'Complex', 'div', 'int_root', 'try_power',
           'normalized_fraction', 'setdps', 'getdps']

from ..utils import str_SUM, str_PRODUCT, str_POWER, str_APPLY, str_SYMBOL, str_NUMBER
from ..basealgebra.primitive import PrimitiveAlgebra, NUMBER, SYMBOL

inttypes = (int, long)

#----------------------------------------------------------------------------#
#                                                                            #
#                              Rational numbers                              #
#                                                                            #
#----------------------------------------------------------------------------#

def normalized_fraction(p, q=1):
    """ Return a normalized fraction.
    """
    x, y = p, q
    while y:
        x, y = y, x % y
    if x != 1:
        p //= x
        q //= x
    if q == 1:
        return p
    return FractionTuple((p, q))

class FractionTuple(tuple):
    """ Represents a fraction.
    """

    # These methods are inherited directly from tuple for speed. This works
    # as long as all FractionTuples are normalized:
    # __new__/__init__
    # __nonzero__
    # __eq__
    # __hash__

    # These methods are generated and defined in methods.py:
    # __add__, __sub__, __rsub__, __mul__, __div__, __rdiv__, __pow__
    # __lt__, __le__, __gt__, __ge__
    
    __slots__ = []

    def __mpfval__(self):
        p, q = self
        return from_rational(p, q, getprec(), round_half_even)

    def as_primitive(self):
        p, q = self
        if p<0:
            return -(PrimitiveAlgebra(-p, head=NUMBER) / PrimitiveAlgebra(q, head=NUMBER))
        return PrimitiveAlgebra(p, head=NUMBER) / PrimitiveAlgebra(q, head=NUMBER)

    def to_str_data(self,sort=True):
        if self[0]<0:
            return str_SUM, str(self)
        return str_PRODUCT, str(self)

    def __str__(self):
        return "%i/%i" % self

    def __repr__(self):
        return "FractionTuple((%r, %r))" % (self)

    def __float__(self):
        p, q = self
        return float(p) / q

    def __int__(self):
        p, q = self
        return p // q

    def __neg__(self):
        p, q = self
        return FractionTuple((-p, q))

    def __pos__(self):
        return self

    def __abs__(self):
        p, q = self
        if p < 0:
            return FractionTuple((-p, q))
        return self

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

    def __rpow__(a, b):
        z, sym = try_power(b, a)
        if not sym:
            return z
        return NotImplemented

#----------------------------------------------------------------------------#
#                                                                            #
#                          Floating-point numbers                            #
#                                                                            #
#----------------------------------------------------------------------------#

from .mpmath.lib import from_int, from_rational, to_str, fadd, fsub, fmul, \
  round_half_even, from_float, to_float, to_int, fpow, from_str, feq, \
  fhash, fcmp, fdiv, fabs, fcabs, fneg, fnan, flog, fexp, fpi, fcos, fsin, \
  fone, fgamma, fzero, fsqrt

from .mpmath import mpf, mpc

Float = mpf

def mpf_to_str_data(self,sort=True):
    if self < 0:
        return str_SUM, str(self)
    return str_NUMBER, str(self)

mpf.to_str_data = mpf_to_str_data

rounding = round_half_even

def getdps():
    return mpf.dps

def setdps(n):
    p = mpf.dps
    mpf.dps = int(n)
    return p

def getprec():
    return mpf.prec


#----------------------------------------------------------------------------#
#                                                                            #
#                              Complex numbers                               #
#                                                                            #
#----------------------------------------------------------------------------#

def innerstr(x):
    if isinstance(x, FractionTuple):
        return "%s/%s" % x
    return str(x)


class Complex(object):
    """ Represents complex number.

    The integer power of a complex number is computed using
    `exponentiation by squaring`__ method.
    
    __ http://en.wikipedia.org/wiki/Exponentiation_by_squaring
    """

    __slots__ = ['real', 'imag']

    def __new__(cls, real, imag=0):
        if imag==0:
            return real
        self = object.__new__(Complex)
        self.real = real
        self.imag = imag
        return self

    def __repr__(self):
        return "Complex(%r, %r)" % (self.real, self.imag)

    def __hash__(self):
        return hash((self.real, self.imag))

    def __mpcval__(self):
        return Float(self.real), Float(self.imag)

    def to_str_data(self,sort=True):
        re, im = self.real, self.imag
        if re==0:
            if im == 1: return str_SYMBOL,"I"
            if im == -1: return str_SUM, "-I"
            return str_PRODUCT, str(self.imag) + "*I"
        restr = innerstr(self.real)
        if im == 1: return str_SUM, "%s + I" % restr
        if im == -1: return str_SUM, "%s - I" % restr
        if im > 0: return str_SUM, "%s + %s*I" % (restr, innerstr(self.imag))
        if im < 0: return str_SUM, "%s - %s*I" % (restr, innerstr(-self.imag))
        raise NotImplementedError(`self`)

    def __str__(self):
        return self.to_str_data()[1]

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
        if re==0:
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
            if self.real != Float(other.real):
                return False
            return self.imag == Float(other.imag)
        return False

    def __pos__(self): return self
    def __neg__(self): return Complex(-self.real, -self.imag)

    def __abs__(self):
        if self.real==0:
            return abs(self.imag)
        if isinstance(self.real, Float) and isinstance(self.imag, Float):
            return abs(mpmath.mpc(self.real, self.imag))
        m2 = self.real**2 + self.imag**2
        if isinstance(m2, (int, long)):
            m,flag = int_root(m2,2)
            if flag:
                return m
        if isinstance(m2, FractionTuple):
            p,fp = int_root(m2[0],2)
            q,fq = int_root(m2[1],2)
            if fp and fq:
                return FractionTuple((p,q))
        if isinstance(m2, (float, Float)):
            return m2 ** 0.5
        raise NotImplementedError('abs(%r)' % (self))


#----------------------------------------------------------------------------#
#                                                                            #
#                            Interface functions                             #
#                                                                            #
#----------------------------------------------------------------------------#

numbertypes = (int, long, float, complex, FractionTuple, Float, Complex)
realtypes = (int, long, float, FractionTuple, Float)
complextypes = (complex, Complex)

def div(a, b):
    """Safely compute a/b.

    If a or b is an integer, this function makes sure to convert it to
    a rational.
    """
    tb = type(b)
    if tb is int or tb is long:
        if not b:
            raise ZeroDivisionError('%r / %r' % (a, b))
        if b == 1:
            return a
        ta = type(a)
        if ta is int or ta is long:
            return normalized_fraction(a, b)
    return a / b

def int_root(y, n):
    """ Return a pair ``(floor(y**(1/n)), x**n == y)``.

    Given integers y and n, return a tuple containing ``x =
    floor(y**(1/n))`` and a boolean indicating whether ``x**n == y``
    exactly.
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
    t = x**n
    while t > y:
        x -= 1
        t = x**n
    return x, t == y

def try_power(x, y):
    """\
    Attempt to compute ``x**y`` where ``x`` and ``y`` must be of the
    types int, long, FractionTuple, Float, or Complex. The function
    returns::

      z, symbolic

    where ``z`` is a number (i.e. a complex rational) and ``symbolic``
    is a list of ``(b, e)`` pairs representing symbolic factors
    ``b**e``.

    Examples::
    
      try_power(3, 2) --> (9, [])
      try_power(2, 1/2) --> (1, [(2, 1/2)])
      try_power(45, 1/2) --> (3, [(5, 1/2)])
    """
    if y==0 or x==1:
        # (anything)**0 -> 1
        # 1**(anything) -> 1
        return 1, []
    if isinstance(x, Infinity) or isinstance(y, Infinity):
        return x**y, []
    if isinstance(y, inttypes):
        if y >= 0:
            return x**y, []
        elif x==0:
            return Infinity.get_zoo(), []
        elif isinstance(x, inttypes):
            return FractionTuple((1, x**(-y))), []
        elif isinstance(x, (FractionTuple, Float, Complex)):
            return x**y, []
    elif isinstance(x, inttypes) and isinstance(y, FractionTuple):
        if x < 0:
            if x==-1:
                p, q = y
                if q==2:
                    return Complex(0, 1)**p, []
                return 1, [(x,y)]
            else:
                z, sym = try_power(-x, y)
                z1, sym1 = try_power(-1, y)
                return z * z1, sym+sym1
        else:
            p, q = y
            r, exact = int_root(x, q)
            if exact:
                if p > 0:
                    g = r**p
                else:
                    g = normalized_fraction(1, r**(-p))
                return g, []
    elif isinstance(x, FractionTuple) and isinstance(y, FractionTuple):
        a, b = x
        r, rsym = try_power(a, y)
        s, ssym = try_power(b, y)
        ssym = [(b, -e) for b, e in ssym]
        return (div(r,s), rsym + ssym)
    elif isinstance(x, Float) or isinstance(y, Float):
        return x ** y, []
    return 1, [(x, y)]


from .evalf import evalf
from .infinity import Infinity

from .methods import (\
    fraction_add, fraction_sub, fraction_rsub, fraction_mul,
    fraction_div, fraction_rdiv, fraction_pow,
    fraction_lt, fraction_le, fraction_gt, fraction_ge,
    complex_add, complex_sub, complex_rsub, complex_mul,
    complex_div, complex_rdiv, complex_pow)

FractionTuple.__add__ = FractionTuple.__radd__ = fraction_add
FractionTuple.__sub__ = fraction_sub
FractionTuple.__rsub__ = fraction_rsub
FractionTuple.__mul__ = FractionTuple.__rmul__ = fraction_mul
FractionTuple.__div__ = fraction_div
FractionTuple.__rdiv__ = fraction_rdiv
FractionTuple.__pow__ = fraction_pow
FractionTuple.__lt__ = fraction_lt
FractionTuple.__le__ = fraction_le
FractionTuple.__gt__ = fraction_gt
FractionTuple.__ge__ = fraction_ge

Complex.__add__ = Complex.__radd__ = complex_add
Complex.__sub__ = complex_sub
Complex.__rsub__ = complex_rsub
Complex.__mul__ = Complex.__rmul__ = complex_mul
Complex.__div__ = complex_div
Complex.__rdiv__ = complex_rdiv
Complex.__pow__ = complex_pow
