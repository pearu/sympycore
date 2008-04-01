#
# Created January 2008 by Fredrik Johansson
#
""" Provides elementary calculus functions sqrt, exp, log, sin, etc and constants pi, E.
"""

__all__ = ['sqrt', 'exp', 'log', 'sin', 'cos', 'tan', 'cot', 'sign', 'mod',
           'E', 'pi', 'gamma']
__docformat__ = "restructuredtext"

from ..algebra import Calculus, I,  NUMBER, TERMS, FACTORS, SYMBOL, TERMS
from ..infinity import oo, undefined, CalculusInfinity
from ..constants import const_pi, const_E, const_gamma
from ..function import Function
from ...arithmetic.evalf import evalf
from ...arithmetic.numbers import complextypes, realtypes, inttypes
from ...arithmetic.number_theory import factorial
from ...arithmetic import infinity

import math

zero = Calculus.zero
one = Calculus.one
half = one/2
sqrt2 = Calculus.convert('2**(1/2)')
sqrt3 = Calculus.convert('3**(1/2)')

#---------------------------------------------------------------------------#
#                                  Exponentials                             #
#---------------------------------------------------------------------------#

pi = const_pi.as_algebra(Calculus)
E = const_E.as_algebra(Calculus)
gamma = const_gamma.as_algebra(Calculus)

Ipi = I*pi
Ipi2 = Ipi/2

class sign(Function):
    def __new__(cls, arg):
        if not isinstance(arg, Calculus):
            arg = Calculus.convert(arg)
        return Calculus(cls, arg)

class mod(Function):
    def __new__(cls, x, y):
        if not isinstance(x, Calculus):
            x = Calculus.convert(x)
        if not isinstance(y, Calculus):
            y = Calculus.convert(y)
        xh,xd = x.pair
        yh,yd = y.pair
        if xh is NUMBER and yh is NUMBER:
            return Calculus.convert(xd % yd)
        return Calculus(cls, (x, y))

class sqrt(Function):
    def __new__(cls, arg):
        return arg ** half

class exp(Function):
    def __new__(cls, arg):
        return E ** arg

    @staticmethod
    def derivative(arg):
        return E ** arg

log_number_table = {
    zero.data : -oo,
    one.data : zero,
    I.data : Ipi2,
    (-I).data : -Ipi2
}

class log(Function):
    def __new__(cls, arg, base=E):
        if type(arg) is not Calculus:
            if isinstance(arg, CalculusInfinity):
                if arg == oo:
                    return oo
                if arg == undefined:
                    return undefined
                return Calculus(cls, arg)
            else:
                arg = Calculus.convert(arg)
        if base != E:
            base = Calculus.convert(base)
            bd = base.data
            ad = arg.data
            if base.head is NUMBER and isinstance(bd, inttypes) and \
                arg.head is NUMBER and isinstance(ad, inttypes) and \
                ad > 0 and bd > 1:
                l = int(math.log(ad, bd) + 0.5)
                if bd**l == ad:
                    return Calculus.convert(l)
            return cls(arg) / cls(base)
        head = arg.head
        data = arg.data
        if head is NUMBER:
            v = log_number_table.get(data)
            if v is not None:
                return v
            if isinstance(data, realtypes) and data < 0:
                return Ipi + log(-arg)
            if isinstance(data, complextypes) and data.real == 0:
                im = data.imag
                if im > 0: return Calculus(cls, Calculus(NUMBER, im)) + Ipi2
                if im < 0: return Calculus(cls, Calculus(NUMBER, -im)) - Ipi2
            return Calculus(cls, arg)
        if arg == E:
            return one
        from ..relational import is_positive
        if head is FACTORS and len(data) == 1:
            base, expt = data.items()[0]
            if is_positive(base) and isinstance(expt, realtypes):
                return Calculus(cls, base) * expt
        if head is TERMS and len(data) == 1:
            term, coeff = data.items()[0]
            if (isinstance(coeff, realtypes) and coeff < 0) and is_positive(base):
                return Ipi + log(-arg)
        return Calculus(cls, arg)

    @classmethod
    def derivative(cls, arg):
        return 1/arg

    @classmethod
    def nth_derivative(cls, arg, n=1):
        return (-1)**(n-1) * factorial(n-1) * arg**(-n)

#---------------------------------------------------------------------------#
#                          Trigonometric functions                          #
#---------------------------------------------------------------------------#

# Tabulated values of sin(x) at multiples of pi/12
C0 = (sqrt3-1)/(2*sqrt2)
C1 = one/2
C2 = sqrt2/2
C3 = sqrt3/2
C4 = (sqrt3+1)/(2*sqrt2)

# Replace entries with None to prevent from evaluating
sine_table = [ \
  Calculus.zero, C0, C1, C2, C3, C4, Calculus.one, C4, C3, C2, C1,C0,
  Calculus.zero,-C0,-C1,-C2,-C3,-C4,-Calculus.one,-C4,-C3,-C2,-C1,-C0]

def get_pi_shift(arg, N):
    """Parse as x, n where arg = x + n*pi/N"""
    if arg.head is TERMS:
        # Optimizing for len == 1 gives 2x speedup in simple cases
        if len(arg.data) == 1:
            e, c = arg.data.items()[0]
            if e == pi:
                c *= N
                if isinstance(c, (int, long)):
                    return zero, c
        c = arg.data.get(pi)
        if c is not None:
            c *= N
            if isinstance(c, (int, long)):
                d = arg.data.copy()
                d.pop(pi)
                return Calculus.Terms(*d.items()), c
        return arg, 0
    if arg == pi:
        return zero, N
    return arg, 0

def has_leading_sign(arg):
    """Detect symmetry cases for odd/even functions."""
    if arg.head is NUMBER:
        if arg < 0:
            return True
    if arg.head is TERMS and len(arg.data) == 1:
        e, c = arg.data.items()[0]
        if c < 0:
            return True
    return None

class TrigonometricFunction(Function):

    parity = None   # 'even' or 'odd'
    period = None   # multiple of pi

    def __new__(cls, arg):
        if type(arg) is not Calculus:
            if isinstance(arg, CalculusInfinity):
                if arg == undefined:
                    return undefined
                return Calculus(cls, arg)
            else:
                arg = Calculus.convert(arg)
        x, m = get_pi_shift(arg, 12)
        m %= (12*cls.period)
        if x == zero:
            v = cls.eval_direct(m)
            if v is not None:
                return v
        period = cls.period
        negate_result = False
        # Full-period symmetry
        if not m % (12*period):
            arg = x
        else:
            # Half-period symmetry
            if not m % 12:
                arg = x
                negate_result = True
            # Quarter-period symmetry
            elif not m % 6:
                f = conjugates[cls]
                sign = (-1)**((((m-6)//12) % period) + (f.parity == 'odd'))
                return sign * f(x)
        if has_leading_sign(arg):
            arg = -arg
            negate_result ^= (cls.parity == 'odd')
        if negate_result:
            return -Calculus(cls, arg)
        else:
            return Calculus(cls, arg)

class sin(TrigonometricFunction):
    parity = 'odd'
    period = 2
    @classmethod
    def eval_direct(cls, m):
        return sine_table[m % 24]

    @classmethod
    def derivative(cls, arg, n=1):
        if n == 1:
            return cos(arg)

    @classmethod
    def nth_derivative(cls, arg, n):
        return sin(arg + n*pi/2)

class cos(TrigonometricFunction):
    parity = 'even'
    period = 2

    @classmethod
    def eval_direct(cls, m):
        return sine_table[(m+6) % 24]

    @classmethod
    def derivative(cls, arg, n=1):
        return -sin(arg)

    @classmethod
    def nth_derivative(cls, arg, n=1):
        return cos(arg + n*pi/2)

class tan(TrigonometricFunction):
    parity = 'odd'
    period = 1

    @classmethod
    def eval_direct(cls, m):
        a = sine_table[m % 24]
        b = sine_table[(m+6) % 24]
        if a == None or b == None:
            return
        return a / b

    @classmethod
    def derivative(cls, arg):
        return 1+tan(arg)**2

class cot(TrigonometricFunction):
    parity = 'odd'
    period = 1

    @classmethod
    def eval_direct(cls, m):
        a = sine_table[m % 24]
        b = sine_table[(m+6) % 24]
        if a == None or b == None:
            return
        return b / a

    @classmethod
    def derivative(cls, arg, n=1):
        return -(1+cot(arg)**2)

# pi/2-x symmetry
conjugates = {
  sin : cos,
  cos : sin,
  tan : cot,
  cot : tan
}
