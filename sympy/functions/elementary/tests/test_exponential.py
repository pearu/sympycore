from sympy import *
#from sympy.utilities.pytest import XFAIL

def test_Exp():

    x = Symbol('x')
    y = Symbol('y')

    assert Exp(nan) == nan

    assert Exp(oo) == oo
    assert Exp(-oo) == 0

    assert Exp(0) == 1
    assert Exp(1) == E

    return
    assert Exp(pi*I/2) == I
    assert Exp(pi*I) == -1
    assert Exp(3*pi*I/2) == -I
    assert Exp(2*pi*I) == 1

    assert Exp(Log(x)) == x
    assert Exp(2*Log(x)) == x**2
    assert Exp(pi*Log(x)) == x**pi

    assert Exp(17*Log(x) + E*Log(y)) == x**17 * y**E

    assert Exp(x*Log(x)) != x**x


def test_Log():

    assert Log(nan) == nan

    assert Log(oo) == oo
    assert Log(-oo) == oo + I*pi

    assert Log(0) == -oo

    assert Log(1) == 0
    assert Log(-1) == I*pi

    assert Log(E) == 1
    assert Log(-E).expand() == 1 + I*pi

    assert Log(pi) == Log(pi)
    assert Log(-pi).expand() == Log(pi) + I*pi

    assert Log(17) == Log(17)
    assert Log(-17) == Log(17) + I*pi

    return

    assert Log(I) == I*pi/2
    assert Log(-I) == -I*pi/2

    assert Log(17*I) == I*pi/2 + Log(17)
    assert Log(-17*I).expand() == -I*pi/2 + Log(17)

    assert Log(oo*I) == oo
    assert Log(-oo*I) == oo

    assert Exp(-Log(3))**(-1) == 3

    x, y = symbols('xy')

    assert Log(x) == Log(x)
    assert Log(x*y) != Log(x) + Log(y)

    #assert Log(x**2) != 2*Log(x)
    assert Log(x**2).expand() == 2*Log(x)
    assert Log(x**y) != y*Log(x)

    #I commented this test out, because it doesn't work well with caching and
    #thus completely breaks limits, that rely on Log(Exp(x)) -> x
    #simplification. --Ondrej
    #assert Log(Exp(x)) != x

    x, y = symbols('xy', real=True)

    assert Log(x) == Log(x)
    #assert Log(x*y) != Log(x) + Log(y)
    assert Log(x*y).expand() == Log(x) + Log(y)

    #assert Log(x**2) != 2*Log(x)
    assert Log(x**2).expand() == 2*Log(x)
    assert Log(x**y) != y*Log(x)

    assert Log(Exp(x)) == x
    #assert Log(-Exp(x)) != x + I*pi
    assert Log(-Exp(x)).expand() == x + I*pi

    k = Symbol('k', positive=True)

    assert Log(-x) == Log(-x)
    assert Log(-k) == Log(-k)

    assert Log(x, 2) == Log(x)/Log(2)
    assert Log(E, 2) == 1/Log(2)

def xtest_Log_apply_evalf():
    value = (Log(3)/Log(2)-1).evalf()

    assert value.epsilon_eq(Real("0.58496250072115618145373"))

#commenting this out, see the issue 252
#@XFAIL
def xtest_Log_simplify():
    x = Symbol("x")
    assert Log(x**2) == 2*Log(x)
    assert Log(x**(2+Log(2))) == (2+Log(2))*Log(x)
