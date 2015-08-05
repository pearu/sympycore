from sympycore.algebra import *

x = Symbol('x')

def test_linear():
    assert x + x == 2*x
    assert (2*x) / 2 == x
    assert (x/2)*2 == x
    assert 3*x + 4*x == 7*x
    assert 2*x/3 + x/3 == x
    assert I*x + 3*x == (3+I)*x

def test_powers():
    assert Number(3) ** Number(-2) == Number(1,9)
    assert Number(4) ** Number(1,2) == Number(2)
    assert str(Number(2) ** Number(1,2)) == '2**(1/2)'
    assert A('4/9') ** A('1/2') == A('2/3')
    assert A('4/7') ** A('1/2') == A('7**(-1/2)')*2
    assert A('7/4') ** A('1/2') == A('7**(1/2)')/2
