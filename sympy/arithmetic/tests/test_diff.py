from sympy import Symbol, Rational, Cos, Sin, Exp, Log, Tan, Cot

def testdiff():
    a = Symbol("a")
    b = Symbol("b")
    c = Symbol("c")
    p = Rational(5)
    e = a*b + b**p
    assert e.diff(a) == b
    assert e.diff(b) == a + 5*b**4
    assert e.diff(b).diff(a) == Rational(1)
    e = a*(b + c)
    assert e.diff(a) == b + c
    assert e.diff(b) == a
    assert e.diff(b).diff(a) == Rational(1)
    e = c**p
    assert e.diff(c, 6) == Rational(0)
    assert e.diff(c, 5) == Rational(120)
    e = c**Rational(2)
    assert e.diff(c) == 2*c
    e = a*b*c
    assert e.diff(c) == a*b

def testdiff2():
    n3 = Rational(3)
    n2 = Rational(2)
    n6 = Rational(6)
    x,c = map(Symbol, 'xc')

    e = n3*(-n2 + x**n2)*Cos(x) + x*(-n6 + x**n2)*Sin(x)
    assert e == 3*(-2 + x**2)*Cos(x) + x*(-6 + x**2)*Sin(x)
    assert e.diff(x).expand() == x**3*Cos(x)
    e = (x + 1)**3
    assert e.diff(x) == 3*(x + 1)**2
    e = x*(x + 1)**3
    assert e.diff(x) == (x + 1)**3 + 3*x*(x + 1)**2
    e = 2*Exp(x*x)*x
    assert e.diff(x) == 2*Exp(x**2) + 4*x**2*Exp(x**2)

def test_diff3():
    a,b,c = map(Symbol, 'abc')
    p = Rational(5)
    e = a*b + Sin(b**p)
    assert e == a*b + Sin(b**5)
    assert e.diff(a) == b
    assert e.diff(b) == a+5*b**4*Cos(b**5)
    e = Tan(c)
    assert e == Tan(c)
    assert e.diff(c) in [Cos(c)**(-2), 1 + Sin(c)**2/Cos(c)**2, 1 + Tan(c)**2]
    e = c*Log(c)-c
    assert e == -c+c*Log(c)
    assert e.diff(c) == Log(c)
    e = Log(Sin(c))
    assert e == Log(Sin(c))
    assert e.diff(c) in [Sin(c)**(-1)*Cos(c), Cot(c)]
    e = (Rational(2)**a/Log(Rational(2)))
    assert e == 2**a*Log(Rational(2))**(-1)
    assert e.diff(a) == 2**a
