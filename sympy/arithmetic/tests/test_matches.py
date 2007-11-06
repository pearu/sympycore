
from sympy import *

def test_basic():
    w = Wild()
    v = Wild()
    wf = WildFunctionType()

    s = Symbol('s')
    t = Symbol('t')
    f = FunctionType('f')

    assert w.match(v)==None
    assert s.match(w)=={w:s}
    assert s.match(wf)==None
    assert f.match(w)==None
    assert f.match(wf)=={wf:f}
    assert s.match(s)=={}
    assert s.match(f)==None
    assert f.match(s)==None
    assert f.match(f)=={}

    assert f(s).match(w)=={w:f(s)}
    assert f(s).match(wf)==None
    assert f(s).match(wf(w))=={w:s,wf:f}
    assert f(s).match(wf(t))==None
    assert f(s,t).match(wf(w))==None
    assert f(s,t).match(wf(w,w))==None
    assert f(s,s).match(wf(w,w))=={w:s,wf:f}
    assert f(s,t).match(wf(w,v))=={w:s,v:t,wf:f}

def test_number():
    s = Symbol('s')
    assert Number(2).matches(2)=={}
    assert Number(2).matches(3)==None
    assert Number(2).matches(s)==None
    assert Number(2).matches(s+2)==None

def test_wild():
    w = Wild()
    s = Symbol('s')
    assert w.matches(Number(2))=={w:2}
    assert w.matches(s)=={w:s}
    assert w.matches(w)==None
    assert w.matches(s+2)=={w:s+2}
    assert w.matches(2*s)=={w:2*s}
    assert w.matches(s**2)=={w:s**2}

def test_symbol():
    s = Symbol('s')
    assert s.matches(s)=={}
    assert s.matches(2)==None
    assert s.matches(2+s)==None
    assert s.matches(2*s)==None
    assert s.matches(s**2)==None

def test_term():
    s = Symbol('s')
    p = 2*s
    assert p.matches(2*s)=={}
    assert p.matches(3*s)==None
    assert p.matches(s)==None
    assert p.matches(Number(2))==None
    assert p.matches(s**2)==None

def test_wild_term():
    w = Wild()
    p = 2*w
    s = Symbol('s')
    t = Symbol('t')
    assert p.matches(Integer(1))=={w:Fraction(1,2)}
    assert p.matches(Integer(2))=={w:1}
    assert p.matches(2*s)=={w:s}
    assert p.matches(3*s)=={w:s*3/2}
    assert p.matches(t*s)=={w:t*s/2}
    assert p.matches(s**2)=={w:s**2/2}
    assert p.matches(2*s+2)=={w:s+1}
    assert p.matches(2*s+4)=={w:s+2}
    assert p.matches(2*s+5)=={w:s+Fraction(5,2)}
    assert p.matches(2*s+t)=={w:s+t/2}
    assert p.matches(2*s-2*t)=={w:s-t}

def test_wild_symbol_term():
    w = Wild()
    s = Symbol('s')
    t = Symbol('t')
    p = s+w
    assert p.matches(s+2)=={w:2}
    assert p.matches(t+2)=={w:t+2-s}

def test_wild_wild_term():
    w2 = Wild()
    w1 = Wild()

    p = w1 + 2*w2
    s = Symbol('s')
    t = Symbol('t')
    assert p.matches(Integer(2)) in [{w2:0,w1:2},{w2:1,w1:0}]
    assert p.matches(2*s+t+2) in [{w2:1+s,w1:t},{w1:2*s+t,w2:1}]
    

def test_wild_factor():
    w = Wild()
    p = w**2
    s = Symbol('s')
    t = Symbol('t')
    assert p.matches(Integer(2))=={w:Integer(2)**Fraction(1,2)}
    assert p.matches(Integer(4))=={w:2}
    assert p.matches(Integer(16))=={w:4}
    assert p.matches(Integer(9))=={w:3}
    assert p.matches(Integer(8))=={w:Integer(2)**Fraction(3,2)}
    assert p.matches(s)==None
    assert p.matches(s**2)=={w:s}
    assert p.matches(s**3)==None
    assert p.matches(s**4)=={w:s**2}
    assert p.matches(s+2)==None
    assert p.matches(s*2)==None
    assert p.matches(s**2*2)==None
    assert p.matches(s**2*4)=={w:2*s}
    assert p.matches(s**2*t**2)=={w:s*t}
    assert p.matches(4*s**2*t**2)=={w:2*s*t}
    assert p.matches(s**4*t**4)=={w:s**2*t**2}
    assert p.matches(s**2*t**4)=={w:s*t**2}
    assert p.matches(s**2*t**3)==None
    assert p.matches(s**2*t**-4)=={w:s*t**-2}

def test_wild_symbol_factor():
    w = Wild()
    s = Symbol('s')
    t = Symbol('t')
    p = s*w
    assert p.matches(Integer(1))=={w:1/s}
    assert p.matches(s)=={w:1}
    assert p.matches(2+t)=={w:(2+t)/s}

def test_arith():
    v = Wild()
    w = Wild()

    s = Symbol('s')
    t = Symbol('t')
    n = Integer(7)
    assert (2*t).match(v*t)=={v:2}
    assert s.match(n)==None
    assert n.match(w)=={w:n}
    assert n.match(n)=={}
    assert (s*t).match(w)=={w:s*t}
    assert (n*t).match(s*w)=={w:n*t/s}
    assert (s*t).match(s*w)=={w:t}
    assert (s*t).match(s*t*w)=={w:1}
    assert (s**2).match(w**2)=={w:s}
    assert (s**(2*t)).match(w**v)=={w:s,v:2*t}
    assert (s+1).match(w**v)=={w:s+1,v:1}
    assert (s**4).match(w**(4*v))=={w:s,v:1}
    assert (s**8).match(w**(4*v))=={w:s,v:2}
    assert (2*t).match(v*t)=={v:2}
    assert (8*t).match(4*v*t)=={v:2}
    assert (s**(8*t)).match(w**(4*v*t))=={w:s,v:2}
    assert (4*t**2).match(w**2)=={w:2*t}
    assert (6*t**2).match(w**2)==None
    assert (8*t**3).match(w**3)=={w:2*t}
    assert (8*t**3).match(w**v)=={w:2*t,v:3}
    assert (9*t**3).match(w**v)=={w:9*t**3,v:1}
    assert Integer(9).match(w**v) in [{w:3,v:2},{w:Exp(2),v:Log(3)}]
    p = w**v
    d = Fraction(8,27).match(p)
    assert p.replace_dict(Fraction(8,27).match(p))==Fraction(8,27)
    assert (s**2*t**3).match(w**3*v**2)=={w:t,v:s}
    assert (s**3*t**2).match(w**3*v**2)=={w:s,v:t}

    v = Wild('v',predicate=lambda expr: expr.is_Atom)
    w = Wild('v',predicate=lambda expr: expr.is_Atom)

    assert (4*s).match(w*s)=={w:4}
    assert (4*s+t).match(w*s+v)=={w:4,v:t}
    assert (4*s+5).match(w*s+v)=={w:4,v:5}


def test_symbol2():
    x = Symbol('x')
    a,b,c,p,q = map(Wild, 'abcpq')

    e = x
    assert e.match(x) == {}
    assert e.match(a) == {a: x}

    e = Rational(5)
    assert e.match(c) == {c: 5}
    assert e.match(e) == {}
    assert e.match(e+1) == None

def test_add():
    x,y,a,b,c = map(Symbol, 'xyabc')
    p,q,r = map(Wild, 'pqr')

    e = a+b
    assert e.match(p+b) == {p: a}
    assert e.match(p+a) == {p: b}

    e = 1+b
    assert e.match(p+b) == {p: 1}

    e = a+b+c
    assert e.match(a+p+c) == {p: b}
    assert e.match(b+p+c) == {p: a}

    e = a+b+c+x
    assert e.match(a+p+x+c) == {p: b}
    assert e.match(b+p+c+x) == {p: a}
    assert e.match(b) == None
    assert e.match(b+p) == {p: a+c+x}
    assert e.match(a+p+c) == {p: b+x}
    assert e.match(b+p+c) == {p: a+x}

    e = 4*x+5
    assert e.match(3*x+p) == {p: x+5}
    p = Wild('p',predicate = lambda expr: expr.is_Atom)
    q = Wild('q',predicate = lambda expr: expr.is_Atom)
    assert e.match(4*x+p) == {p: 5}
    assert e.match(p*x+5) == {p: 4}
    assert e.match(p*x+q) == {p: 4, q: 5}

    e = 4*x+5*y+6
    assert e.match(p*x+q*y+r) == {p: 4, q: 5, r: 6}

def test_power():
    x,y,a,b,c = map(Symbol, 'xyabc')
    p,q,r = map(Wild, 'pqr')

    e = (x+y)**a
    assert e.match(p**q) == {p: x+y, q: a}
    assert e.match(p**p) == None

    e = (x+y)**(x+y)
    assert e.match(p**p) == {p: x+y}
    assert e.match(p**q) == {p: x+y, q: x+y}

    p = Wild('p',predicate = lambda expr: expr.is_Atom)
    p1 = Wild('p1',predicate = lambda expr: expr.is_Atom and not expr.is_one)
    q = Wild('q',predicate = lambda expr: expr.is_Atom)

    e = 3/(4*x+5)
    assert e.match(3/(p*x+q)) == {p: 4, q: 5}

    e = 3/(4*x+5)
    assert e.match(p1/(q*x+r)) == {p1: 3, q: 4, r: 5}

    e = 2/(x+1)
    assert e.match(p1/(q*x+r)) == {p1: 2, q: 1, r: 1}

    e = 1/(x+1)
    assert e.match(p/(q*x+r)) == {p: 1, q: 1, r: 1}

    r = Wild('r',predicate = lambda expr: expr.is_Atom)
    e = (2*x)**2
    assert e.match(p*q**r) == {p: 4, q: x, r: 2}

    e = Integer(1)
    assert e.match(x**p) == {p: 0}

def test_mul():
    x,y,a,b,c = map(Symbol, 'xyabc')
    p,q = map(Wild, 'pq')

    e = 4*x
    assert e.match(p*x) == {p: 4}
    assert e.match(p*y) == {p: 4*x/y}

    e = a*x*b*c
    assert e.match(p*x) == {p: a*b*c}
    assert e.match(c*p*x) == {p: a*b}

    e = (a+b)*(a+c)
    assert e.match((p+b)*(p+c)) == {p: a}

    e = x
    assert e.match(p*x) == {p: 1}

    e = Exp(x)
    assert e.match(x**p*Exp(x*q)) == {p: 0, q: 1}
    assert (x*e).match(x**p*Exp(x*q)) == {p: 1, q: 1}
    assert (x**3*e).match(x**p*Exp(x*q)) == {p: 3, q: 1}
    assert (e/x).match(x**p*Exp(x*q)) == {p: -1, q: 1}
    
def test_complex():
    a,b,c = map(Symbol, 'abc')
    x,y = map(Wild, 'xy')

    (1+I).match(x+I) == {x : 1}
    (a+I).match(x+I) == {x : a}
    (a+b*I).match(x+y*I) == {x : a, y : b}
    (2*I).match(x*I) == {x : 2}
    (a*I).match(x*I) == {x : a}
    (a*I).match(x*y) == {x : a, y : I}
    (2*I).match(x*y) == {x : 2, y : I}

def test_functions():
    x = Symbol('x')
    g = WildFunctionType('g')
    p = Wild('p')
    q = Wild('q')

    f = Cos(5*x)
    assert f.match(p*Cos(q*x)) == {p: 1, q: 5}
    assert f.match(p*g(5*x)) == {p: 1, g: Cos}
    assert f.match(p*g(q)) == {p: 1, g: Cos, q:5*x}
    assert f.match(p*q) in [{p: 1, q:Cos(5*x)},{q: 1, p:Cos(5*x)}]

    assert f.match(p*g(q*x)) == {p: 1, g: Cos, q: 5}

def test_interface():
    x,y = map(Symbol, 'xy')
    p,q = map(Wild, 'pq')

    assert (x+1).match(p+1) == {p: x}
    assert (x*3).match(p*3) == {p: x}
    assert (x**3).match(p**3) == {p: x}
    assert (x*Cos(y)).match(p*Cos(q)) == {p: x, q: y}

    assert (x*y).match(p*q) in [{p:x, q:y}, {p:y, q:x}]
    assert (x+y).match(p+q) in [{p:x, q:y}, {p:y, q:x}]
    assert (x*y+1).match(p*q) in [{p:1, q:1+x*y}, {p:1+x*y, q:1}]

# derivative tests are disabled because Derivative is not impl yet
def xtest_derivative1():
    x,y = map(Symbol, 'xy')
    p,q = map(Wild, 'pq')

    f = Function('f',nofargs=1)
    fd = Derivative(f(x), x)

    assert fd.match(p) == {p: fd}
    assert (fd+1).match(p+1) == {p: fd}
    assert (fd).match(fd) == {}
    assert (3*fd).match(p*fd) != None
    assert (3*fd-1).match(p*fd + q) == {p: 3, q: -1}

def xtest_derivative_bug1():
    f = Function("f")
    x = Symbol("x")
    a = Wild("a", exclude=[f])
    b = Wild("b", exclude=[f])
    pattern = a * Derivative(f(x), x, x) + b
    expr = Derivative(f(x), x)+x**2
    d1 = {b: x**2}
    d2 = pattern.matches(expr, d1, evaluate=True)
    assert d2 == None

def xtest_derivative2():
    f = Function("f")
    x = Symbol("x")
    a = Wild("a", exclude=[f])
    b = Wild("b", exclude=[f])
    e = Derivative(f(x), x)
    assert e.match(Derivative(f(x), x)) == {}
    assert e.match(Derivative(f(x), x, x)) == None
    e = Derivative(f(x), x, x)
    assert e.match(Derivative(f(x), x)) == None
    assert e.match(Derivative(f(x), x, x)) == {}
    e = Derivative(f(x), x)+x**2
    assert e.match(a*Derivative(f(x), x) + b) == {a: 1, b: x**2}
    assert e.match(a*Derivative(f(x), x, x) + b) == None
    e = Derivative(f(x), x, x)+x**2
    assert e.match(a*Derivative(f(x), x) + b) == None
    assert e.match(a*Derivative(f(x), x, x) + b) == {a: 1, b: x**2}

def xtest_match_deriv_bug1():
    n = Function('n')
    l = Function('l')

    x = Symbol('x')
    p = Wild('p')

    e = Derivative(l(x), x)/x - Derivative(Derivative(n(x), x), x)/2 - \
        Derivative(n(x), x)**2/4 + Derivative(n(x), x)*Derivative(l(x), x)/4
    e = e.subs(n(x), -l(x))
    t = x*exp(-l(x))
    t2 = Derivative(t, x, x)/t
    assert e.match( (p*t2).expand() ) == {p: -Rational(1)/2}

def test_match_bug2():
    x,y = map(Symbol, 'xy')
    p,q,r = map(Wild, 'pqr')
    res = (x+y).match(p+q+r)
    assert (p+q+r).replace_dict(res) == x+y

def test_match_bug3():
     x,a,b = map(Symbol, 'xab')
     p = Wild('p')
     assert (b*x*Exp(a*x)).match(x*Exp(p*x)) == None

def test_match_bug4():
    x = Symbol('x')
    p = Wild('p')
    e = x
    assert e.match(-p*x) == {p: -1}

def test_match_bug5():
    x = Symbol('x')
    p = Wild('p')
    e = -x
    assert e.match(-p*x) == {p: 1}

def test_match_bug6():
    x = Symbol('x')
    p = Wild('p')
    e = x
    assert e.match(3*p*x) == {p: Rational(1)/3}

def test_behavior1():
    x = Symbol('x')
    p = Wild('p')
    e = 3*x**2
    a = Wild('a', exclude = [x])
    assert e.match(a*x) == None
    assert e.match(p*x) == {p: 3*x}

def test_behavior2():
    x = Symbol('x')
    p = Wild('p')

    e = Rational(6)
    assert e.match(2*p) == {p: 3}

    e = 3*x + 3 + 6/x
    a = Wild('a', exclude = [x],
             predicate = lambda expr: expr!=x)
    assert e.expand().match(a*x**2 + a*x + 2*a) == None
    expr = e.expand()
    pat = p*x**2 + p*x + 2*p
    #print 'pat=',pat
    #print 'expr=',expr
    assert expr.match(pat) == {p: 3/x}

def test_match_polynomial():
    x = Symbol('x')
    a = Wild('a', exclude=[x])
    b = Wild('b', exclude=[x])
    c = Wild('c', exclude=[x])
    d = Wild('d', exclude=[x])

    eq = 4*x**3 + 3*x**2 + 2*x + 1
    pattern = a*x**3 + b*x**2 + c*x + d
    assert eq.match(pattern) == {a: 4, b: 3, c: 2, d: 1}
    assert (eq-3*x**2).match(pattern) == {a: 4, b: 0, c: 2, d: 1}

def test_exclude():
    x,y,a = map(Symbol, 'xya')
    p = Wild('p', exclude=[1,x])
    q = Wild('q', exclude=[x])
    r = Wild('r', exclude=[y])

    e = 3*x**2 + y*x + a
    assert e.match(p*x**2 + q*x + r) == {p: 3, q: y, r: a}

    e = x+1
    assert e.match(x+p) == None
    assert e.match(p+1) == None
    assert e.match(x+1+p) == {p: 0}

    e = Cos(x) + 5*Sin(y)
    assert e.match(r) == None
    assert e.match(Cos(y) + r) == None
    assert e.match(r + p*Sin(q)) == {r: Cos(x), p: 5, q: y}

def test_floats():
    a,b = map(Wild, 'ab')

    e = Cos(0.12345)**2
    r = e.match(a*Cos(b)**2)
    assert r == {a: 1, b: Real(0.12345)}
