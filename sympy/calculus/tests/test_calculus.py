from sympy import *

def test_operators():
    x = Symbol('x')
    y = Symbol('y')
    assert Integral(x, x) == x**2 / 2
    assert Integral(x, (x, 2, 3)) == Rational(5,2)
    assert Integral(x*y, x, y) == x**2 * y**2 / 4
    a = Integral(x**x, x)
    assert isinstance(a, Integral)
    #assert str(a) == "Integral(x**x, x)"
    b = Integral(x**x, (x, 1, 4))
    assert isinstance(b, Integral)
    #assert str(b) == "Integral(x**x, (x, 1, 4))"
    assert Derivative(x**2 + x, x) == 2*x + 1
    assert Derivative(x**3, (x, 2)) == 6*x
