RATIONAL = 'Q'
SYMBOLIC = 'S'
TERMS = '+'
FACTORS = '*'

def make_int(n):
    return (RATIONAL, n, 1)

def make_rational(p, q):
    x, y = p, q
    while y:
        x, y = y, x % y
    if x != 1:
        p //= x
        q //= x
    return (RATIONAL, p, q)

zero = make_int(0)
one = make_int(1)
two = make_int(2)
half = make_rational(1,2)

def make_symbol(name):
    return (SYMBOLIC, name)

def convert_terms(x):
    if x[0] is RATIONAL:
        return (TERMS, [(one, x[1:])])
    else:
        return (TERMS, [(x, (1, 1))])

def add_default(a, b):
    if a[0] is not TERMS: a = convert_terms(a)
    if b[0] is not TERMS: b = convert_terms(b)
    return add_terms_terms(a, b)

def add_terms_terms(a, b):
    c = dict(a[1])
    # Add dicts
    for e, (r, s) in b[1]:
        if e in c:
            p, q = c[e]
            c[e] = (p*s + q*r, q*s)
        else:
            c[e] = (r, s)
    # Normalize
    for e, (p, q) in c.items():
        if not p:
            del c[e]
            continue
        x, y = p, q
        while y:
            x, y = y, x % y
        if x != 1:
            c[e] = (p//x, q//x)
    if not c:
        return zero
    citems = c.items()
    if len(citems) == 1:
        w = citems[0]
        if w[1] == (1, 1):
            return w[0]
    return (TERMS, frozenset(c.items()))

def add_symbolic_symbolic(a, b):
    if a == b:
        return (TERMS, frozenset([(a, (2, 1))]))
    return (TERMS, frozenset([(a, (1, 1)), (b, (1, 1))]))

def add_rational_rational(a, b):
    _, p, q = a
    _, r, s = b
    return make_rational(p*s + q*r, q*s)

addition = {
    (TERMS, TERMS) : add_terms_terms,
    (SYMBOLIC, SYMBOLIC) : add_symbolic_symbolic,
    (RATIONAL, RATIONAL) : add_rational_rational
}


def mul_default(a, b):
    if a[0] is not FACTORS: a = (FACTORS, [(a, (1, 1))])
    if b[0] is not FACTORS: b = (FACTORS, [(b, (1, 1))])
    return mul_factors_factors(a, b)

def mul_factors_factors(a, b):
    c = dict(a[1])
    for e, (r, s) in b[1]:
        if e in c:
            p, q = c[e]
            c[e] = (p*s + q*r, q*s)
        else:
            c[e] = (r, s)
    for e, (p, q) in c.items():
        if not p:
            del c[e]
            continue
        x, y = p, q
        while y:
            x, y = y, x % y
        if x != 1:
            c[e] = (p//x, q//x)
    if not c:
        return one
    return (FACTORS, frozenset(c.items()))

def mul_rational_symbolic(a, b):
    if a == zero: return zero
    if a == one: return b
    return (TERMS, frozenset([(b, a[1:])]))

def mul_symbolic_rational(a, b):
    return mul_rational_symbolic(b, a)

def mul_rational_terms(a, b):
    if a == zero: return zero
    if a == one: return b
    p, q = a[1:]
    return (TERMS, frozenset([(e, (p*r, q*s)) for e, (r, s) in b[1]]))

def mul_terms_rational(a, b):
    return mul_rational_terms(b, a)

def mul_rational_rational(a, b):
    _, p, q = a
    _, r, s = b
    return make_rational(p*r, q*s)

multiplication = {
    (RATIONAL, SYMBOLIC) : mul_rational_symbolic,
    (SYMBOLIC, RATIONAL) : mul_symbolic_rational,
    (RATIONAL, TERMS)    : mul_rational_terms,
    (TERMS, RATIONAL)    : mul_terms_rational,
    (FACTORS, FACTORS)   : mul_factors_factors,
    (RATIONAL, RATIONAL) : mul_rational_rational
}

def show(x):
    h = x[0]
    if h is RATIONAL:
        return '%i/%i' % (x[1:])
    if h is SYMBOLIC:
        return x[1]
    if h is TERMS:
        return ' + '.join((("(%i/%i)" % b)+"*"+show(a)) for (a, b) in x[1])
    if h is FACTORS:
        return ' * '.join(("(%s)**(%i/%i)" % (show(a), b[0], b[1])) for (a, b) in x[1])
    return str(x)

class Expr:

    def __init__(self, value=None, _s=None):
        if _s:
            self._s = _s
        elif isinstance(value, (int, long)):
            self._s = make_int(value)
        elif isinstance(value, str):
            self._s = make_symbol(value)

    def __repr__(self):
        return show(self._s)

    def __add__(self, other):
        if not isinstance(other, Expr):
            other = Expr(other)
        s, t = self._s, other._s
        add = addition.get((s[0], t[0]), add_default)
        return Expr(_s=add(self._s, other._s))

    __radd__ = __add__

    def __mul__(self, other):
        if not isinstance(other, Expr):
            other = Expr(other)
        s, t = self._s, other._s
        mul = multiplication.get((s[0], t[0]), mul_default)
        return Expr(_s=mul(s, t))

    __rmul__ = __mul__

def Rational(p, q):
    return Expr(_s=make_rational(p, q))


#x = Expr('x')
#y = Expr('y')
#z = Expr('z')
#A = x*Rational(2,3) + y*Rational(2,3) + Rational(17,6)
#B = x*Rational(-1,2) + y*1 + z*Rational(3,2) + 1
#A + B

from time import clock
import psyco
import sympy

def time1():
    x = Expr('x')
    y = Expr('y')
    z = Expr('z')
    a = Rational(1,2)
    b = Rational(3,4)
    c = Rational(5,6)
    A = a*x + b*y + c*z
    B = b*x + c*y + a*z
    t1 = clock()
    n = 100
    while n:
        #3*(a*x+b*y+c*z)
        #A + B
        #x + y
        #a + b
        a * b
        n -= 1
    t2 = clock()
    return (t2-t1) / 100

def time2():
    x = sympy.Symbol('x')
    y = sympy.Symbol('y')
    z = sympy.Symbol('z')
    a = sympy.Rational(1,2)
    b = sympy.Rational(3,4)
    c = sympy.Rational(5,6)
    A = a*x + b*y + c*z
    B = b*x + c*y + a*z
    t1 = clock()
    n = 100
    while n:
        #3*(a*x+b*y+c*z)
        #A + B
        #x + y
        #a + b
        a * b
        n -= 1
    t2 = clock()
    return (t2-t1) / 100

def timing():
    t1 = time1()
    t2 = time2()
    return t1, t2, t2/t1

print timing()

"""
from directadd5 import *
"""