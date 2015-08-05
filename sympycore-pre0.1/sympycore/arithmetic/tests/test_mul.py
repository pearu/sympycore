from sympycore import *

a = Symbol("a")
b = Symbol("b")
c = Symbol("c")


def test_operations():
    assert Mul() == 1
    assert Mul(3) == 3
    assert Mul(0, 2) == 0
    assert Mul(2, 3, a) == 6*a
    assert Div() == 1
    assert Div(3) == Rational(1,3)
    assert Div(2,a) == 2/a
    assert Div(2,a,b) == 2/(a*b)
    assert Pow(a,2) == a*a
    assert Sqrt(a) == a**Rational(1,2)
    assert Sqrt(0) == 0
    assert Sqrt(-1) == I
    assert Pow(I, -1) == -I

