from sympycore.calculus import *
from sympycore.calculus.differentiation import *

x = Symbol('x')
M = 10**6

def test_diff_poly():
    assert diff(3**(pi+5), x) == 0
    assert diff(x, x) == 1
    assert diff(x, x, 2) == 0
    assert diff(3*x**2 + 5*x, x) == 6*x + 5
    assert diff(3*x**2 + 5*x, x, 2) == 6
    assert diff(x**M + 2*x + 3, x, M+1) == 0

def test_diff_powers():
    assert diff(exp(x), x) == exp(x)
    assert diff(exp(x+1), x) == exp(x+1)
    assert diff(exp(x), x, M) == exp(x)
    assert diff(exp(x+1), x, M) == exp(x+1)
    assert diff(exp(3*x+1), x) == 3*exp(3*x+1)
    assert diff(2**(3*x+1), x) == 3*2**(3*x+1)*log(2)
    assert diff(2**(3*x+1), x, 1000) == 3**1000 * 2**(3*x+1) * log(2)**1000
    assert diff((2*x+1)**(3*x), x) == (2*x+1)**(3*x) * (6*x/(2*x+1)+3*log(2*x+1))

def test_diff_products():
    assert diff((1+x)*(2+x), x) == 3+2*x
    assert diff((1+x)**3*(2+x)**2, x) == 2*(1+x)**3*(2+x) + 3*(1+x)**2 * (2+x)**2
    assert diff(pi**2 * 2**Number(1,2) * x, x) == pi**2 * 2**Number(1,2)

def test_diff_log():
    assert diff(log(x), x) == 1/x
    assert diff(log(3*x), x) == 1/x
    assert diff(log(3*x+1), x) == 3/(3*x+1)
    assert diff(log(3*x+1), x, 5) == 24 * 3**5 / (3*x+1)**5

def test_diff_trig():
    assert diff(sin(x), x) == cos(x)
    assert diff(cos(x), x) == -sin(x)
    assert diff(sin(2*x), x) == 2*cos(2*x)
    assert diff(tan(x), x) == 1 + tan(x)**2
    assert diff(cot(x), x) == -1-cot(x)**2
    assert diff(sin(x), x, M) == sin(x)
    assert diff(sin(x), x, M+1) == cos(x)
    assert diff(cos(x), x, M) == cos(x)
    assert diff(cos(x), x, M+1) == -sin(x)
    assert diff(sin(3*x+1), x, 5) == 3**5 * cos(3*x+1)
    assert diff(cos(3*x+1), x, 5) == -3**5 * sin(3*x+1)
    assert diff(x*sin(x), x) == x*cos(x) + sin(x)
    assert diff(x*sin(x)*cos(x), x) == x*cos(x)**2 + cos(x)*sin(x) - x*sin(x)**2
