"""
Float - using mpmath.lib functionality.
"""

import decimal

from ..core import Basic, sympify, BasicType, classes, objects
from .number import Real
from .mpmath.lib import (fzero,
                         fcmp, fneg_exact, fadd, fsub, fmul, fdiv, fpow,
                         fabs, flog, fexp, fatan,fsqrt,
                         from_int, from_rational, from_float,
                         to_int, to_float, to_rational,
                         from_str,
                         normalize,
                         fpi, fgamma,
                         STANDARD_PREC, ROUND_HALF_EVEN,
                         ROUND_FLOOR, ROUND_CEILING,
                         LOG2_10,
                         )

__all__ = ['Float']

getctx = decimal.getcontext
Dec = decimal.Decimal
def binary_to_decimal(s, n):
    """Represent as a decimal string with at most n digits"""
    man, exp, bc = s
    prec_ = getctx().prec
    getctx().prec = n + 10
    d = Dec(man) * Dec(2)**exp
    getctx().prec = n
    a = str((+d).normalize())
    getctx().prec = prec_
    return a


def make_arithmetic_mth(mthname, fmth):
    def mth(self, other):
        Float = self.__class__
        if isinstance(other, (int,long,float)):
            other = Float(other, self.prec)
        else:
            other = sympify(other)
        if other.is_Rational:
            other = Float(other, self.prec)
        if other.is_Float:
            precision = Float.coerce_precisions(mthname, self, other)
            rounding = Float._rounding
            return Float(fmth(self, other, precision, rounding), precision)
        return NotImplemented
    return mth

#----------------------------------------------------------------------
# Float class
#

class Float(Real, tuple):

    _rounding = ROUND_HALF_EVEN
    _precision = STANDARD_PREC

    def __new__(cls, val=fzero, precision=None, rounding=None):
        
        if precision is None:
            _precision = Float._precision
        else:
            _precision = precision
        if rounding is None:
            _rounding = Float._rounding
        else:
            _rounding = rounding

        obj = None
        
        if isinstance(val, Basic):
            if val.is_Float:
                if val.prec == _precision:
                    obj = val
                else:
                    obj = tuple.__new__(cls, normalize(val[0], val[1], _precision, _rounding))
            elif val.is_Integer:
                obj = tuple.__new__(cls, from_int(val.p, _precision, _rounding))
            elif val.is_Fraction:
                obj = tuple.__new__(cls, from_rational(val.p, val.q, _precision, _rounding))
            else:
                return val.evalf(precision=_precision, rounding=_rounding)
        elif isinstance(val, (int, long)):
            obj = tuple.__new__(cls, from_int(val, _precision, _rounding))
        elif isinstance(val, float):
            obj = tuple.__new__(cls, from_float(val, _precision, _rounding))
        elif isinstance(val, tuple):
            assert len(val)==3,`val`
            obj = tuple.__new__(cls, val)
        elif isinstance(val, str):
            obj = tuple.__new__(cls, from_str(val, _precision, _rounding))

        if obj is None:
            raise TypeError('%s: expected int|long|float|str|Number instance but got %r'\
                            % (cls.__name__, type(val)))
    
        obj._precision = _precision
        return obj

    man = property(lambda self: self[0])
    exp = property(lambda self: self[1])
    bc = property(lambda self: self[2])
    prec = property(lambda self: self._precision)

    def tostr(self, level=0):
        dps = int(round(self.prec/LOG2_10)-1)
        return binary_to_decimal(self, dps)

    def torepr(self):
        return '%s(%s, precision=%s)' % (self.__class__.__name__,
                                         tuple(self), self.prec)

    @staticmethod
    def make_from_fraction(p, q):
        _precision = Float._precision
        _rounding = Float._rounding        
        return tuple.__new__(Float,
                             from_rational(p, q, _precision, _rounding))

    @property
    def is_positive(self): return self.man > 0
    @property
    def is_negative(self): return self.man < 0
    @property
    def is_nonpositive(self): return self.man <= 0
    @property
    def is_nonnegative(self): return self.man >= 0
    @property
    def is_zero(self): return self.man==0

    __hash__ = tuple.__hash__

    def __eq__(self, other):
        Float = self.__class__
        if isinstance(other, (int,long,float)):
            other = Float(other, self.prec)
        if isinstance(other, Basic):
            if other.is_Rational:
                other = Float(other, self.prec)
            if other.is_Float:
                return tuple.__eq__(self, other) and self.prec==other.prec
            if other.is_Number:
                return NotImplemented
            return False
        return self == sympify(other)

    def __ne__(self, other):
        Float = self.__class__
        if isinstance(other, (int,long,float)):
            other = Float(other, self.prec)
        else:
            other = sympify(other)
        if self is other: return False
        if other.is_Rational:
            other = Float(other, self.prec)
        if other.is_Float:
            return tuple.__ne__(self, other) or self.prec!=other.prec
        return NotImplemented

    def __lt__(self, other):
        Float = self.__class__
        if isinstance(other, (int,long,float)):
            other = Float(other, self.prec)
        else:
            other = sympify(other)
        if self is other: return False
        if other.is_Rational:
            other = Float(other, self.prec)
        if other.is_Float:
            return fcmp(self, other) < 0
        return NotImplemented

    def __le__(self, other):
        Float = self.__class__
        if isinstance(other, (int,long,float)):
            other = Float(other, self.prec)
        else:
            other = sympify(other)
        if self is other: return True
        if other.is_Rational:
            other = Float(other, self.prec)
        if other.is_Float:
            return fcmp(self, other) <= 0
        return NotImplemented

    def __gt__(self, other):
        Float = self.__class__
        if isinstance(other, (int,long,float)):
            other = Float(other, self.prec)
        else:
            other = sympify(other)
        if self is other: return False
        if other.is_Rational:
            other = Float(other, self.prec)
        if other.is_Float:
            return fcmp(self, other) > 0
        return NotImplemented

    def __ge__(self, other):
        Float = self.__class__
        if isinstance(other, (int,long,float)):
            other = Float(other, self.prec)
        else:
            other = sympify(other)
        if self is other: return True
        if other.is_Rational:
            other = Float(other, self.prec)
        if other.is_Float:
            return fcmp(self, other) >= 0
        return NotImplemented

    def __float__(self):
        return to_float(self[:])

    def __int__(self):
        return int(to_int(self[:]))

    def __long__(self):
        return long(to_int(self[:]))

    def __abs__(self):
        Float = self.__class__
        precision = self.prec
        rounding = Float._rounding
        return Float(fabs(self, precision, rounding), self.prec)

    def __pos__(self):
        return self

    def __neg__(self):
        Float = self.__class__
        return Float(fneg_exact(self), self.prec)

    @staticmethod
    def coerce_precisions(mth, s, t):
        return min(s.prec, t.prec)

    __add__ = make_arithmetic_mth('__add__', fadd)
    __sub__ = make_arithmetic_mth('__sub__', fsub)
    __mul__ = make_arithmetic_mth('__mul__', fmul)
    __div__ = make_arithmetic_mth('__div__', fdiv)

    def __pow__(self, other):
        Float = self.__class__
        if isinstance(other, (int,long)):
            precision = self.prec
            rounding = Float._rounding
            if isinstance(other, Basic): other = other.p
            return Float(fpow(self, other, precision, rounding), precision)
        else:
            other = sympify(other)
        if other.is_Rational:
            if other.is_half:
                if self.is_nonnegative:
                    precision = self.prec
                    rounding = Float._rounding
                    return Float(fsqrt(self, precision, rounding), precision)
            other = Float(other, self.prec)
        if other.is_Float:
            precision = Float.coerce_precisions('__pow__', self, other)
            rounding = Float._rounding
            if other.exp >=0:
                return Float(fpow(self, other.man << other.exp, precision, rounding), precision)
            if self.is_nonnegative:
                return (other * self.evalf_log(precision+5)).evalf_exp(precision)
        return NotImplemented

    def __radd__(self, other):
        Float = self.__class__
        if isinstance(other, (int,long,float)):
            other = Float(other, self.prec)
        if isinstance(other, Basic):
            if other.is_Rational:
                other = Float(other, self.prec)
            if other.is_Float:
                return other.__add__(self)
            return classes.Add(other, self)
        return sympify(other) + self

    def __rsub__(self, other):
        Float = self.__class__
        if isinstance(other, (int,long,float)):
            other = Float(other, self.prec)
        if isinstance(other, Basic):
            if other.is_Rational:
                other = Float(other, self.prec)
            if other.is_Float:
                return other.__sub__(self)
            return classes.Add(other, -self)
        return sympify(other) - self

    def __rmul__(self, other):
        Float = self.__class__
        if isinstance(other, (int,long,float)):
            other = Float(other, self.prec)
        if isinstance(other, Basic):
            if other.is_Rational:
                other = Float(other, self.prec)
            if other.is_Float:
                return other.__mul__(self)
            return classes.Mul(other, self)
        return sympify(other) * self

    def __rdiv__(self, other):
        Float = self.__class__
        if isinstance(other, (int,long,float)):
            other = Float(other, self.prec)
        if isinstance(other, Basic):
            if other.is_Rational:
                other = Float(other, self.prec)
            if other.is_Float:
                return other.__div__(self)
            return classes.Mul(other, 1/self)
        return sympify(other) / self

    def __rpow__(self, other):
        Float = self.__class__
        if isinstance(other, (int,long,float)):
            other = Float(other, self.prec)
        if isinstance(other, Basic):
            if other.is_Rational:
                other = Float(other, self.prec)
            if other.is_Float:
                return other.__pow__(self)
            return classes.Pow(other, self)
        return sympify(other) ** self

    def evalf(self, precision=None):
        Float = self.__class__
        if precision is None:
            return self
        return Float(self, precision)

    def evalf_sqrt(self, precision=None):
        Float = self.__class__
        if self.is_nonnegative:
            if precision is None:
                precision = self.prec
            rounding = Float._rounding
            return Float(fsqrt(self[:], precision, rounding), precision)
        return abs(self).evalf_sqrt(precision) * objects.I

    def evalf_log(self, precision=None):
        Float = self.__class__
        if self.is_positive:
            if precision is None:
                precision = self.prec
            rounding = Float._rounding
            return Float(flog(self[:], precision, rounding), precision)
        if self.is_zero:
            return objects.nan
        return abs(self).evalf_log(precision) + objects.I

    def evalf_exp(self, precision=None):
        Float = self.__class__
        if precision is None:
            precision = self.prec
        rounding = Float._rounding
        return Float(fexp(self[:], precision, rounding), precision)

    def evalf_atan(self, precision=None):
        Float = self.__class__
        if precision is None:
            precision = self.prec
        rounding = Float._rounding
        return Float(fatan(self[:], precision, rounding), precision)

    #TODO: evalf_atan2, evalf_sin, evalf_cos, etc.

    @staticmethod
    def evalf_pi(precision=None):
        if precision is None:
            precision = Float._precision
        rounding = Float._rounding
        return Float(fpi(precision, rounding), precision)

    @staticmethod
    def evalf_gamma(precision=None):
        if precision is None:
            precision = Float._precision
        rounding = Float._rounding
        return Float(fgamma(precision, rounding), precision)

    def try_power(self, other):
        if other.is_Infinity:
            a = abs(self)
            if a < 1:
                return Float(0, self.prec)
            if a==1:
                return a
            if self.is_negative:
                return objects.nan
            return other
