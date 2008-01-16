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
        raise NotImplementedError

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
    def __eq__(self, other): return feq(self.val, self.convert(other))
    def __cmp__(self, other): return fcmp(self.val, self.convert(other))

    def __add__(self, other):
        return mpf(fadd(self.val, self.convert(other), self.prec, rounding), self.prec)

    __radd__ = __add__

    def __sub__(self, other):
        return mpf(fsub(self.val, self.convert(other), self.prec, rounding), self.prec)

    def __rsub__(self, other):
        return mpf(fsub(self.convert(other), self.val, self.prec, rounding), self.prec)

    def __mul__(self, other):
        return mpf(fmul(self.val, self.convert(other), self.prec, rounding), self.prec)

    __rmul__ = __mul__

    def __pow__(self, n):
        assert isinstance(n, inttypes)
        return mpf(fpow(self.val, n, self.prec, rounding))

__all__ = ['mpq', 'mpf', 'div']
