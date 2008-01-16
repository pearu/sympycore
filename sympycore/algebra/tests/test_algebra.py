from sympycore.algebra import *

x = Symbolic('x')

def test_linear():
    assert x + x == 2*x
    assert (2*x) / 2 == x
    #assert (x/2)*2 == x
