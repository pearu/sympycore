
from sympycore.algebra import Symbol, Number

def test_symbol():
    p = Symbol('p')
    s = Symbol('s')
    t = Symbol('t')
    assert s.matches(s)=={}
    assert s.matches(t)==None
    assert s.matches(t,{},[s,],[True,])=={s:t}
    assert s.matches(t,{},[s,t],[True,True])==None

def test_number():
    s = Symbol('s')
    n = Number(2)
    assert n.matches(2)=={}
    assert n.matches(3)==None
    assert n.matches(s)==None
    assert n.matches(s+2)==None

