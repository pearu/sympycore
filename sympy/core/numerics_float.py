"""
This module implements a multiprecision binary floating-point type in
Python. It is typically 10-100 times fasterthan Python's standard
Decimals. For details on usage, refer to the docstrings in the Float
class.
"""

from utils import memoizer_immutable_args, memoizer_Float_new
from basic import Basic, sympify
from number import Real

from floatlib import *


# Construct Float from raw man and exp
def makefloat(man, exp, newtuple=tuple.__new__):
    return newtuple(Float, normalize(man, exp, Float._prec, Float._mode))

def makefloat_from_fraction(p, q):
    prec = Float._prec
    mode = Float._mode
    n = prec + bitcount(q) + 2
    return tuple.__new__(Float, normalize((p<<n)//q, -n, prec, mode))



#----------------------------------------------------------------------
# Float class
#

class Float(Real, tuple):
    """
    A Float is a rational number of the form

        man * 2**exp

    ("man" and "exp" are short for "mantissa" and "exponent"). Both man
    and exp are integers, possibly negative, and may be arbitrarily large.
    Essentially, a larger mantissa corresponds to a higher precision
    and a larger exponent corresponds to larger magnitude.

    A Float instance is represented by a tuple

        (man, exp, bc)

    where bc is the bitcount of the mantissa. The elements can be
    accessed as named properties:

        >>> x = Float(3)
        >>> x.man
        3
        >>> x.exp
        0
        >>> x.bc
        2

    When performing an arithmetic operation on two Floats, or creating a
    new Float from an existing numerical value, the result gets rounded
    to a fixed precision level, just like with ordinary Python floats.
    Unlike regular Python floats, however, the precision level can be
    set arbitrarily high. You can also change the rounding mode (all
    modes supported by Decimal are also supported by Float).

    The precision level and rounding mode are stored as properties of
    the Float class. (An individual Float instances does not have any
    precision or rounding data associated with it.) The precision level
    and rounding mode make up the current working context. You can
    change the working context through static methods of the Float
    class:

        Float.setprec(n)    -- set precision to n bits
        Float.extraprec(n)  -- increase precision by n bits
        Float.setdps(n)     -- set precision equivalent to n decimals
        Float.setmode(mode) -- set rounding mode

    Corresponding methods are available for inspection:

        Float.getprec()
        Float.getdps()
        Float.getmode()

    There are also two methods Float.store() and Float.revert(). If
    you call Float.store() before changing precision or mode, the
    old context can be restored with Float.revert(). (If Float.revert()
    is called one time too much, the default settings are restored.)
    You can nest multiple uses of store() and revert().

    (In the future, it will also be possible to use the 'with'
    statement to change contexts.)

    Note that precision is measured in bits. Since the ratio between
    binary and decimal precision levels is irrational, setprec and
    setdps work slightly differently. When you set the precision with
    setdps, the bit precision is set slightly higher than the exact
    corresponding precision to account for the fact that decimal
    numbers cannot generally be represented exactly in binary (the
    classical example is 0.1). The exact number given to setdps
    is however used by __str__ to determine number of digits to
    display. Likewise, when you set a bit precision, the decimal
    printing precision used for __str__ is set slightly lower.

    The following rounding modes are available:

        ROUND_DOWN       -- toward zero
        ROUND_UP         -- away from zero
        ROUND_FLOOR      -- towards -oo
        ROUND_CEILING    -- towards +oo
        ROUND_HALF_UP    -- to nearest; 0.5 to 1
        ROUND_HALF_DOWN  -- to nearest; 0.5 to 0
        ROUND_HALF_EVEN  -- to nearest; 0.5 to 0 and 1.5 to 2

    The rounding modes are available both as global constants defined
    in this module and as properties of the Float class, e.g.
    Float.ROUND_CEILING.

    The default precision level is 53 bits and the default rounding
    mode is ROUND_HALF_EVEN. In this mode, Floats should round exactly
    like regular Python floats (in the absence of bugs!).
    """

    #------------------------------------------------------------------
    # Static methods for context management
    #

    # Also make these constants available from the class
    ROUND_DOWN = ROUND_DOWN
    ROUND_UP = ROUND_UP
    ROUND_FLOOR = ROUND_FLOOR
    ROUND_CEILING = ROUND_CEILING
    ROUND_HALF_UP = ROUND_HALF_UP
    ROUND_HALF_DOWN = ROUND_HALF_DOWN
    ROUND_HALF_EVEN = ROUND_HALF_EVEN

    _prec = 53
    _dps = 15
    _mode = ROUND_HALF_EVEN
    _stack = []

    make = staticmethod(makefloat)
    make_from_fraction = staticmethod(makefloat_from_fraction)

    @staticmethod
    def store():
        """Store the current precision/rounding context. It can
        be restored by calling Float.revert()"""
        Float._stack.append((Float._prec, Float._dps, Float._mode))

    @staticmethod
    def revert():
        """Revert to last precision/rounding context stored with
        Float.store()"""
        if Float._stack:
            Float._prec, Float._dps, Float._mode = Float._stack.pop()
        else:
            Float._prec, Float._dps, Float._mode = 53, 15, ROUND_HALF_EVEN

    @staticmethod
    def setprec(n):
        """Set precision to n bits"""
        n = int(n)
        Float._prec = n
        Float._dps = int(round(n/LOG2_10)-1)

    @staticmethod
    def setdps(n):
        """Set the precision high enough to allow representing numbers
        with at least n decimal places without loss."""
        n = int(n)
        Float._prec = int(round((n+1)*LOG2_10))
        Float._dps = n

    @staticmethod
    def extraprec(n):
        Float.setprec(Float._prec + n)

    @staticmethod
    def setmode(mode):
        assert isinstance(mode, RoundingMode)
        Float._mode = mode

    @staticmethod
    def getprec(): return Float._prec

    @staticmethod
    def getdps(): return Float._dps

    @staticmethod
    def getmode(): return Float._mode


    #------------------------------------------------------------------
    # Core object functionality
    #

    man = property(lambda self: self[0])
    exp = property(lambda self: self[1])
    bc = property(lambda self: self[2])

    @classmethod
    def makefloat(cls, man, exp, newtuple=tuple.__new__):
        return newtuple(cls, normalize(man, exp, cls._prec, cls._mode))

    @memoizer_Float_new
    def __new__(cls, x=0, prec=None, mode=None):
        # when changing __new__ signature, update memoizer_Float_new accordingly
        """
        Float(x) creates a new Float instance with value x. The usual
        types are supported for x:

            >>> Float(3)
            Float('3')
            >>> Float(3.5)
            Float('3.5')
            >>> Float('3.5')
            Float('3.5')
            >>> Float(Rational(7,2))
            Float('3.5')

        You can also create a Float from a tuple specifying its
        mantissa and exponent:

            >>> Float((5, -3))
            Float('0.625')

        Use the prec and mode arguments to specify a custom precision
        level (in bits) and rounding mode. If these arguments are
        omitted, the current working precision is used instead.

            >>> Float('0.500001', prec=3, mode=ROUND_DOWN)
            Float('0.5')
            >>> Float('0.500001', prec=3, mode=ROUND_UP)
            Float('0.625')

        """
        prec = prec or cls._prec
        mode = mode or cls._mode
        if x.__class__ is tuple:
            return tuple.__new__(cls, normalize(x[0], x[1], prec, mode))
        if isinstance(x, (int, long)):
            return tuple.__new__(cls, normalize(x, 0, prec, mode))
        if isinstance(x, float):
            return cls(float_from_pyfloat(x, prec, mode))
        if isinstance(x, (str, Basic.Rational)):
            # Basic.Rational should support parsing
            if isinstance(x, str):
                # XXX: fix this code
                import sympy
                x = sympy.Rational(x)
                x = Basic.Rational(x.p, x.q)
            return cls(float_from_rational(x.p, x.q, prec, mode))
        if isinstance(x, Basic):
            return x.evalf()
        raise TypeError(`x`)

    def __hash__(s):
        try:
            # Try to be compatible with hash values for floats and ints
            return hash(float(s))
        except OverflowError:
            # We must unfortunately sacrifice compatibility with ints here. We
            # could do hash(man << exp) when the exponent is positive, but
            # this would cause unreasonable inefficiency for large numbers.
            return tuple.__hash__(s)

    def __pos__(s):
        """Normalize s to the current working precision, rounding
        according to the current rounding mode."""
        return makefloat(s[0], s[1])

    def __float__(s):
        """Convert to a Python float. May raise OverflowError."""
        return float_to_pyfloat(s)

    def __int__(s):
        """Convert to a Python int, using floor rounding"""
        return float_to_int(s)

    def rational(s): # XXX: use s.as_Fraction instead
        """Convert to a SymPy Rational"""
        return Basic.Rational(*float_to_rational(s))

    def __repr__(s):
        """Represent s as a decimal string, with sufficiently many
        digits included to ensure that Float(repr(s)) == s at the
        current working precision."""
        st = "Float('%s')"
        return st % binary_to_decimal(s.man, s.exp, Float._dps + 2)

    def __str__(s):
        """Print slightly more prettily than __repr__"""
        return binary_to_decimal(s.man, s.exp, Float._dps)

    def torepr(self):
        st = "Float('%s')"
        return '%s(%r)' % (self.__class__.__name__,
                           binary_to_decimal(self.man, self.exp, Float._dps + 2))

    #------------------------------------------------------------------
    # Comparisons
    #

    def compare(self, other):
        """
        Warning: in extreme cases, the truncation error resulting from
        calling Float(t) will result in an erroneous comparison: for
        example, Float(2**80) will compare as equal to 2**80+1. This
        problem can be circumvented by manually increasing the working
        precision or by converting numbers into Rationals for
        comparisons.
        """
        if self is other: return 0
        c = cmp(self.__class__, other.__class__)
        if c:
            return c
        return fcmp(self, other)

    def __eq__(self, other):
        """s.__eq__(t) <==> s == Float(t)

        Determine whether s and Float(t) are equal (see warning for
        __cmp__ about conversion between different types.)"""
        other = Basic.sympify(other)
        if self is other: return True
        if other.is_Rational:
            other = other.as_Float
        if other.is_Float:
            return tuple.__eq__(self, other)
        return NotImplemented

    def __ne__(self, other):
        other = Basic.sympify(other)
        if self is other: return False
        if other.is_Rational:
            other = other.as_Float
        if other.is_Float:
            return tuple.__ne__(self, other)
        return NotImplemented

    def __lt__(self, other):
        other = Basic.sympify(other)
        if self is other: return False
        if other.is_Rational:
            other = other.as_Float
        if other.is_Float:
            return self.compare(other)==-1
        return NotImplemented

    def __le__(self, other):
        other = Basic.sympify(other)
        if self is other: return True
        if other.is_Rational:
            other = other.as_Float
        if other.is_Float:
            return self.compare(other)<=0
        return NotImplemented

    def __gt__(self, other):
        other = Basic.sympify(other)
        if self is other: return False
        if other.is_Rational:
            other = other.as_Float
        if other.is_Float:
            return self.compare(other)==1
        return NotImplemented

    def __ge__(self, other):
        other = Basic.sympify(other)
        if self is other: return True
        if other.is_Rational:
            other = other.as_Float
        if other.is_Float:
            return self.compare(other)>=0
        return NotImplemented

    def ae(s, t, rel_eps=None, abs_eps=None):
        """
        Determine whether the difference between s and t is smaller
        than a given epsilon ("ae" is short for "almost equal").

        Both a maximum relative difference and a maximum difference
        ('epsilons') may be specified. The absolute difference is
        defined as |s-t| and the relative difference is defined
        as |s-t|/max(|s|, |t|).

        If only one epsilon is given, both are set to the same value.
        If none is given, both epsilons are set to 2**(-prec+m) where
        prec is the current working precision and m is a small integer.
        """
        if not isinstance(t, Float):
            t = Float(t)
        if abs_eps is None and rel_eps is None:
            rel_eps = tuple.__new__(Float, (1, -s._prec+4, 1))
            rel_eps = Float((1, -s._prec+4))
        if abs_eps is None:
            abs_eps = rel_eps
        elif rel_eps is None:
            rel_eps = abs_eps
        diff = abs(s-t)
        if diff <= abs_eps:
            return True
        abss = abs(s)
        abst = abs(t)
        if abss < abst:
            err = diff/abst
        else:
            err = diff/abss
        return err <= rel_eps

    def almost_zero(s, prec):
        """Quick check if |s| < 2**-prec. May return a false negative
        if s is very close to the threshold."""
        return s.bc + s.exp < prec

    def __nonzero__(s):
        return not not s[0]

    #------------------------------------------------------------------
    # Arithmetic
    #

    def __abs__(s):
        if s[0] < 0:
            return -s
        return s

    def __neg__(s):
        return makefloat(-s[0], s[1])

    def __add__(s, t):
        t = sympify(t)
        if t.is_Rational:
            t = t.as_Float
        if t.is_Float:
            return Float(fadd(s, t, Float._prec, Float._mode))
        return NotImplemented

    def __radd__(self, other):
        if isinstance(other, Basic):
            if other.is_Rational:
                other = other.as_Float
            if other.is_Float:
                return other + self
            return Basic.Add(other, self)
        return sympify(other) + self

    def __sub__(s, t):
        t = sympify(t)
        if t.is_Rational:
            t = t.as_Float
        if t.is_Float:
            return s + tuple.__new__(Float, (-t[0],) + t[1:])
        return NotImplemented

    def __rsub__(self, other):
        if isinstance(other, Basic):
            if other.is_Rational:
                other = other.as_Float
            if other.is_Float:
                return other - self
            return Basic.Add(other, -self)
        return sympify(other) - self

    def __mul__(s, t):
        if isinstance(t, (int, long, Basic.Integer)):
            return makefloat(s[0]*int(t), s[1])
        t = sympify(t)
        if t.is_Rational:
            t = t.as_Float
        if t.is_Float:
            return Float(fmul(s, t, Float._prec, Float._mode))
        return NotImplemented

    def __rmul__(self, other):
        if isinstance(other, Basic):
            if other.is_Rational:
                other = other.as_Float
            if other.is_Float:
                return other * self
            return Basic.Mul(other, self)
        return sympify(other) * self

    def __div__(s, t):
        if isinstance(t, (int, long, Basic.Integer)):
            t = int(t)
            sman, sexp, sbc = s
            extra = s._prec - sbc + bitcount(t) + 4
            return makefloat((sman<<extra)//t, sexp-extra)
        t = sympify(t)
        if t.is_Rational:
            t = t.as_Float
        if t.is_Float:
            return Float(fdiv(s, t, Float._prec, Float._mode))
        return NotImplemented

    def __rdiv__(self, other):
        if isinstance(other, Basic):
            if other.is_Rational:
                other = other.as_Float
            if other.is_Float:
                return other / self                
            return Basic.Mul(other, makefloat_from_fraction(1,1) / self)
        return sympify(other) / self

    def __pow__(self, other):
        other = sympify(other)
        r = self.try_power(other)
        if r is not None:
            return r
        return NotImplemented

    @memoizer_immutable_args('Float.try_power')
    def try_power(self, other):
        if other.is_Integer:
            return Float(fpow(self, other, Float._prec, Float._mode))
        if other.is_Fraction:
            other = other.as_Float
        if other.is_Float:
            if other == 0.5:
                return Float(fsqrt(self, Float._prec, Float._mode))
            from numerics.functions import exp, log
            return exp(other * log(self))
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

    def __rpow__(self, other):
        if isinstance(other, Basic):
            if other.is_Float:
                other = other.as_Float
            if other.is_Float:
                return other ** self
            return Basic.Pow(other, self)
        return sympify(other) ** self
