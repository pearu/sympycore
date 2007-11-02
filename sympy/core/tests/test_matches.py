
from sympy import *

def test_basic():
    w = BasicWildSymbol()
    v = BasicWildSymbol()
    wf = BasicWildFunctionType()
    s = BasicSymbol('s')
    t = BasicSymbol('t')
    f = BasicFunctionType('f')
    
    assert w.match(v)==None
    assert s.match(w)=={w:s}
    assert s.match(wf)==None
    assert f.match(w)==None
    assert f.match(wf)=={wf:f}
    assert s.match(s)=={}
    assert s.match(f)==None
    assert f.match(s)==None
    assert f.match(f)=={}

    assert f(s).match(w)=={w:f(s)}
    assert f(s).match(wf)==None
    assert f(s).match(wf(w))=={w:s,wf:f}
    assert f(s).match(wf(t))==None
    assert f(s,t).match(wf(w))==None
    assert f(s,t).match(wf(w,w))==None
    assert f(s,s).match(wf(w,w))=={w:s,wf:f}
    assert f(s,t).match(wf(w,v))=={w:s,v:t,wf:f}
