"""
 plus  | -oo | +oo | nan | r
 ------------------------------
  -oo  | -oo | nan | nan | -oo
  +oo  | nan | +oo | nan | +oo
  nan  | nan | nan | nan | nan
   p   | -oo | +oo | nan | p+r

 p,r are rational

 mul   | -oo | +oo | nan |  0  |  -r |  +p
 ------------------------------------------
  -oo  | +oo | -oo | nan | nan | +oo | -oo
  +oo  | -oo | +oo | nan | nan | -oo | +oo
  nan  | nan | nan | nan | nan | nan | nan
   0   | nan | nan | nan |  0  |  0  |  0
  -r   | +oo | -oo | nan |  0  | r*r | -p*r
  +p   | -oo | +oo | nan |  0  | -r*p| p*p

 p,r are positive rational numbers

 pow   | -oo | +oo | nan |  0  |  -1 | +1  | -n  | +n        | -1/n | +1/n
 ------------------------------------------------------------------------------------
  -oo  | nan | nan | nan |  1  |  0  | -oo | 0   |(-1)**n*oo | 0    | (-1)**(1/n) * oo
  +oo  |  0  | +oo | nan |  1  |  0  | +oo | 0   | +oo       | 0    | +oo
  nan  | nan | nan | nan |  1  | nan | nan | nan | nan       | nan  | nan 
   0   | +oo |  0  |  0  |  1  | +oo |  0  | +oo |  0        | +oo  |  0
   -1  | nan | nan | nan |  1  |  -1 |  -1 | (-1)**n | (-1)**n | -(-1)**(1+1/n) | (-1)**(1/n)
   +1  |  1  |  1  |  1  |  1  |  1  |  1  |  1  |  1        |   1  |   1
   -m  |  0  | +oo+oo*I |nan|1 | -1/m|  -m |(-1)**n/m**n|(-m)**n|-(-1)**(1+1/n)/m**(1/n) | (-1)**(1/n)*m**(1/n)
   +m  |  0  | +oo | nan |  1  | 1/m |  +m | 1/m**n | m**n   | 1/m**(1/n) | m**(1/n)
   
 m,n are positive integers

Author: Pearu Peterson <pearu.peterson@gmail.com>
Created: 2006
"""

__all__ = ['Number','Rational','Integer','Decimal']

import math

import decimal

decimal_to_Number_cls = {
    decimal.Decimal('0').as_tuple():'Zero',
    decimal.Decimal('1').as_tuple():'One',
    decimal.Decimal('-1').as_tuple():'NegativeOne',
    decimal.Decimal('Infinity').as_tuple():'Infinity',
    decimal.Decimal('-Infinity').as_tuple():'NegativeInfinity',
    decimal.Decimal('NaN').as_tuple():'NaN',
    }

import decimal_math

from base import Symbolic, Constant, integer_types, decimal_types
from base import RelationalMethods, FunctionalMethods, ArithmeticMethods
from singleton import ConstantSingleton

class Number(RelationalMethods, ArithmeticMethods,
             Constant):
    """ Represents a number.
    """

    ###########################################################################
    #
    # Constructor methods
    #

    Number_cache = {}
    
    def __new__(cls, *obj):
        if len(obj)==1: obj=obj[0]
        if isinstance(obj,integer_types):
            return Integer(obj)
        if isinstance(obj,tuple) and len(obj)==2:
            return Rational(*obj)
        if isinstance(obj, (str,float,decimal.Decimal)):
            return Decimal(obj)
        if isinstance(obj, Number):
            return obj
        raise TypeError,`type(obj)`

    ############################################################################
    #
    # Informational methods
    #

    def get_precedence(self): return 30

    ###########################################################################
    #
    # Transformation methods
    #

    def todecimal(self):
        return Decimal(self._todecimal())

    def _todecimal(self):
        """ Return as decimal.Decimal instance.
        """
        raise NotImplementedError,'%s needs ._todecimal() method' % (self.__class__.__name__)

    ############################################################################
    #
    # Substitution methods
    #

    def substitute(self, subst, replacement=None):
        return self

    def neg_invert(self):
        return -self

    ############################################################################
    #
    # Relational methods
    #

    def __eq__(self, other):
        raise NotImplementedError,'%s needs .__eq__() method' % (self.__class__.__name__)

    def __ne__(self, other):
        r = self == other
        if isinstance(r, bool): return not r
        return ~r

    def __lt__(self, other):
        raise NotImplementedError,'%s needs .__lt__() method' % (self.__class__.__name__)

    def __gt__(self, other):
        return Symbolic(other).__lt__(self)

    def __le__(self, other):
        r = self > other
        if isinstance(r, bool): return not r
        return ~r

    def __ge__(self, other):
        return Symbolic(other).__le__(self)

    ############################################################################
    #
    # Default methods.
    #

    def calc_expanded(self): return self

#
# End of Number class
#
################################################################################

def gcd(a, b):
    '''Returns the Greatest Common Divisor,
    implementing Euclid\'s algorithm.'''
    while a:
        a, b = b%a, a
    return b

def ngcd(*args):
    if not args: return 1
    if len(args)==1: return args[0]
    if len(args)==2: return gcd(*args)
    return ngcd(args[0],ngcd(*args[1:]))

def factor_trial_division(n):
    """
    Factor any integer into a product of primes, 0, 1, and -1.
    """
    if not n: return {0:1}
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


class Decimal(Number):
    """ Represents a decimal number
    """

    def float_to_decimal(f):
        "Convert a floating point number to a Decimal with no loss of information"
        # Transform (exactly) a float to a mantissa (0.5 <= abs(m) < 1.0) and an
        # exponent.  Double the mantissa until it is an integer.  Use the integer
        # mantissa and exponent to compute an equivalent Decimal.  If this cannot
        # be done exactly, then retry with more precision.

        mantissa, exponent = math.frexp(f)
        while mantissa != int(mantissa):
            mantissa *= 2.0
            exponent -= 1
        mantissa = int(mantissa)

        oldcontext = decimal.getcontext()
        decimal.setcontext(decimal.Context(traps=[decimal.Inexact]))
        try:
            while True:
                try:
                    return mantissa * decimal.Decimal(2) ** exponent
                except decimal.Inexact:
                    decimal.getcontext().prec += 1
        finally:
            decimal.setcontext(oldcontext)

    float_to_decimal = staticmethod(float_to_decimal)

    ###########################################################################
    #
    # Constructor methods
    #
    
    def __new__(cls, num):
        if isinstance(num, (str, int, long)):
            num = decimal.Decimal(num)
        elif isinstance(num, float):
            num = Decimal.float_to_decimal(num)
        if isinstance(num, decimal.Decimal):
            singleton_cls_name = decimal_to_Number_cls.get(num.as_tuple(), None)
            if singleton_cls_name is not None:
                return getattr(Symbolic, singleton_cls_name)()
            return Symbolic.__new__(cls, num)
            #obj = Number.Number_cache.get(num, None)
            #if obj is None:
            #    Number.Number_cache[num] = obj = Symbolic.__new__(cls, num)
            #return obj
        raise TypeError,'%r' % (type(num))

    def init(self, num):
        self.num = num
        return

    def astuple(self):
        return (self.__class__.__name__, self.num)

    def eval_power(base, exponent):
        """
        base is decimal but not equal to rationals, integers, 0.5, oo, -oo, nan
        exponent is symbolic object but not equal to 0, 1

        (-p) ** r -> exp(r * log(-p)) -> exp(r * (log(p) + I*Pi)) ->
                  -> p ** r * (sin(Pi*r) + cos(Pi*r) * I)
        """
        if isinstance(exponent, Number):
            e = exponent._todecimal()
            if base.is_negative():
                m = decimal_math.pow(-base.num, e)
                a = decimal_math.pi() * e
                s = m * decimal_math.sin(a)
                c = m * decimal_math.cos(a)
                return Decimal(s) + Decimal(c) * Symbolic.ImaginaryUnit()
            return Decimal(decimal_math.pow(base.num, e))
        return

    ############################################################################
    #
    #b Informational methods
    #

    def torepr(self):
        return repr(self.num)

    def tostr(self, level=0):
        return str(self.num.normalize())

    def is_negative(self):
        return self.num.as_tuple()[0]==1

    def is_positive(self):
        return self.num.as_tuple()[0]==1

    ###########################################################################
    #
    # Transformation methods
    #

    def __int__(self):
        return int(self.num)

    def __float__(self):
        return float(self.num)

    def _todecimal(self):
        return self.num

    ############################################################################
    #
    # Relational methods
    #

    def __eq__(self, other):
        other = Symbolic(other)
        if isinstance(other, Number):
            return self.num == other._todecimal()
        return Number.__eq__(self, other)

    def __lt__(self, other):
        other = Symbolic(other)
        if isinstance(other, Number):
            return self.num < other._todecimal()
        return Number.__lt__(self, other)

    ############################################################################
    #
    # Arithmetic operations
    #

    def __abs__(self):
        return Decimal(abs(self.num))

    def __neg__(self):
        return Decimal(-self.num)

    def __add__(self, other):
        other = Symbolic(other)
        if isinstance(other, Number):
            return Decimal(self.num + other._todecimal())
        return Number.__add__(self, other)

    def __mul__(self, other):
        other = Symbolic(other)
        if isinstance(other, Number):
            return Decimal(self.num * other._todecimal())
        return Number.__mul__(self, other)

#
# End of Rational class
#
################################################################################

class Rational(Number):
    """ Represents a rational number.

    Operations:
      numer/1 -> Integer(numer)
      0/0 -> NaN()
      numer/0 -> Infinity()*numer
      0/numer -> Zero()
    """

    ###########################################################################
    #
    # Constructor methods
    #
    
    def __new__(cls, numer, denom):
        if isinstance(numer,integer_types) and isinstance(denom,integer_types):
            if denom==0:
                if numer>0: return Infinity()
                if numer<0: return NegativeInfinity()
                return NaN()
            if numer==0: return Zero()
            if denom < 0:
                numer = -numer
                denom = -denom
            n = gcd(abs(numer), denom)
            if n>1:
                numer = numer // n
                denom = denom // n
            if denom==1: return Integer(numer)
            if denom==2 and numer==1: return Half()
            obj = Number.Number_cache.get((numer, denom), None)
            if obj is None:
                Number.Number_cache[(numer, denom)] = obj = Symbolic.__new__(cls, numer, denom)
            return obj
        if isinstance(numer, Number) or isinstance(denom, Number):
            return numer / denom
        raise TypeError,'%r,%r' % (type(numer),type(denom))

    def init(self, numer, denom):
        self.numer = numer
        self.denom = denom
        return

    def astuple(self):
        return (self.__class__.__name__, self.numer, self.denom)

    def calc_factors(self):
        f = factor_trial_division(self.numer)
        for p,e in factor_trial_division(self.denom).items():
            try:
                f[p] += -e
            except KeyError:
                f[p] = -e
        fi = {}
        for p,e in f.items():
            if e==0:
                del f[p]
            else:
                try:
                    fi[e] *= p
                except KeyError:
                    fi[e] = p
        f = {}
        for e,p in fi.items():
            f[p] = e
        if len(f)>1 and f.has_key(1): del f[1]
        return f

    def eval_power(base, exponent):
        """
        base is rational but not equal to integers, oo, -oo, nan
        exponent is symbolic object but not equal to 0, 1

        (n/d) ** nan -> nan
        (n/d) ** -1 -> d/n
        (n/d) ** -p  -> (d/n) ** p, p is any number
        (n/d) ** oo -> oo if n>d
                    -> 0 if |n|<d
                    -> oo+oo*I if n < -d
        (n/d) ** i -> (n**i)/(d**i), i is positive integer
        (n/d) ** (r/s) -> n ** (r/s) * d ** (-r/s)
        """
        if isinstance(exponent, Number):
            if isinstance(exponent, Decimal):
                return Decimal(decimal_math.pow(base._todecimal(), exponent.num))
            if isinstance(exponent, NaN):
                return NaN()
            if exponent.is_negative():
                if isinstance(exponent, NegativeOne):
                    return Rational(base.denom, base.numer)
                return Rational(base.denom, base.numer) ** (-exponent)
            assert not isinstance(exponent, NegativeInfinity)
            if isinstance(exponent, Infinity):
                if base.numer > base.denom:
                    return Infinity()
                if base.numer < -base.denom:
                    return Infinity() + Infinity() * Symbolic.ImaginaryUnit()
                return Zero()
            if isinstance(exponent, Integer):
                return Rational(base.numer ** exponent.numer, base.denom ** exponent.numer)
            if isinstance(exponent, Rational):
                return Integer(base.numer) ** exponent * Integer(base.denom) ** (-exponent)

        return

    ############################################################################
    #
    # Informational methods
    #

    def is_negative(self):
        return self.numer < 0

    def is_positive(self):
        return self.numer > 0

    def get_precedence(self): return 50 # same as in Mul

    ###########################################################################
    #
    # Transformation methods
    #

    def tostr(self, level=0):
        precedence = self.get_precedence()
        if precedence<=level:
            return '(%s/%s)' % (self.numer, self.denom)
        return '%s/%s' % (self.numer, self.denom)

    def _todecimal(self):
        return decimal.Decimal(self.numer) / decimal.Decimal(self.denom)

    def __int__(self):
        return int(self.numer//self.denom)

    def __float__(self):
        return float(self.todecimal())

    ###########################################################################
    #
    # Comparison methods
    #

    def compare(self, other):
        if self is other: return 0
        c = self.compare_classes(other)
        if c: return c
        return cmp(self.numer * other.denom, self.denom * other.numer)

    ############################################################################
    #
    # Relational methods
    #

    def __eq__(self, other):
        other = Symbolic(other)
        if isinstance(other, Decimal):
            return other == self
        if isinstance(other, Rational):
            return self.denom==other.denom and self.numer==other.numer
        return Number.__eq__(self, other)

    def __lt__(self, other):
        other = Symbolic(other)
        if isinstance(other, Decimal):
            return self.todecimal() < other
        if isinstance(other, Rational):
            return self.numer * other.denom < self.denom*other.numer        
        return Number.__lt__(self, other)

    ############################################################################
    #
    # Arithmetic operations
    #

    def __abs__(self):
        if self.numer < 0: return -self
        return self

    def __neg__(self): return Rational(-self.numer, self.denom)

    def __add__(self, other):
        other = Symbolic(other)
        if isinstance(other, Decimal): return other + self
        if isinstance(other, Rational):
            return Rational(self.numer*other.denom+self.denom*other.numer,
                            self.denom*other.denom)        
        return Number.__add__(self, other)

    def __mul__(self, other):
        other = Symbolic(other)
        if isinstance(other, Decimal): return other * self
        if isinstance(other, Rational):
            return Rational(self.numer*other.numer, self.denom*other.denom)
        return Number.__mul__(self, other)

#
# End of Rational class
#
################################################################################


class Integer(Rational):
    """ Represents an integer.
    
    Operations:
      0 -> Zero()
      1 -> One()
      -1 -> NegativeOne()
      integer -> integer
    """

    ###########################################################################
    #
    # Constructor methods
    #

    denom = 1

    def __new__(cls, numer):
        if isinstance(numer, integer_types):
            if numer==0: return Zero()
            if numer==1: return One()
            if numer==-1: return NegativeOne()
            obj = Number.Number_cache.get((numer,), None)
            if obj is None:
                Number.Number_cache[(numer,)] = obj = Symbolic.__new__(cls, numer)
            return obj
        if isinstance(numer, Integer): return numer
        raise TypeError,`type(numer)`

    def init(self, numer):
        self.numer = numer
        return

    def astuple(self): return (self.__class__.__name__, self.numer)

    def eval_power(base, exponent):
        """
        base is integer but not equal to 0, 1, -1, oo, -oo, nan
        exponent is symbolic object but not equal to 0, 1

        n ** nan -> nan
        n ** -1 -> 1/n
        (+n) ** oo -> oo
        (-n) ** oo -> oo + oo*I
        n ** -oo -> 0
        n ** -m -> 1/(n**m)
        n ** m  -> (n**m)
        n ** (r/s) -> n ** q * n ** (r/s - q), where q=r//s and q!=0
        """
        if isinstance(exponent, Number):
            if isinstance(exponent, Decimal):
                return Decimal(decimal_math.pow(base._todecimal(), exponent.num))
            if isinstance(exponent, NaN):
                return NaN()
            if isinstance(exponent, NegativeOne):
                return Rational(1, base.numer)
            if isinstance(exponent, Infinity):
                if base.is_negative():
                    return Infinity() + Infinity() * Symbolic.ImaginaryUnit()
                return Infinity()
            if isinstance(exponent, NegativeInfinity):
                return Zero()
            if isinstance(exponent, Integer):
                if exponent.is_negative():
                    return Rational(1, base.numer ** (-exponent.numer))
                return Integer(base.numer ** exponent.numer)
            if isinstance(exponent, Rational):
                q = int(exponent)
                if q:
                    q = Integer(q)
                    return base ** q * base ** (exponent - q)
        return            
    ############################################################################
    #
    # Informational methods
    #

    def is_negative(self): return self.numer < 0

    def is_positive(self): return self.numer > 0

    def is_even(self): return not self.numer % 2

    def is_odd(self): return bool(self.numer % 2)

    ###########################################################################
    #
    # Transformation methods
    #


    def tostr(self, level=0):
        precedence = self.get_precedence()
        if precedence<=level and self.numer<0:
            return '(%s)' % (self.numer)
        return str(self.numer)

    def todecimal(self):
        return Decimal(self.numer)

#
# End of Integer class
#
################################################################################



class Zero(ConstantSingleton, Integer):
    """ Represents number 0.

    Operations:
      0 + obj -> obj
      0 * nan -> nan
      0 * oo -> nan
      0 * number -> 0
      0 ** oo -> nan
      0 ** -oo -> 0
      0 ** 0 -> 1
      0 ** neg number -> oo
      0 ** pos number -> 0
      oo ** 0 -> nan
      nan ** 0 -> nan
      number ** 0 -> 1
    """

    ###########################################################################
    #
    # Constructor methods
    #
    
    numer = 0
    denom = 1

    def eval_power(base, exponent):
        """
        exponent is symbolic object but not equal to 0, 1

        0 ** 0 -> 1
        0 ** (-n) -> oo, n is number, oo
        0 ** n    -> 0, n is number, oo, nan, numeric-expresson
        """
        if isinstance(exponent, Number):
            if exponent.is_negative():
                return Infinity()
            return Zero()
        if not exponent.symbols():
            d = exponent.todecimal()
            if isinstance(d, Number):
                if d.is_negative():
                    return Infinity()
                return Zero()
        return

    ############################################################################
    #
    # Informational methods
    #

    def is_negative(self): return False
    def is_positive(self): return False

    ###########################################################################
    #
    # Transformation methods
    #

    def _todecimal(self):
        return decimal.Decimal(0)

    ############################################################################
    #
    # Relational methods
    #

    def __eq__(self, other):
        other = Symbolic(other)
        if self is other: return True
        if isinstance(other, Number): return False
        return Number.__eq__(self, other)

    def __lt__(self, other):
        other = Symbolic(other)
        if self is other: return False
        if isinstance(other, Number):
            return other.is_positive()
        return Number.__lt__(self, other)

    ############################################################################
    #
    # Arithmetic operations
    #

    def __neg__(self): return self
    def __add__(self, other): return other
    __radd__ = __add__
    def __mul__(self, other):
        if isinstance(other, (NaN, Infinity, NegativeInfinity)): return NaN()
        return self
    __rmul__ = __mul__

    def __div__(self, other):
        if isinstance(other, NaN): return other
        if isinstance(other, Infinity): return self
        if self is other: return NaN()
        if isinstance(other, Number): return self
        if isinstance(other, integer_types):
            if other==0: return NaN()
            return self
        return Number.__div__(self, other)

#
# End of Zero class
#
################################################################################


class Half(ConstantSingleton, Rational):
    """ Represents number 1/2.
    """
    ###########################################################################
    #
    # Constructor methods
    #
    
    numer = 1
    denom = 2

    ############################################################################
    #
    # Informational methods
    #

    def is_negative(self): return False

    ###########################################################################
    #
    # Transformation methods
    #

    def _todecimal(self):
        return decimal.Decimal("0.5")

    ############################################################################
    #
    # Relational methods
    #

    def __eq__(self, other):
        other = Symbolic(other)
        if self is other: return True
        if isinstance(other, Number): return False
        return Number.__eq__(self, other)

    def __lt__(self, other):
        other = Symbolic(other)
        if self is other: return False
        if isinstance(other, Number):
            return (other-self).is_positive()
        return Number.__lt__(self, other)

#
# End of Half class
#
################################################################################

class One(ConstantSingleton, Integer):
    """ Represents number 1.

    Operations:
      obj ** 1 -> obj
      1 * obj -> obj
      obj / 1 -> obj
    """

    ###########################################################################
    #
    # Constructor methods
    #
    
    numer = 1
    denom = 1

    def eval_power(base, exponent):
        """
        exponent is symbolic object but not equal to 0, 1
        
        1 ** oo, 1 ** nan, 1 ** number, 1 ** obj  -> 1
        """
        return base

    ############################################################################
    #
    # Informational methods
    #

    def is_negative(self): return False
    def is_positive(self): return True

    ###########################################################################
    #
    # Transformation methods
    #

    def _todecimal(self):
        return decimal.Decimal(1)

    ############################################################################
    #
    # Relational methods
    #

    def __eq__(self, other):
        other = Symbolic(other)
        if self is other: return True
        if isinstance(other, Number): return False
        return Number.__eq__(self, other)

    def __lt__(self, other):
        other = Symbolic(other)
        if self is other: return False
        if isinstance(other, Number):
            return (other-self).is_positive()
        return Number.__lt__(self, other)

    ############################################################################
    #
    # Arithmetic operations
    #

    def __neg__(self): return NegativeOne()
    def __mul__(self, other): return other
    __rmul__ = __mul__
    __pow__ = eval_power

    def __rdiv__(self, other): return other

#
# End of One class
#
################################################################################


class NegativeOne(ConstantSingleton, Integer):
    """ Represents number -1.

    Operations:
      -(-1) -> 1
      (-1) * obj -> -obj
      obj / (-1) -> -obj
      (-1) ** inf -> nan
      0 ** -1 -> inf
      nan ** -1 -> nan
      inf ** -1 -> 0
      0 ** -1 -> inf
    """

    ###########################################################################
    #
    # Constructor methods
    #

    numer = -1
    denom = 1

    def eval_power(base, exponent):
        """
        exponent is symbolic object but not equal to 0, 1
        
        (-1) ** d -> sin(d*Pi) + cos(d*Pi) * I, d is decimal
        (-1) ** nan -> nan
        (-1) ** oo  -> nan
        (-1) ** -oo -> nan
        (-1) ** e   -> 1 if e is even
        (-1) ** o   -> -1 if o is odd
        (-1) ** (1/2) -> I
        (-1) ** (n/2) -> I ** n
        (-1) ** (n/d) -> (-1) ** q * (-1) ** (n/d - q), q = n//d != 0
        """
        if isinstance(exponent, Number):
            if isinstance(exponent, Decimal):
                a = exponent.num * decimal_math.pi()
                s = decimal_math,sin(a)
                c = decimal_math,cos(a)
                return Decimal(s) + Decimal(c) * Symbolic.ImaginaryUnit()
            if isinstance(exponent, NaN):
                return NaN()
            if isinstance(exponent, (Infinity, NegativeInfinity)):
                return NaN()
            if isinstance(exponent, Integer):
                if exponent.is_odd(): return NegativeOne()
                return One()
            if isinstance(exponent, Half):
                return Symbolic.ImaginaryUnit()
            if isinstance(exponent, Rational):
                if exponent.denom == 2:
                    return Symbolic.ImaginaryUnit() ** Integer(exponent.numer)
                q = int(exponent)
                if q:
                    q = Integer(q)
                    return base ** q * base ** (exponent - q)
        return

    ############################################################################
    #
    # Informational methods
    #

    def is_positive(self): return False
    def is_negative(self): return True

    ###########################################################################
    #
    # Transformation methods
    #

    def _todecimal(self):
        return decimal.Decimal(-1)

    ############################################################################
    #
    # Relational methods
    #

    def __eq__(self, other):
        other = Symbolic(other)
        if self is other: return True
        if isinstance(other, Number): return False
        return Number.__eq__(self, other)

    def __lt__(self, other):
        other = Symbolic(other)
        if self is other: return False
        if isinstance(other, Number):
            return (other-self).is_positive()
        return Number.__lt__(self, other)

    ############################################################################
    #
    # Arithmetic operations
    #

    def __neg__(self): return One()
    def __mul__(self, other):
        if self is other: return One()
        return -other
    __rmul__ = __mul__

    def __rdiv__(self, other): return -other

#
# End of NegativeOne class
#
################################################################################

class NaN(ConstantSingleton, Rational):
    """ Represents undefined quantity.

    Operations:
      all operations with NaN() instance return NaN() except...
      1 ** nan -> 1
    """

    ###########################################################################
    #
    # Constructor methods
    #

    numer = 0
    denom = 0

    def eval_power(base, exponent):
        """
        exponent is symbolic object but not equal to 0, 1
        """
        return NaN()

    ############################################################################
    #
    # Informational methods
    #

    def is_negative(self): return False
    def is_positive(self): return False

    ###########################################################################
    #
    # Transformation methods
    #

    def tostr(self, level=0):
        return 'NaN'

    def _todecimal(self):
        return decimal.Decimal('NaN')

    ############################################################################
    #
    # Relational methods
    #

    #def __eq__(self, other):
    #    return False
    #__ne__ = __lt__ = __gt__ = __le__ = __ge__ = __eq__

    ############################################################################
    #
    # Arithmetic operations
    #

    def __pos__(self): return self
    def __neg__(self): return self
    def __add__(self, other):
        if isinstance(other, integer_types + (Number,)):
            return self
        return Number.__add__(self, other)
    def __sub__(self, other):
        if isinstance(other, integer_types + (Number,)):
            return self
        return Number.__sub__(self, other)
    def __mul__(self, other):
        if isinstance(other, integer_types + (Number,)):
            return self
        return Number.__mul__(self, other)
    def __div__(self, other):
        if isinstance(other, integer_types + (Number,)):
            return self
        return Number.__div__(self, other)
    def __rmul__(self, other):
        if isinstance(other, integer_types + (Number,)):
            return self
        return Number.__rmul__(self, other)
    def __rdiv__(self, other):
        if isinstance(other, integer_types + (Number,)):
            return self
        return Number.__rdiv__(self, other)
    def __radd__(self, other):
        if isinstance(other, integer_types + (Number,)):
            return self
        return Number.__radd__(self, other)
    def __rsub__(self, other):
        if isinstance(other, integer_types + (Number,)):
            return self
        return Number.__rsub__(self, other)

#
# End of NaN class
#
################################################################################

class Infinity(ConstantSingleton, Rational):
    """ Represents infinity +oo.

    oo and -oo are singletons.
    
    Operations:
      -(oo) -> -oo
      0 * oo -> nan
      number * oo  -> sign(number) * oo
      oo - oo -> nan
      oo + number -> oo
      oo ** -number -> 0
      oo ** 0 -> nan
      (-1)**oo -> nan
    """
    ###########################################################################
    #
    # Constructor methods
    #
    
    numer = 1
    denom = 0

    def eval_power(base, exponent):
        """
        exponent is symbolic object but not equal to 0, 1

        oo ** nan -> nan
        oo ** (-p) -> 0, p is number, oo
        """
        if isinstance(exponent, Number):
            if isinstance(exponent, NaN):
                return NaN()
            if exponent.is_negative():
                return Zero()
            if exponent.is_positive():
                return Infinity()
        if not exponent.symbols():
            d = exponent.todecimal()
            if isinstance(d, Number):
                return base ** d
        return

    ############################################################################
    #
    # Informational methods
    #

    def is_negative(self): return False
    def is_positive(self): return True

    ###########################################################################
    #
    # Transformation methods
    #

    def tostr(self, level=0):
        return 'Inf'

    def _todecimal(self):
        return decimal.Decimal('Infinity')

    ############################################################################
    #
    # Relational methods
    #

    def __eq__(self, other):
        other = Symbolic(other)
        if self is other: return True
        if isinstance(other, Number):
            return False
        return Number.__eq__(self, other)

    def __lt__(self, other):
        other = Symbolic(other)
        if isinstance(other, Number): return False
        return Number.__lt__(self, other)

    ############################################################################
    #
    # Arithmetic operations
    #

    def __neg__(self): return NegativeInfinity()

    def __add__(self, other):
        if isinstance(other, (NaN, NegativeInfinity)): return NaN()
        if isinstance(other, (Number,)+integer_types): return self
        return Number.__add__(self, other)

    def __mul__(self, other):
        if isinstance(other, (NaN,Zero)): return NaN()
        if isinstance(other, (Infinity,NegativeInfinity)): return other
        sign = None
        if isinstance(other, integer_types): sign = cmp(other,0)
        elif isinstance(other, Number): sign = cmp(other.numer,0)
        if sign is not None:
            if sign > 0: return self
            if sign < 0: return NegativeInfinity()
            return NaN()
        return Number.__mul__(self, other)

#
# End of Infinity class
#
################################################################################

class NegativeInfinity(ConstantSingleton, Rational):
    """ Represents -oo.
    """
    
    ###########################################################################
    #
    # Constructor methods
    #

    numer = -1
    denom = 0

    def eval_power(base, exponent):
        """
        exponent is symbolic object but not equal to 0, 1

        (-oo) ** nan -> nan
        (-oo) ** oo  -> nan
        (-oo) ** (-oo) -> nan
        (-oo) ** e -> oo, e is positive even integer
        (-oo) ** o -> -oo, o is positive odd integer
        
        """
        if isinstance(exponent, Number):
            if isinstance(exponent, (NaN, Infinity, NegativeInfinity)):
                return NaN()
            if isinstance(exponent, Integer):
                if exponent.is_positive():
                    if exponent.is_odd():
                        return NegativeInfinity()
                    return Infinity()
            return NegativeOne()**exponent * Infinity() ** exponent
        return
        
    ############################################################################
    #
    # Informational methods
    #

    def is_negative(self): return True
    def is_positive(self): return False

    ###########################################################################
    #
    # Transformation methods
    #

    def tostr(self, level=0):
        precedence = self.get_precedence()
        if precedence<=level:
            return '(-Inf)'
        return '-Inf'

    def _todecimal(self):
        return decimal.Decimal('-Infinity')

    ############################################################################
    #
    # Relational methods
    #

    def __eq__(self, other):
        other = Symbolic(other)
        if self is other: return True
        if isinstance(other, Number): return False
        return Number.__eq__(self, other)

    def __lt__(self, other):
        other = Symbolic(other)
        if isinstance(other, Number): return True
        return Number.__lt__(self, other)

    ############################################################################
    #
    # Arithmetic operations
    #

    def __neg__(self): return Infinity()

    def __add__(self, other):
        if isinstance(other, (NaN, Infinity)): return NaN()
        if isinstance(other, (Number,)+integer_types): return self
        return Number.__add__(self, other)

    def __mul__(self, other):
        if isinstance(other, (NaN,Zero)): return NaN()
        if isinstance(other, Infinity): return self
        if isinstance(other, NegativeInfinity): return Infinity()
        sign = None
        if isinstance(other, integer_types): sign = cmp(other,0)
        elif isinstance(other, Number): sign = cmp(other.numer,0)
        if sign is not None:
            if sign > 0: return self
            if sign < 0: return Infinity()
            return NaN()
        return Number.__mul__(self, other)

#
# End of NegativeInfinity class
#
################################################################################

    
Symbolic.singleton_classes['NaN'] = NaN
Symbolic.singleton_classes['infinity'] = Infinity

Symbolic.Number = Number
Symbolic.Decimal = Decimal
Symbolic.Rational = Rational
Symbolic.Integer = Integer
Symbolic.One = One
Symbolic.NegativeOne = NegativeOne
Symbolic.Half = Half
Symbolic.Zero = Zero
Symbolic.NaN = NaN
Symbolic.Infinity = Infinity
Symbolic.NegativeInfinity = NegativeInfinity


# EOF
