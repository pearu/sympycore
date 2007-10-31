
from sympy import *

def test_sorting():
    s1 = Set(1,2)
    s2 = Set(3,4)
    l = [s2, s1]
    l.sort(Basic.static_compare)
    assert l==[s1,s2]
