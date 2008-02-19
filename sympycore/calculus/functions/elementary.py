#
# Created January 2008 by Fredrik Johansson
#

from ..algebra import A, oo, I, undefined, NUMBER, ADD, MUL, SYMBOL
from ..constants import const_pi, const_E
from ..function import Function
from ...arithmetic.evalf import evalf, Float
from ...arithmetic.numbers import Complex, realtypes, inttypes

def is_positive(x):
    from ..relational import no_assumptions
    return no_assumptions.positive(x)

import math

zero = A(0)
one = A(1)
half = one/2
sqrt2 = A('2**(1/2)')
sqrt3 = A('3**(1/2)')

#---------------------------------------------------------------------------#
#                                  Exponentials                             #
#---------------------------------------------------------------------------#

pi = const_pi.as_algebra(A)
E = const_E.as_algebra(A)

Ipi = I*pi
Ipi2 = Ipi/2

class sqrt(Function):
    def __new__(cls, arg):
        if not isinstance(arg, A):
            arg = A.convert(arg)
        return A.Pow(arg, half)

class exp(Function):
    def __new__(cls, arg):
        if not isinstance(arg, A):
            arg = A.convert(arg)
        return A.Pow(E, arg)

    @classmethod
    def derivative(cls, arg):
        return exp(arg)

log_number_table = {
    zero.data : -oo,
    one.data : zero,
    oo.data : oo,
    undefined.data : undefined,
    I.data : Ipi2,
    (-I).data : -Ipi2
}

class log(Function):
    def __new__(cls, arg, base=E):
        if not isinstance(arg, A):
            arg = A.convert(arg)
        if base != E:
            base = A.convert(base)
            bd = base.data
            ad = arg.data
            if base.head is NUMBER and isinstance(bd, inttypes) and \
                arg.head is NUMBER and isinstance(ad, inttypes) and \
                ad > 0 and bd > 1:
                l = int(math.log(ad, bd) + 0.5)
                if bd**l == ad:
                    return A(l)
            return cls(arg) / cls(base)
        head = arg.head
        data = arg.data
        if head is NUMBER:
            v = log_number_table.get(data)
            if v is not None:
                return v
            if isinstance(data, realtypes) and data < 0:
                return Ipi + log(-arg)
            if isinstance(data, Complex) and data.real == 0:
                im = data.imag
                if im > 0: return A(A(im, head=NUMBER), head=cls) + Ipi2
                if im < 0: return A(A(-im, head=NUMBER), head=cls) - Ipi2
            return A(arg, head=cls)
        if arg == E:
            return one
        if head is MUL and len(data) == 1:
            base, expt = data.items()[0]
            if is_positive(base) and isinstance(expt, realtypes):
                return A(base, head=cls) * expt
        if head is ADD and len(data) == 1:
            term, coeff = data.items()[0]
            if (isinstance(coeff, realtypes) and coeff < 0) and is_positive(base):
                return Ipi + log(-arg)
        return A(arg, head=cls)

    @classmethod
    def derivative(cls, arg):
        return 1/arg

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
  A(0), C0, C1, C2, C3, C4, A(1), C4, C3, C2, C1,C0,
  A(0),-C0,-C1,-C2,-C3,-C4,-A(1),-C4,-C3,-C2,-C1,-C0]

def get_pi_shift(arg, N):
    """Parse as x, n where arg = x + n*pi/N"""
    if arg.head is ADD:
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
                return A.Terms(*d.items()), c
        return arg, 0
    if arg == pi:
        return zero, N
    return arg, 0

def has_leading_sign(arg):
    """Detect symmetry cases for odd/even functions."""
    if arg.head is NUMBER:
        if arg < 0:
            return True
    if arg.head is ADD and len(arg.data) == 1:
        e, c = arg.data.items()[0]
        if c < 0:
            return True
    return None

class TrigonometricFunction(Function):

    parity = None   # 'even' or 'odd'
    period = None   # multiple of pi

    def __new__(cls, arg):
        if not isinstance(arg, A):
            arg = A.convert(arg)
        if arg.is_Number and isinstance(arg.data, Float):
            return A.Number(evalf('%s(%s)' % (cls.__name__, arg)))
        x, m = get_pi_shift(arg, 12)
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
                sign = (-1)**(((m-6)//12) % period)
                return sign * conjugates[cls](-x)
        if has_leading_sign(arg):
            arg = -arg
            negate_result ^= (cls.parity == 'odd')
        if negate_result:
            return -A(arg, head=cls)
        else:
            return A(arg, head=cls)

class sin(TrigonometricFunction):
    parity = 'odd'
    period = 2
    @classmethod
    def eval_direct(cls, m):
        return sine_table[m % 24]

    @classmethod
    def derivative(cls, arg):
        return cos(arg)

class cos(TrigonometricFunction):
    parity = 'even'
    period = 2
    @classmethod
    def eval_direct(cls, m):
        return sine_table[(m+6) % 24]

    @classmethod
    def derivative(cls, arg):
        return -sin(arg)

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
    def eval_direct(cls, arg):
        a = sine_table[m % 24]
        b = sine_table[(m+6) % 24]
        if a == None or b == None:
            return
        return b / a

    @classmethod
    def derivative(cls, arg):
        return -(1+cot(arg)**2)

# pi/2-x symmetry
conjugates = {
  sin : cos,
  cos : sin,
  tan : cot,
  cot : tan
}
