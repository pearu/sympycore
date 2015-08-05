"""
('+', frozenset) -- term:coef<Q> dict
('*', frozenset) -- base:exp<Q> dict
('S', 'x') -- symbol
('Q', 1, 2) -- rational number
('A', ...) -- atom wrapper
"""

def make_rational(p, q):
    return ('Q', p, q)

one = make_rational(1, 1)

def make_symbol(name):
    return ('S', name)

def add(a, b):
    if a[0] == '+':
        c = dict(a[1])
    else:
        if a[0] == 'Q': c = {one : a[1:]}
        else: c = {a : (1, 1)}
    if b[0] == '+':
        b = b[1]
    else:
        if b[0] == 'Q': b = [(one, b[1:])]
        else: b = [(b, (1, 1))]
    for e, (r, s) in b:
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
    return ('+', frozenset(c.items()))

def mul(a, b):
    if (a[0], b[0]) == ('S', 'Q'):
        return ('+', frozenset([(a, b[1:])]))
    raise NotImplementedError

def show(x):
    h = x[0]
    if h == 'Q':
        return '%i/%i' % (x[1:])
    if h == 'S':
        return x[1]
    if h == '+':
        return ' + '.join((("(%i/%i)" % b)+"*"+show(a)) for (a, b) in x[1])
    return str(x)

class Expr:
    def __init__(self, value=None, _s=None):
        if _s:
            self._s = _s
        elif isinstance(value, int):
            self._s = make_rational(value, 1)
        elif isinstance(value, str):
            self._s = make_symbol(value)
    def __repr__(self):
        return show(self._s)
    def __add__(self, other):
        if not isinstance(other, Expr):
            other = Expr(other)
        return Expr(_s=add(self._s, other._s))
    def __mul__(self, other):
        if not isinstance(other, Expr):
            other = Expr(other)
        return Expr(_s=mul(self._s, other._s))

def Rational(p, q):
    return Expr(_s=make_rational(p, q))

x = Expr('x')
y = Expr('y')
z = Expr('z')
A = x*Rational(2,3) + y*Rational(2,3) + Rational(17,6)
B = x*Rational(-1,2) + y*1 + z*Rational(3,2) + 1
A + B
