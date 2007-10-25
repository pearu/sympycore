
from sympy import *

def test_I():

    assert str(I)=='I'
    assert I**2==-1
    assert I**3==-I
    assert I**4==1
    assert I**5==I
    assert I**6==-1
    assert I**7==-I
    assert I**8==1

    assert (-1)**Fraction(1,2)==I
    assert (-4)**Fraction(1,2)==2*I
    assert (-Fraction(4,9))**Fraction(1,2)==2*I/3

def test_oo():
    assert str(oo)=='oo'
    assert oo**2==oo
    assert (-oo)**2==oo
    assert (-oo)**3==-oo
    assert oo**Fraction(-2,3)==0
    assert oo**Fraction(2,3)==oo
    assert 2**oo==oo
    assert oo**0==1
    assert oo**oo==oo
    assert oo**(-oo)==0
    assert oo**nan==nan
    assert (-oo)**Fraction(1,2)==I*oo
    assert (-oo)**Fraction(3,2)==-I*oo
    assert Fraction(1,2)**oo==0
    assert Fraction(-1,2)**oo==0
    assert Fraction(3,2)**oo==oo
    assert Fraction(1,2).as_Float**oo==0
    assert Fraction(-1,2).as_Float**oo==0
    assert Fraction(3,2).as_Float**oo==oo
    assert 1**oo==1
    assert 0**oo==0
    assert (-1)**oo==nan
    assert Fraction(-3,2)**oo==nan
    assert Fraction(-3,2).as_Float**oo==nan

    #assert oo+1==oo

def test_nan():
    assert str(nan)=='nan'
    assert nan**2==nan
    assert 2**nan==nan
    assert 1**nan==1
    assert 0**nan==nan



if __name__ == '__main__':
    test_I()
    test_oo()
    test_nan()
