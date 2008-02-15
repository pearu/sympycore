
from sympycore import *

A = Calculus
x,y,z = map(A.Symbol,'xyz')
f = A(1.2)

def test_ops():
    assert f+1==A(2.2)
    assert f+1.2==A(2.4)

    assert `f+x`=="Calculus('1.2 + x')"
    assert `1.2+x`=="Calculus('1.2 + x')"
    assert `f+pi`=="Calculus('4.34159265359')"
    assert `1.2+pi`=="Calculus('4.34159265359')"

