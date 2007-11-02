
from sympy import *

def test_basic():
    w = Wild()
    v = Wild()
    wf = WildFunctionType()

    s = Symbol('s')
    t = Symbol('t')
    f = FunctionType('f')

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

def test_arith():
    w = Wild()
    v = Wild()
    s = Symbol('s')
    t = Symbol('t')
    n = Integer(7)
    #assert (4*t**2).match(w**2)=={w:2*t}
    assert s.match(n)==None
    assert n.match(w)=={w:n}
    assert n.match(n)=={}
    assert (s*t).match(w)=={w:s*t}
    assert (n*t).match(s*w)==None
    assert (s*t).match(s*w)=={w:t}
    assert (s*t).match(s*t*w)=={w:1}
    assert (s**2).match(w**2)=={w:s}
    assert (s**(2*t)).match(w**v)=={w:s,v:2*t}
    assert (s+1).match(w**v)=={w:s+1,v:1}
    assert (s**4).match(w**(4*v))=={w:s,v:1}
    assert (s**8).match(w**(4*v))=={w:s,v:2}
    assert (2*t).match(v*t)=={v:2}
    assert (8*t).match(4*v*t)=={v:2}
    assert (s**(8*t)).match(w**(4*v*t))=={w:s,v:2}

