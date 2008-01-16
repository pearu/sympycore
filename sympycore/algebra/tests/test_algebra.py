from sympycore.algebra import *

x = Symbol('x')

def test_linear():
    assert x + x == 2*x
    assert (2*x) / 2 == x
    assert (x/2)*2 == x
    assert 3*x + 4*x == 7*x
    assert 2*x/3 + x/3 == x
    assert I*x + 3*x == (3+I)*x

