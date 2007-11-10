
from sympy import *

def test_boolean():
    b = Boolean('b')
    assert b.tostr()=='b'
    assert b.torepr()=="Boolean('b')"
