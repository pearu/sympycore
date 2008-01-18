from sympycore.algebra.numberlib import *

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
    assert mpq(1234,15) < 83
    assert mpq(1234,15) > 82
    assert mpq(2,3) < mpq(3, 4)

def test_mpf():
    assert mpf(2) != 3
    assert mpf(2) == 2
    assert mpf(1.1) == mpf('1.1')
    assert mpf(3) * mpf(4) == 12
    assert mpf(3) + mpf(4) == mpf(7)
    assert mpf(3) - mpf(4) == -1
    assert 4*mpf(3) == 12
    assert mpf(3)*4 == 12
    assert 2+mpf(5) == 7
    assert 0.5 + mpf(1) == 1.5
    assert mpf(1) + 0.5 == 1.5
    assert hash(mpf(3)) == hash(3)
    assert hash(mpf(1.5)) == hash(1.5)
    assert mpf(3) < mpf(4)
    assert mpf(3) > mpf(2)
    assert mpf(3) < 4

def test_mpc():
    assert mpc(2,3) == mpc(2,3)
    assert mpc(2,3) != mpc(2,4)
    assert mpc(3,0) == 3
    assert mpc(3,1) != 3
    assert mpc(2,3)*2 == mpc(4,6)
    assert 2*mpc(2,3) == mpc(4,6)
    assert mpc(2,3)+2 == mpc(4,3)
    assert 2+mpc(2,3) == mpc(4,3)
    assert mpc(2,3)-2 == mpc(0,3)
    assert 2-mpc(2,3) == mpc(0,-3)
    assert mpc(mpq(2,3), 1) + mpc(mpq(1,3), 1) == mpc(1, 2)
    assert -mpc(2,3) == mpc(-2,-3)
    assert +mpc(2,3) == mpc(2,3)
    assert mpc(0,1)**2 == -1
    assert mpc(0,1)**3 == mpc(0,-1)
    assert mpc(0,1)**4 == 1
    assert mpc(0,1)**(10**9) == 1
    assert mpc(0,1)**(10**9+1) == mpc(0,1)
    assert mpc(0,1)**(10**9+2) == -1
    assert mpc(0,1)**(10**9+3) == mpc(0,-1)
    assert mpc(3,4)**10 == mpc(-9653287,1476984)
    assert mpc(mpq(1,2), mpq(-5,6))**3 == mpc(mpq(-11,12), mpq(-5,108))
    assert str(mpc(4,-3)) == '(4 - 3*I)'
    assert str(mpc(0,mpq(1,2))) == '(1/2)*I'
    assert mpc(0,1)**(-2) == -1


def test_extended_numbers():
    assert 1*oo == oo
    assert -3*oo == -oo
    assert oo*oo == oo
    assert oo+oo == oo
    assert mpq(1,3)*oo == oo
    assert -oo == (-1)*oo
    assert -(-oo) == oo
    assert oo - oo == nan
    assert -oo + -oo == -oo
    assert -oo - (-oo) == nan
    assert oo + nan == nan
    assert (mpc(0,1)*oo)*mpc(0,1) == -oo
    assert zoo * oo == zoo
    assert zoo * -oo == zoo
    assert zoo * nan == nan
    assert zoo + nan == nan
    assert 0*oo == nan
    assert 0*zoo == nan
    assert 0*nan == nan

def test_extended_cmp():
    assert -oo < oo
    assert -oo < 3
    assert -oo < mpq(-5,4)
    assert -oo <= 3
    assert -oo <= -oo
    assert not (-oo > 3)
    assert not (-oo > -oo)
    assert not (-oo < -oo)
    assert oo > 3
    assert oo > -oo
    assert oo <= oo
    assert not (oo < 3)
    assert not (oo < oo)
    assert not (oo > oo)
    assert not (nan < nan)
    assert not (nan > nan)
    assert max(2, 3, 1, nan, 2) == 3
    assert min(2, 3, 1, nan, 2) == 1
    assert max(2, -oo, oo, 3) == oo
    assert min(2, -oo, oo, 3) == -oo

def test_powers():
    assert try_power(3, 2) == (9, None)
    assert try_power(3, -2) == (mpq(1, 9), None)
    assert try_power(0, -1) == (oo, None)
    assert try_power(mpq(1,2), 0) == (1, None)
    assert try_power(mpc(0, 1), 2) == (-1, None)
    assert try_power(mpc(-1,2), -2) == (mpc(mpq(-3,25), mpq(4,25)), None)
    assert try_power(2, mpq(1, 2)) == (1, (2, mpq(1, 2)))