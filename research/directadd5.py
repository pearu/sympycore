import gmpy

NUMBER = 'N'
SYMBOLIC = 'S'
TERMS = '+'
FACTORS = '*'

class rational(tuple):

    def __new__(cls, p, q, tnew=tuple.__new__):
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
        return "%i/%i" % self

    __repr__ = __str__

    # not needed when __new__ normalizes to ints
    # __nonzero__
    # __eq__
    # __hash__

    def __add__(self, other):
        p, q = self
        if isinstance(other, int):
            r, s = other, 1
        else:
            r, s = other
        return rational(p*s + q*r, q*s)

    __radd__ = __add__

    def __mul__(self, other):
        p, q = self
        if isinstance(other, int):
            r, s = other, 1
        elif isinstance(other, rational):
            r, s = other
        else:
            return NotImplemented
        return rational(p*r, q*s)

    __rmul__ = __mul__



def make_int(n):
    return (NUMBER, n)

def make_rational(p, q):
    return (NUMBER, rational(p, q))

zero = make_int(0)
one = make_int(1)
two = make_int(2)
half = make_rational(1, 2)

def make_symbol(name):
    return (SYMBOLIC, name)

def convert_terms(x):
    if x[0] is NUMBER:
        return (TERMS, [(one, x[1])])
    else:
        return (TERMS, [(x, 1)])

def add_default(a, b):
    if a[0] is not TERMS: a = convert_terms(a)
    if b[0] is not TERMS: b = convert_terms(b)
    return add_terms_terms(a, b)

def add_terms_terms(a, b):
    c = dict(a[1])
    for e, x in b[1]:
        if e in c:
            c[e] += x
            if not c[e]:
                del c[e]
        else:
            c[e] = x
    if not c:
        return zero
    citems = c.items()
    if len(citems) == 1:
        w = citems[0]
        if w[1] == 1:
            return w[0]
    return (TERMS, frozenset(citems))

def add_symbolic_symbolic(a, b):
    if a == b:
        return (TERMS, frozenset([(a, 2)]))
    return (TERMS, frozenset([(a, 1), (b, 1)]))

def add_rational_rational(a, b):
    return (NUMBER, a[1]+b[1])

addition = {
    (TERMS, TERMS)       : add_terms_terms,
    (SYMBOLIC, SYMBOLIC) : add_symbolic_symbolic,
    (NUMBER, NUMBER) : add_rational_rational
}


def mul_default(a, b):
    if a[0] is not FACTORS: a = (FACTORS, [(a, 1)])
    if b[0] is not FACTORS: b = (FACTORS, [(b, 1)])
    return mul_factors_factors(a, b)

def mul_factors_factors(a, b):
    c = dict(a[1])
    for e, x in b[1]:
        if e in c:
            c[e] += x
            if not c[e]:
                del c[e]
        else:
            c[e] = x
    if not c:
        return one
    return (FACTORS, frozenset(c.items()))

def mul_rational_symbolic(a, b):
    if a == zero: return zero
    if a == one: return b
    return (TERMS, frozenset([(b, a[1])]))

def mul_symbolic_rational(a, b):
    return mul_rational_symbolic(b, a)

def mul_rational_terms(a, b):
    if a == zero: return zero
    if a == one: return b
    p = a[1]
    return (TERMS, frozenset([(e, p*x) for e, x in b[1]]))

def mul_terms_rational(a, b):
    return mul_rational_terms(b, a)

def mul_rational_rational(a, b):
    return (NUMBER, a[1]*b[1])

multiplication = {
    (NUMBER, SYMBOLIC) : mul_rational_symbolic,
    (SYMBOLIC, NUMBER) : mul_symbolic_rational,
    (NUMBER, TERMS)    : mul_rational_terms,
    (TERMS, NUMBER)    : mul_terms_rational,
    (FACTORS, FACTORS)   : mul_factors_factors,
    (NUMBER, NUMBER) : mul_rational_rational
}

def show(x):
    if isinstance(x, int):
        return str(x)
    h = x[0]
    if h is NUMBER:
        return str(x[1])
    if h is SYMBOLIC:
        return x[1]
    if h is TERMS:
        return ' + '.join((show(b)+"*"+show(a)) for (a, b) in x[1])
    if h is FACTORS:
        return ' * '.join(("(%s)**(%i/%i)" % (show(a), show(b))) for (a, b) in x[1])
    return str(x)

class Expr:

    def __init__(self, value=None, _s=None):
        if _s:
            self._s = _s
            return
        if isinstance(value, int):
            self._s = (NUMBER, value)
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


# use time() instead on unix
import sys
if sys.platform=='win32':
    from time import clock
else:
    from time import time as clock

import sympycore as sympy

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
    n = 1000
    while n:
        3*(a*x+b*y+c*z)
        #A + B
        #x + y
        #a + b
        #a * b
        n -= 1
    t2 = clock()
    return 100 / (t2-t1)

def time2(n=1000):
    Symbol = sympy.Symbol
    Number = sympy.Number
    x = Symbol('x')
    y = Symbol('y')
    z = Symbol('z')
    a = Number(1,2)
    b = Number(3,4)
    c = Number(4,5)
    A = a*x + b*y + c*z
    B = b*x + c*y + a*z
    t1 = clock()
    while n:
        3*(a*x+b*y+c*z)
        #A + B
        #x + y
        #a + b
        #a * b
        n -= 1
    t2 = clock()
    return 100 / (t2-t1)


def timing():
    t1 = time1()
    t2 = time2()
    return t1, t2, t1/t2

print "without psyco"
print timing()
print timing()
print timing()

from sympycore import profile_expr

profile_expr('time2(1000)')

try:
    import psyco
except ImportError:
    psyco = None
if psyco is not None:
    psyco.full()

    print "with psyco"
    print timing()
    print timing()
    print timing()
