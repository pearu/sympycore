"""
The mpq fraction type implemented here is only intended to be used to
extend code that would otherwise use Python ints for the purpose
of representing exact numbers. Addition, multiplication and comparison
with mpqs and Python ints is therefore safe.

However, integer-valued fractions are converted back to Python ints,
and therefore code that would not work ordinarily with ints like

    a = mpq(2)
    b = mpq(3)
    a / b

should not be expected to work (this itself is an implementation detail
that may be changed). For this reason, non-integer-safe operations are
provided as functions (which take either mpq or Python ints as input).

Possible issues:
* Hashing is not compatible with floats (however, mixing floats and
  rationals is probably not a good idea).

"""

__all__ = ['mpq', 'mpf', 'mpc', 'div', 'extended_number',
           'nan', 'undefined', 'oo', 'moo', 'zoo']

from primitive import PrimitiveAlgebra, NUMBER

inttypes = (int, long)

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
            r, s = other, 1
        elif check(other, mpq):
            r, s = other
        else:
            return NotImplemented
        return mpq(p*s + q*r, q*s)

    __radd__ = __add__

    def __sub__(self, other, check=isinstance, inttypes=inttypes):
        p, q = self
        if check(other, inttypes):
            r, s = other, 1
        elif check(other, mpq):
            r, s = other
        else:
            return NotImplemented
        return mpq(p*s - q*r, q*s)

    def __rsub__(self, other, check=isinstance, inttypes=inttypes):
        p, q = self
        if check(other, inttypes):
            r, s = other, 1
        elif check(other, mpq):
            r, s = other
        else:
            return NotImplemented
        return mpq(q*r - p*s, q*s)

    def __mul__(self, other, check=isinstance, inttypes=inttypes):
        p, q = self
        if check(other, inttypes):
            r, s = other, 1
        elif check(other, mpq):
            r, s = other
        else:
            return NotImplemented
        return mpq(p*r, q*s)

    __rmul__ = __mul__

    def __pow__(self, n):
        if not (isinstance(n, inttypes) and n >= 0):
            raise ValueError
        p, q = self
        return mpq(p**n, q**n)

rational_types = (int, long, mpq)

def div(a, b, check=isinstance, inttypes=inttypes):
    if check(a, inttypes):
        p, q = a, 1
    else:
        p, q = a
    if check(b, inttypes):
        r, s = b, 1
    else:
        r, s = b
    return mpq(p*s, q*r)



from mpmath.lib import from_int, from_rational, to_str, fadd, fsub, fmul, \
  round_half_even, from_float, to_float, to_int, fpow, from_str, feq, \
  fhash, fcmp

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

    def __pow__(self, n):
        assert isinstance(n, inttypes)
        return mpf(fpow(self.val, n, self.prec, rounding))


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

    def __pow__(self, n):
        assert isinstance(n, (int, long)) and n >= 0
        if not n: return 1
        if n == 1: return self
        if n == 2: return self * self
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
        if not other:
            return nan
        return extended_number(self.infinite, as_direction(self.direction*other))

    __rmul__ = __mul__


undefined = nan = extended_number(0, 0)
oo = extended_number(1, 1)
moo = extended_number(1, -1)
zoo = extended_number(1, 0)
