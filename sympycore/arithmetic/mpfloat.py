from sympy import *
from mpmath.lib import *

# Implement significance arithmetic, using Python floats to represent
# the estimated accuracy. If x != 0 and p is the accuracy,
# the true value of x is estimated to be within
# [x*(1-2**-p), x*(1+2**-p)].

exact = 1e300
bitrate = 3.3219280948873626


def sigmul(s, t, sa, ta):
    """
    (1+a) * (1+b) = 1 + a + b + a*b
    So the retained accuracy is a little less than min(sa, sb)
    """
    accuracy = min(sa, ta)
    val = fmul(s, t, int(accuracy+1), ROUND_HALF_EVEN)
    return val, accuracy


def sigadd(s, t, sa, ta):
    sman, sexp, sbc = s
    tman, texp, tbc = t
    shigh = sexp + sbc
    thigh = texp + tbc
    ssign = sman < 0
    tsign = tman < 0
    if ssign ^ tsign and abs(shigh - thigh) < 3:
        # Detect catastrophic cancellation
        max_accuracy = min(sa, ta)
        r = fadd(s, t, max_accuracy, ROUND_HALF_EVEN)
        if r == fzero:
            accuracy = 0
        else:
            rman, rexp, rbc = r
            lost = max(shigh, thigh) - (rexp+rbc)
            accuracy = max_accuracy - lost
            r = fpos(r, int(accuracy+1), ROUND_HALF_EVEN)
        # print "lost in cancellation", max_accuracy - accuracy
        return r, accuracy
    if shigh >= thigh:
        accuracy = max(0, min(sa, shigh-thigh+ta))
    else:
        accuracy = max(0, min(ta, thigh-shigh+sa))
    return fadd(s, t, int(accuracy+1), ROUND_HALF_EVEN), accuracy


class Float(Number):

    def __new__(cls, v, accuracy=None):
        a = object.__new__(cls)
        if isinstance(v, float):
            a.val = float_from_pyfloat(v, 53, ROUND_FLOOR)
            a._acc = 52
        elif isinstance(v, int):
            a.val = float_from_int(v, bitcount(v), ROUND_FLOOR)
            a._acc = exact
        if accuracy is not None:
            a.val = fpos(a.val, int(accuracy*bitrate+1), ROUND_HALF_EVEN)
            a._acc = float(accuracy * bitrate)
        return a

    @property
    def accuracy(self):
        return self._acc / bitrate

    def __repr__(s):
        if s._acc == exact:
            dps = 100  # XXX
        else:
            dps = int(s._acc/bitrate+1)
        dps = max(1, dps)
        return binary_to_decimal(s.val, dps)

    def binaryop(s, t, f, symbolic):
        t = Basic.sympify(t)
        if isinstance(t, Float):
            r = object.__new__(Float)
            r.val, r._acc = f(s.val, t.val, s._acc, t._acc)
            return r
        return symbolic(self, other)

    def __neg__(s):
        r = object.__new__(Float)
        r.val = fneg_noround(s.val)
        r._acc = s._acc
        return r

    def __add__(s, t):
        return s.binaryop(t, sigadd, Add)

    __radd__ = __add__

    def __sub__(s, t):
        return s.binaryop(-t, sigadd, lambda x, y: Add(x, -y))

    def __mul__(s, t):
        return s.binaryop(t, sigmul, Mul)

    __rmul__ = __mul__

