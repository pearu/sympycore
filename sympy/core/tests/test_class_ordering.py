
from sympy import *

def test_basic():
    a = BasicSymbol('a')
    b = BasicFunction('a')
    l = [b,a]
    l.sort(Basic.compare)
    assert l==[a,b]

    
