
from sympycore import *

def test_basic():
    a = BasicSymbol('a')
    b = BasicFunction('a')
    l = [b,a]
    l = sort_sequence(l)
    assert l==[a,b]

    
