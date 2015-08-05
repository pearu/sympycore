
from sympycore import *

def xtest_sorting():
    s1 = Set(1,2)
    s2 = Set(3,4)
    l = [s2, s1]
    l.sort(cmp)
    assert l==[s1,s2]
