from sympycore.calculus import Calculus as A
from sympycore.calculus.algebra import oo
from sympycore.calculus.functions.elementary import sin, cos, tan, cot, pi, E, exp, log

def test_exp_log():
    assert exp(1) == E
    assert exp(0) == 1
    assert log(0) == -oo
    assert log(1) == 0
    assert log(oo) == oo

def test_trig_values():
    sqrt2 = A('2**(1/2)')
    sqrt3 = A('3**(1/2)')
    assert sin(0) == 0
    assert sin(pi) == 0
    assert sin(4*pi) == 0
    assert sin(3*pi/2) == -1
    assert sin(5*pi/2) == 1
    assert sin(pi/3) == sqrt3/2
    assert sin(pi/2) == 1
    assert cos(0) == 1
    assert cos(pi) == -1
    assert cos(8*pi) == 1
    assert cos(-9*pi) == -1
    assert cos(pi/2) == 0
    assert cos(3*pi/2) == 0
    assert cos(11*pi/2) == 0
    assert cos(pi/12) == (1 + sqrt3) / (2 * sqrt2)
    assert tan(7*pi/12) == sin(7*pi/12)/cos(7*pi/12)

def test_trig_symmetry():
    x = A('x')
    assert sin(-x) == -sin(x)
    assert cos(-x) == cos(x)
    assert tan(-x) == -tan(x)
    assert cot(-x) == -cot(x)
    assert sin(x+pi) == -sin(x)
    assert sin(x+2*pi) == sin(x)
    assert sin(x+3*pi) == -sin(x)
    assert sin(x+4*pi) == sin(x)
    assert sin(x-5*pi) == -sin(x)
    assert cos(x+pi) == -cos(x)
    assert cos(x+2*pi) == cos(x)
    assert cos(x+3*pi) == -cos(x)
    assert cos(x+4*pi) == cos(x)
    assert cos(x-5*pi) == -cos(x)
    assert tan(x+pi) == tan(x)
    assert tan(x-3*pi) == tan(x)
    assert cot(x+pi) == cot(x)
    assert cot(x-3*pi) == cot(x)
    assert sin(pi/2-x) == cos(x)
    assert sin(3*pi/2-x) == -cos(x)
    assert sin(5*pi/2-x) == cos(x)
    assert cos(pi/2-x) == sin(x)
    assert cos(3*pi/2-x) == -sin(x)
    assert cos(5*pi/2-x) == sin(x)
    assert tan(pi/2-x) == cot(x)
    assert tan(3*pi/2-x) == cot(x)
    assert tan(5*pi/2-x) == cot(x)
    assert cot(pi/2-x) == tan(x)
    assert cot(3*pi/2-x) == tan(x)
    assert cot(5*pi/2-x) == tan(x)
    assert sin(pi/2+x) == cos(x)
    assert cos(pi/2+x) == -sin(x)
    assert tan(pi/2+x) == -cot(x)
    assert cot(pi/2+x) == -tan(x)

def test_trig_diff():
    x = A('x')
    assert sin(x).diff(x) == cos(x)
    assert cos(x).diff(x) == -sin(x)
    assert sin(2*x).diff(x) == 2*cos(2*x)

    assert tan(x).diff(x) == 1+tan(x)**2
    assert cot(x).diff(x) == -1-cot(x)**2

    assert log(x).diff(x) == 1/x
    assert exp(x).diff(x) == exp(x)


    assert (x*sin(x)).diff(x) == x*cos(x) + sin(x)
