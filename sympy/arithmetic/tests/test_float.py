
from sympy import *

def test_str():
    assert Float('1.2').tostr()=='1.2'
    assert Float(2).tostr()=='2'
    assert Float(1.1111,15).tostr()=='1.111'
    assert Float(Fraction(1,2)).tostr()=='0.5'

def test_comparison():
    assert (Float(1.2)==Float(1.2))==True
    assert (Float(1.2,53)==Float(1.2,80))==False
    assert (Float(1.2)==Float(1.1))==False
    assert (Float(1.2)!=Float(1.1))==True
    assert (Float(1.2) < 2)==True
    assert (Float(1.2) > 2)==False
    assert (Float(1.2) <= 1)==False
    assert (Float(1.2) >= 1)==True

def test_arithmetic():
    assert +Float(1.2)==Float(1.2)
    assert -Float(1.2)==Float(-1.2)
    assert Float(1.2)+1==Float(1+1.2)
    assert 1+Float(1.2)==Float(1+1.2)
    assert Float(1.2)-1==Float(1.2-1)
    assert 1-Float(1.2)==Float(1-1.2)
    assert Float(1.2)*2==Float(1.2*2)
    assert 2*Float(1.2)==Float(1.2*2)
    assert Float(1.2)/2==Float(1.2/2)
    assert 2/Float(1.2)==Float(2/1.2)
    assert Float(1.2)**2==Float(1.2**2)
    assert Float(2**Float(1.2),40)==Float(2**1.2,40)
