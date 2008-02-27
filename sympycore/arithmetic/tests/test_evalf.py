from sympycore.arithmetic.evalf import *
from sympycore.arithmetic.evalf import mpmath, compile_mpmath
from sympycore.calculus import Symbol, I, Number, exp, sin, cos, E, pi
import math
import cmath

def test_evalf():
    expr1 = Number(1)/3
    expr2 = sin(E)**2 + cos(E)**2 - 1
    expr3 = exp(I) - cos(1) - I*sin(1)
    assert abs(evalf(pi, 15) - math.pi) < 1e-14
    assert abs(evalf(expr1, 30) - expr1) < 1e-29
    assert abs(evalf(expr2, 30)) < 1e-29
    assert abs(evalf(expr2, 100)) < 1e-99
    assert abs(evalf(expr2, 300)) < 1e-99
    assert abs(evalf(expr3, 20)) < 1e-19

def test_compiled():
    x = Symbol('x')
    y = Symbol('y')
    f1 = compile_mpmath([], exp(2))
    f2 = compile_mpmath('x', exp(x))
    f3 = compile_mpmath(['x', 'y'], cos(x)+sin(y)*I)
    mpmath.mpf.dps = 15
    assert abs(f1() - math.exp(2)) < 1e-14
    assert abs(f2(2) - math.exp(2)) < 1e-14
    assert abs(f3(3,4) - (cmath.cos(3)+cmath.sin(4)*1j)) < 1e-14
