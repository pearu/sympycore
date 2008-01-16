
from sympycore.algebra import Symbol, Number

def test_number():
    s = Symbol('s')
    n = Number(2)
    assert n.matches(2)=={}
    assert n.matches(3)==None
