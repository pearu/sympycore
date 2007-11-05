from sympy import *

def test_Sin():
    x, y = Symbol('x'), Symbol('y')
    assert Sin(0) == 0
    assert Sin(1) == Sin(1)
    assert Sin(-1) == -Sin(1)
    assert Sin(x) == Sin(x)
    assert Sin(-x) == -Sin(x)
    assert Sin(pi) == 0
    assert Sin(-pi) == 0
    assert Sin(2*pi) == 0
    assert Sin(-2*pi) == 0
    assert Sin(-3*10**73*pi) == 0
    assert Sin(7*10**103*pi) == 0
    assert Sin(pi/2) == 1
    assert Sin(-pi/2) == -1
    assert Sin(5*pi/2) == 1
    assert Sin(7*pi/2) == -1
    assert Sin(pi/3) == Sqrt(3)/2
    assert Sin(-2*pi/3) == -Sqrt(3)/2
    assert Sin(pi/4) == Sqrt(2)/2
    assert Sin(-pi/4) == -Sqrt(2)/2
    assert Sin(17*pi/4) == Sqrt(2)/2
    assert Sin(-3*pi/4) == -Sqrt(2)/2
    half = Rational(1,2)
    assert Sin(pi/6) == half
    assert Sin(-pi/6) == -half
    assert Sin(7*pi/6) == -half
    assert Sin(-5*pi/6) == -half
    assert Sin(pi/105) == Sin(pi/105)
    assert Sin(-pi/105) == -Sin(pi/105)
    assert Sin(2 + 3*I) == Sin(2 + 3*I)
