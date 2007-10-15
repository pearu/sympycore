
from sympy.sandbox.core import *

def test_integer():
    i = Integer(2)
    j = Integer(3)

    assert i.__class__ == Integer

    assert i==i
    assert i==2
    assert 2==i

    assert i!=j
    assert i!=3
    assert 3!=i

    assert i<j
    assert i<3
    assert 2<j
    
    assert j>i
    assert j>2
    assert 3>i

    assert i<=j
    assert i<=3
    assert i<=2
    assert 2<=j
    assert 3<=j

    assert j>=i
    assert j>=2
    assert 3>=i
    assert j>=3
    assert 2>=i

def test_fraction():
    i = Fraction(6,5)
    j = Fraction(13,4)

    assert i.__class__ == Fraction

    assert i==i
    assert i!=j
    assert i!=3
    assert 3!=i

    assert i<j
    assert i<3
    assert 2<j
    
    assert j>i
    assert j>2
    assert 3>i

    assert i<=j
    assert i<=3
    assert i<=2
    assert 2<=j
    assert 3<=j

    assert j>=i
    assert j>=2
    assert 3>=i
    assert j>=3
    assert 2>=i

def test_float():
    i = Fraction(6,5).as_Float
    j = Fraction(13,4).as_Float

    assert i.__class__ == Float

    assert i==i
    assert i!=j
    assert i!=3
    assert 3!=i

    assert i<j
    assert i<3
    assert 2<j
    
    assert j>i
    assert j>2
    assert 3>i

    assert i<=j
    assert i<=3
    assert i<=2
    assert 2<=j
    assert 3<=j

    assert j>=i
    assert j>=2
    assert 3>=i
    assert j>=3
    assert 2>=i

def test_interval():
    i = Fraction(6,5).as_Interval
    j = Fraction(13,4).as_Interval

    assert i.__class__ == Interval

    assert i==i
    assert i!=j
    assert i!=3
    assert 3!=i

    #TODO: Interval needs __lt__,etc methods
    
if __name__ == '__main__':
    test_integer()
    test_fraction()
    test_float()
    test_interval()
