from sympycore.algebra.fractionlib import *

def test_mpq():
    assert mpq(1) == 1
    assert mpq(1,1) == 1
    assert mpq(1,2) != 1
    assert mpq(1,2) == mpq(2,4)
    assert mpq(1,2) + mpq(5,6) == mpq(4,3)
    assert 2*mpq(1,2) == 1
    assert mpq(1,2)*2 == 1
    assert mpq(1,3) + mpq(2,3) == 1
    assert float(mpq(1,4)) == 0.25
    assert mpq(1,2) == mpq(-1,-2)
    assert mpq(-1,2) == mpq(1,-2)
    assert -mpq(2,3) == mpq(-2,3)
    assert +mpq(2,3) == mpq(2,3)
    assert mpq(1,2) - 1 == mpq(-1,2)
    assert 1 - mpq(1,2) == mpq(1,2)
    assert mpq(2,3)**0 == 1
    assert mpq(2,3)**1 == mpq(2,3)
    assert mpq(2,3)**2 == mpq(4,9)
    assert div(1,2) == mpq(1,2)
    assert div(3,mpq(1,2)) == 6
    assert div(mpq(1,2),mpq(3,2)) == mpq(1,3)
