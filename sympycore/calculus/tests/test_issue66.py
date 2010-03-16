
from sympycore import *
def test_reproduce_issue():
    e = Calculus('a*b')
    assert e.subs(dict (a=2,b=2))==4

