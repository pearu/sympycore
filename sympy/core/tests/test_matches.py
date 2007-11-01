
from sympy import *

def test_basic():
    w = BasicWildSymbol()
    wf = BasicWildFunctionType()
    s = BasicSymbol('s')
    f = BasicFunctionType('f')
    assert s.match(w)=={w:s}
    assert s.match(wf)==None
    assert f.match(w)==None
    assert f.match(wf)=={wf:f}
