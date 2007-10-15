"""
This module contains "low-level" functions for multiprecision floating-
point arithmetic implemented in pure Python. The code is entirely self-
contained, so it can be used by other projects without requiring the
rest of SymPy to be present.

The code is written in a functional style for simplicity and speed.
The only data structures used are tuples. High-level classes with
methods like __add__, etc are left to the user to implement according
to his or her own convenience. (Avoiding objects makes the arithmetic
run twice as fast in some cases.)

A floating-point number x = man * 2**exp is represented by the tuple
(man, exp, bc) where man is the mantissa, exp is the exponent, and bc
is the number of bits in the mantissa.
"""


#----------------------------------------------------------------------------#
#                                                                            #
#                             General utilities                              #
#                                                                            #
#----------------------------------------------------------------------------#

import math
import decimal

# Same as standard Python float
STANDARD_PREC = 53


# All supported rounding modes. We define them as integer constants for easy
# management, but change __repr__ to give more information on inspection

class RoundingMode(int):
    def __new__(cls, level, name):
        a = int.__new__(cls, level)
        a.name = name
        return a
    def __repr__(self): return self.name

ROUND_DOWN    = RoundingMode(1, 'ROUND_DOWN')
ROUND_UP      = RoundingMode(2, 'ROUND_UP')
ROUND_FLOOR   = RoundingMode(3, 'ROUND_FLOOR')
ROUND_CEILING = RoundingMode(4, 'ROUND_CEILING')
ROUND_HALF_UP = RoundingMode(5, 'ROUND_HALF_UP')
ROUND_HALF_DOWN = RoundingMode(6, 'ROUND_HALF_DOWN')
ROUND_HALF_EVEN = RoundingMode(7, 'ROUND_HALF_EVEN')


def _quadratic_steps(start, target):
    # generate list of precision steps for quadratically convergent algorithms
    L = [target]
    while L[-1] > start*2:
        L = L + [L[-1]//2 + 1]
    return L[::-1]


#----------------------------------------------------------------------------#
#                                                                            #
#                             Radix conversion                               #
#                                                                            #
#----------------------------------------------------------------------------#

LOG2_10 = math.log(10,2)  # 3.3219...

# TODO: only binary_to_decimal is used currently. Things could be sped
# up by using the other functions below, currently used only by the
# pidigits.py demo

def binary_to_decimal(man, exp, n):
    """Represent as a decimal string with at most n digits"""
    import decimal
    prec_ = decimal.getcontext().prec
    decimal.getcontext().prec = n
    if exp >= 0: d = decimal.Decimal(man) * (1<<exp)
    else:        d = decimal.Decimal(man) / (1<<-exp)
    a = str(d)
    decimal.getcontext().prec = prec_
    return a

def bin_to_radix(x, xbits, base, bdigits):
    return x * (base**bdigits) >> xbits

_numerals = '0123456789abcdefghijklmnopqrstuvwxyz'

def small_numeral(n, base=10):
    # Calculate numeral of n*(base**digits) in the given base
    if base == 10:
        return str(n)
    digs = []
    while n:
        n, digit = divmod(n, base)
        digs.append(_numerals[digit])
    return "".join(digs[::-1])

global_options = {}

# TODO: speed up for bases 2, 4, 8, 16, ...
def fixed_to_str(x, base, digits):
    if digits < 789:
        return small_numeral(x, base)
    half = (digits // 2) + (digits & 1)
    if "verbose" in global_options and half > 50000:
        print "  dividing..."
    A, B = divmod(x, base**half)
    ad = fixed_to_str(A, base, half)
    bd = fixed_to_str(B, base, half).rjust(half, "0")
    return ad + bd


#----------------------------------------------------------------------------#
#                                                                            #
#                          Bit manipulation, etc                             #
#                                                                            #
#----------------------------------------------------------------------------#

def make_fixed(s, prec):
    """Convert a floating-point number to a fixed-point big integer"""
    man, exp, bc = s
    offset = exp + prec
    if offset >= 0:
        return man << offset
    else:
        return man >> (-offset)

def bitcount(n, log=math.log, table=(0,1,2,2,3,3,3,3,4,4,4,4,4,4,4,4)):
    """Give size of n in bits; i.e. the position of the highest set bit
    in n. If n is negative, the absolute value is used. The bitcount of
    zero is taken to be 0."""

    if not n: return 0
    if n < 0: n = -n

    # math.log gives a good estimate, and never overflows, but
    # is not always exact. Subtract 2 to underestimate, then
    # count remaining bits by table lookup
    bc = int(log(n, 2)) - 2
    if bc < 0:
        bc = 0
    return bc + table[n >> bc]

def trailing_zeros(n):
    """Count trailing zero bits in an integer. If n is negative, it is
    replaced by its absolute value."""
    if n & 1: return 0
    if not n: return 0
    if n < 0: n = -n
    t = 0
    while not n & 0xffffffffffffffff: n >>= 64; t += 64
    while not n & 0xff: n >>= 8; t += 8
    while not n & 1: n >>= 1; t += 1
    return t

def _rshift(x, n):
    # quick right shift with default rounding
    if n >= 0: return x >> n
    else:      return x << (-n)

def _lshift(x, n):
    # quick left shift with default rounding
    if n >= 0: return x << n
    else:      return x >> (-n)

def rshift(x, n, mode):
    """Shift x n bits to the right (i.e., calculate x/(2**n)), and
    round to the nearest integer in accordance with the specified
    rounding mode. The exponent n may be negative, in which case x is
    shifted to the left (and no rounding is necessary)."""

    if not n or not x:
        return x
    # Support left-shifting (no rounding needed)
    if n < 0:
        return x << -n

    # To get away easily, we exploit the fact that Python rounds positive
    # integers toward zero and negative integers away from zero when dividing
    # or shifting. The simplest rounding modes can be handled entirely through
    # shifts:
    if mode < ROUND_HALF_UP:
        if mode == ROUND_DOWN:
            if x > 0: return x >> n
            else:     return -((-x) >> n)
        if mode == ROUND_UP:
            if x > 0: return -((-x) >> n)
            else:     return x >> n
        if mode == ROUND_FLOOR:
            return x >> n
        if mode == ROUND_CEILING:
            return -((-x) >> n)

    # Here we need to inspect the bits around the cutoff point
    if x > 0: t = x >> (n-1)
    else:     t = (-x) >> (n-1)
    if t & 1:
        if mode == ROUND_HALF_UP or \
           (mode == ROUND_HALF_DOWN and x & ((1<<(n-1))-1)) or \
           (mode == ROUND_HALF_EVEN and (t&2 or x & ((1<<(n-1))-1))):
            if x > 0:  return (t>>1)+1
            else:      return -((t>>1)+1)
    if x > 0: return t>>1
    else:     return -(t>>1)

def normalize(man, exp, prec=STANDARD_PREC, rounding=ROUND_HALF_EVEN):
    """Normalize the binary floating-point number represented by
    man * 2**exp to the specified precision level, rounding according
    to the specified rounding mode if necessary. The mantissa is also
    stripped of trailing zero bits, and its bits are counted. The
    returned value is a tuple (man, exp, bc)."""
    if not man:
        return 0, 0, 0
    bc = bitcount(man)
    if bc > prec:
        man = rshift(man, bc-prec, rounding)
        exp += (bc - prec)
        bc = prec
    # Strip trailing zeros
    if not man & 1:
        tr = trailing_zeros(man)
        if tr:
            man >>= tr
            exp += tr
            bc -= tr
    if not man:
        return 0, 0, 0
    return man, exp, bc

#----------------------------------------------------------------------------#
#                                                                            #
#                            Type conversion                                 #
#                                                                            #
#----------------------------------------------------------------------------#

def float_from_int(n, prec=STANDARD_PREC, rounding=ROUND_HALF_EVEN):
    return normalize(n, 0, prec, rounding)

def float_from_rational(p, q, prec=STANDARD_PREC, rounding=ROUND_HALF_EVEN):
    """Create floating-point number from a rational number p/q"""
    n = prec + bitcount(q) + 2
    return normalize((p<<n)//q, -n, prec, rounding)

def float_from_pyfloat(x, prec=STANDARD_PREC, rounding=ROUND_HALF_EVEN):
    # We assume that a float mantissa has 53 bits
    m, e = math.frexp(x)
    return normalize(int(m*(1<<53)), e-53, prec, rounding)

def float_to_int(s):
    man, exp, bc = s
    return rshift(man, -exp, ROUND_DOWN)

def float_to_pyfloat(s):
    """Convert to a Python float. May raise OverflowError."""
    man, exp, bc = s
    try:
        return math.ldexp(man, exp)
    except OverflowError:
        # Try resizing the mantissa. Overflow may still happen here.
        n = bc - 53
        m = man >> n
        return math.ldexp(m, exp + n)

def float_to_rational(s):
    """Return p/q such that s = p/q exactly. p and q are not reduced
    to lowest terms."""
    man, exp, bc = s
    if exp > 0:
        return man * 2**exp, 1
    else:
        return man, 2**-exp


fzero = float_from_int(0)
fone = float_from_int(1)
ftwo = float_from_int(2)
fhalf = float_from_rational(1, 2)
assert fhalf == float_from_pyfloat(0.5)


#----------------------------------------------------------------------------#
#                                                                            #
#                                Comparison                                  #
#                                                                            #
#----------------------------------------------------------------------------#

def feq(s, t):
    """Floating-point equality testing. The numbers are assumed to
    be normalized, meaning that this simply performs tuple comparison."""
    return s == t

def fcmp(s, t):
    """Floating-point comparison. Return -1 if s < t, 0 if s == t,
    and 1 if s > t."""

    # An inequality between two numbers s and t is determined by looking
    # at the value of s-t. A full floating-point subtraction is relatively
    # slow, so we first try to look at the exponents and signs of s and t.
    sman, sexp, sbc = s
    tman, texp, tbc = t

    # Very easy cases: check for 0's and opposite signs
    if not tman: return cmp(sman, 0)
    if not sman: return cmp(0, tman)
    if sman > 0 and tman < 0: return 1
    if sman < 0 and tman > 0: return -1

    # In this case, the numbers likely have the same magnitude
    if sexp == texp: return cmp(sman, tman)

    # The numbers have the same sign but different exponents. In this
    # case we try to determine if they are of different magnitude by
    # checking the position of the highest set bit in each number.
    a = sbc + sexp
    b = tbc + texp
    if sman > 0:
        if a < b: return -1
        if a > b: return 1
    else:
        if a < b: return 1
        if a < b: return -1

    # The numbers have similar magnitude but different exponents.
    # So we subtract and check the sign of resulting mantissa.
    return cmp(fsub(s, t, prec=5)[0], 0)


#----------------------------------------------------------------------------#
#                                                                            #
#                            Basic arithmetic                                #
#                                                                            #
#----------------------------------------------------------------------------#

def fadd(s, t, prec=STANDARD_PREC, rounding=ROUND_HALF_EVEN):
    """Floating-point addition. Given two tuples s and t containing the
    components of floating-point numbers, return their sum rounded to 'prec'
    bits using the 'rounding' mode, represented as a tuple of components."""

    #  General algorithm: we set min(s.exp, t.exp) = 0, perform exact integer
    #  addition, and then round the result.
    #                   exp = 0
    #                       |
    #                       v
    #          11111111100000   <-- s.man (padded with zeros from shifting)
    #      +        222222222   <-- t.man (no shifting necessary)
    #          --------------
    #      =   11111333333333

    # We assume that s has the higher exponent. If not, just switch them:
    if t[1] > s[1]:
        s, t = t, s

    sman, sexp, sbc = s
    tman, texp, tbc = t

    # Check if one operand is zero. Float(0) always has exp = 0; if the
    # other operand has a large exponent, its mantissa will unnecessarily
    # be shifted a huge number of bits if we don't check for this case.
    if not tman:
        return normalize(sman, sexp, prec, rounding)
    if not sman:
        return normalize(tman, texp, prec, rounding)

    # More generally, if one number is huge and the other is small,
    # and in particular, if their mantissas don't overlap at all at
    # the current precision level, we can avoid work.

    #       precision
    #    |            |
    #     111111111
    #  +                 222222222
    #     ------------------------
    #  #  1111111110000...

    # However, if the rounding isn't to nearest, correct rounding mandates
    # the result should be adjusted up or down. This is not yet implemented.

    if sexp - texp > 100:
        bitdelta = (sbc+sexp)-(tbc+texp)
        if bitdelta > prec + 5:
            # TODO: handle rounding here
            return normalize(sman, sexp, prec, rounding)

    # General case
    return normalize(tman+(sman<<(sexp-texp)), texp, prec, rounding)


def fsub(s, t, prec=STANDARD_PREC, rounding=ROUND_HALF_EVEN):
    """Floating-point subtraction"""
    return fadd(s, (-t[0], t[1], t[2]), prec, rounding)

def fneg(s, prec=STANDARD_PREC, rounding=ROUND_HALF_EVEN):
    """Floating-point negation. In addition to changing sign, rounds to
    the specified precision."""
    return normalize(-s[0], s[1], prec, rounding)


def fmul(s, t, prec=STANDARD_PREC, rounding=ROUND_HALF_EVEN):
    """Floating-point multiplication"""

    sman, sexp, sbc = s
    tman, texp, tbc = t

    # This is very simple. A possible optimization would be to throw
    # away some bits when prec is much smaller than sbc+tbc
    return normalize(sman*tman, sexp+texp, prec, rounding)


def fdiv(s, t, prec=STANDARD_PREC, rounding=ROUND_HALF_EVEN):
    """Floating-point division"""
    sman, sexp, sbc = s
    tman, texp, tbc = t

    # Perform integer division between mantissas. The mantissa of s must
    # be padded appropriately to preserve accuracy. Note: this algorithm
    # could produce wrong rounding in some corner cases.
    extra = prec - sbc + tbc + 4
    if extra < 0:
        extra = 0

    return normalize((sman<<extra)//tman, sexp-texp-extra, prec, rounding)


def fpow(s, n, prec=STANDARD_PREC, rounding=ROUND_HALF_EVEN):
    """Compute s**n, where n is an integer"""
    n = int(n)
    if n == 0: return fone
    if n == 1: return normalize(s[0], s[1], prec, rounding)
    if n == 2: return fmul(s, s, prec, rounding)
    if n == -1: return fdiv(fone, s, prec, rounding)
    if n < 0:
        return fdiv(fone, fpow(s, -n, prec+3, ROUND_FLOOR), prec, rounding)
    # Now we perform binary exponentiation. Need to estimate precision
    # to avoid rounding from temporary operations. Roughly log_2(n)
    # operations are performed.
    prec2 = prec + int(4*math.log(n, 2) + 4)
    man, exp, bc = normalize(s[0], s[1], prec2, ROUND_FLOOR)
    pm, pe, pbc = fone
    while n:
        if n & 1:
            pm, pe, pbc = normalize(pm*man, pe+exp, prec2, ROUND_FLOOR)
            n -= 1
        man, exp, bc = normalize(man*man, exp+exp, prec2, ROUND_FLOOR)
        n = n // 2
    return normalize(pm, pe, prec, rounding)


"""
Square roots are most efficiently computed with Newton's method.
Two functions are implemented: _sqrt_fixed and _sqrt_fixed2.

  _sqrt_fixed uses the iteration r_{n+1} = (r_n + y/r_n)/2,
  which is just Newton's method applied to the equation r**2 = y.

  _sqrt_fixed2 uses the iteration r_{n+1} = r_n*(3 - y*r_n**2)
  to calculate 1/sqrt(y), and then multiplies by y to obtain
  sqrt(y).

The first iteration is slightly faster at low precision levels, since
it essentially just requires one division at each step, compared to
the three multiplications in the second formula. However, the second
iteration is much better at extremely high precision levels. This is
due to the fact that Python uses the Karatsuba algorithm for integer
multiplication, which is asymptotically faster than its division
algorithm.

For optimal speed, we exploit the "self-correcting" nature of
Newton's method to perform subcomputations at as low a precision level
as possible. Starting from a 50-bit floating-point estimate, the
first step can be computed using 100-bit precision, the second
at 200-bit precision, and so on; full precision is only needed for
the final step.

Both functions use fixed-point arithmetic and assume that the input y
is a big integer, i.e. given the integer y and precision prec,
they return floor(sqrt(x) * 2**prec) where y = floor(x * 2**prec).

The functions currently assume that x ~= 1. (TODO: make the code
work for x of arbitrary magnitude.) The main fsqrt() function
fiddles with the exponent of the input to reduce it to unit
magnitude before passing it to _sqrt_fixed or _sqrt_fixed2.

"""

def _sqrt_fixed(y, prec):
    # get 50-bit initial guess from regular float math
    if prec < 200:
        r = int(y**0.5 * 2.0**(50-prec*0.5))
    else:
        r = int((y >> (prec-100))**0.5)
    prevp = 50
    for p in _quadratic_steps(50, prec+8):
        # Newton iteration: r_{n+1} = (r_{n} + y/r_{n})/2
        # print "sqrt", p
        r = _lshift(r, p-prevp-1) + (_rshift(y, prec-p-prevp+1)//r)
        prevp = p
    return r >> 8

def _sqrt_fixed2(y, prec):
    r = float_to_pyfloat(normalize(y, -prec, 64, ROUND_FLOOR)) ** -0.5
    r = int(r * 2**50)
    prevp = 50
    for p in _quadratic_steps(50, prec+8):
        # print "sqrt", p
        r2 = _rshift(r*r, 2*prevp - p)
        A = _lshift(r, p-prevp)
        T = _rshift(y, prec-p)
        S = (T*r2) >> p
        B = (3 << p) - S
        r = (A*B)>>(p+1)
        prevp = p
    r = (r * y) >> prec
    return r >> 8

def fsqrt(s, prec=STANDARD_PREC, rounding=ROUND_HALF_EVEN):
    """
    If x is a positive Float, sqrt(x) returns the square root of x as a
    Float, rounded to the current working precision.
    """
    man, exp, bc = s
    if not man: return fzero
    if (man, exp) == (1, 0): return fone

    prec2 = prec + 4

    # Convert to a fixed-point number with prec bits. Adjust
    # exponents to be even so that they can be divided in half
    if prec2 & 1:
        prec2 += 1
    if exp & 1:
        exp -= 1
        man <<= 1
    shift = bitcount(man) - prec2
    shift -= shift & 1
    man = _rshift(man, shift)

    if prec < 65000:
        man = _sqrt_fixed(man, prec2)
    else:
        man = _sqrt_fixed2(man, prec2)

    return normalize(man, (exp+shift-prec2)//2, prec, ROUND_HALF_EVEN)


#----------------------------------------------------------------------------#
#                                                                            #
#                         Mathematical constants                             #
#                                                                            #
#----------------------------------------------------------------------------#

# Evaluate a Machin-like formula, i.e., a rational combination of
# of acot(n) or acoth(n) for specific integer values of n
def _machin(coefs, prec, hyperbolic=False):
    def acot(x):
        # Series expansion for atan/acot, optimized for integer arguments
        s = w = (1<<prec)//x; x2 = x*x; n = 3
        while 1:
            w //= x2
            term = w // n
            if not term: break
            if hyperbolic or n & 2 == 0: s += term
            else: s -= term
            n += 2
        return s
    s = 0
    for a, b in coefs:
        s += a * acot(b)
    return s

"""
At low precision, pi can be calculated easily using Machin's formula
pi = 16*acot(5)-4*acot(239). For high precision, we use the Brent-Salamin
algorithm based on the arithmetic-geometric mean. See for example Wikipedia
(http://en.wikipedia.org/wiki/Brent-Salamin_algorithm) or "Pi and the AGM" by
Jonathan and Peter Borwein (Wiley, 1987). The algorithm (as stated in the
Wikipedia article) consists of setting

  a_0 = 1;  b_0 = 1/sqrt(2);  t_0 = 1/4;  p_0 = 1

and computing

  a_{n+1} = (a_n + b_n)/2
  b_{n+1} = sqrt(a_n * b_n)
  t_{n+1} = t_n - p_n*(a_n - a_{n+1})**2
  p_{n+1} = 2*p_n

for n = 0, 1, 2, 3, ..., after which the approximation is given by
pi ~= (a_n + b_n)**2 / (4*t_n). Each step roughly doubles the number of
correct digits.
"""

def _pi_agm(prec, verbose=False, verbose_base=10):
    prec += 50
    a = 1 << prec
    if verbose: print "  computing initial square root..."
    b = _sqrt_fixed2(a>>1, prec)
    t = a >> 2
    p = 1
    step = 1
    while 1:
        an = (a+b)>>1
        adiff = a - an
        if verbose:
            try:
                logdiff = math.log(adiff, verbose_base)
            except ValueError:
                logdiff = 0
            digits = int(prec/math.log(verbose_base,2) - logdiff)
            print "  iteration", step, ("(accuracy ~= %i base-%i digits)" % \
                (digits, verbose_base))
        if p > 16 and abs(adiff) < 1000:
            break
        prod = (a*b)>>prec
        b = _sqrt_fixed2(prod, prec)
        t = t - p*((adiff**2) >> prec)
        p = 2*p
        a = an
        step += 1
    if verbose: print "  final division"
    return ((((a+b)**2) >> 2) // t) >> 50

def fpi(prec=STANDARD_PREC, rounding=ROUND_HALF_EVEN):
    """Compute a floating-point approximation of pi"""
    if prec < 10000:
        pi_man = _machin([(16, 5), (-4, 239)], prec+10)
    else:
        pi_man = _pi_agm(prec+10)
    return normalize(pi_man, -prec-10, prec, rounding)

