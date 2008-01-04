from sympycore import *

def test_arithmetic():
    a = Symbol('a')
    b = Function('b')
    c = E
    d = Integer(3)
    l = [b,c,a,d]
    l = sort_sequence(l)
    assert l==[d,c,a,b]
