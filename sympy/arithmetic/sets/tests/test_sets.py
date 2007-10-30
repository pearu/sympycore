
from sympy import *

def test_integers():
    Z = Integers
    n = Fraction(1,2)
    x = Symbol('x')
    assert Element(1,Z)==True
    assert Element(0,Z)==True
    assert Element(-1,Z)==True
    assert Element(45,Z)==True
    assert Element(-450,Z)==True
    assert Element(n,Z)==False
    assert Element(x,Z).is_Element==True

def test_positive_integers():
    P = +Integers
    n = Fraction(1,2)
    x = Symbol('x')
    assert Element(1,P)==True
    assert Element(45,P)==True
    assert Element(0,P)==False
    assert Element(-1,P)==False
    assert Element(-5,P)==False
    assert Element(n,P)==False
    assert Element(x,P).is_Element

def test_negative_integers():
    N = -Integers
    n = Fraction(1,2)
    x = Symbol('x')
    assert Element(1,N)==False
    assert Element(45,N)==False
    assert Element(0,N)==False
    assert Element(-1,N)==True
    assert Element(-5,N)==True
    assert Element(n,N)==False
    assert Element(x,N).is_Element

def test_shifted_positive_integers():
    P = +Integers + 3
    n = Fraction(1,2)
    x = Symbol('x')
    assert Element(1,P)==False
    assert Element(3,P)==False
    assert Element(4,P)==True
    assert Element(45,P)==True
    assert Element(0,P)==False
    assert Element(-1,P)==False
    assert Element(-5,P)==False
    assert Element(n,P)==False
    assert Element(x,P).is_Element

    P = +Integers - 3
    assert Element(1,P)==True
    assert Element(45,P)==True
    assert Element(0,P)==True
    assert Element(-1,P)==True
    assert Element(-2,P)==True
    assert Element(-3,P)==False
    assert Element(n,P)==False
    assert Element(x,P).is_Element

def test_shifted_negative_integers():
    N = -Integers + 3
    n = Fraction(1,2)
    x = Symbol('x')
    assert Element(2,N)==True
    assert Element(3,N)==False
    assert Element(30,N)==False
    assert Element(-5,N)==True
    assert Element(n,N)==False
    assert Element(x,N).is_Element

    N = -Integers - 3
    assert Element(1,N)==False
    assert Element(45,N)==False
    assert Element(0,N)==False
    assert Element(-1,N)==False
    assert Element(-3,N)==False
    assert Element(-4,N)==True
    assert Element(n,N)==False
    assert Element(x,N).is_Element

def test_range_of_integers():
    R = +(-Integers +3) # (0,3) in Z <=> {1,2}
    assert Element(-10,R)==False
    assert Element(-1,R)==False
    assert Element(0,R)==False
    assert Element(1,R)==True
    assert Element(2,R)==True
    assert Element(3,R)==False
    assert Element(35,R)==False

    R = (+(-Integers +5)) + 20 # (20,25) in Z <=> {21,22,23,24}
    assert Element(-10,R)==False
    assert Element(-1,R)==False
    assert Element(20,R)==False
    assert Element(21,R)==True
    assert Element(24,R)==True
    assert Element(25,R)==False
    assert Element(35,R)==False


def test_evens():
    E = Evens
    n = Fraction(1,2)
    x = Symbol('x')
    assert Element(-2,E)==True
    assert Element(-1,E)==False
    assert Element(0,E)==True
    assert Element(1,E)==False
    assert Element(2,E)==True
    assert Element(3,E)==False
    assert Element(n,E)==False
    assert Element(x,E).is_Element

def test_odds():
    O = Odds
    n = Fraction(1,2)
    x = Symbol('x')
    assert Element(-3,O)==True
    assert Element(-2,O)==False
    assert Element(-1,O)==True
    assert Element(0,O)==False
    assert Element(1,O)==True
    assert Element(2,O)==False
    assert Element(3,O)==True
    assert Element(n,O)==False
    assert Element(x,O).is_Element

def test_positive_evens():
    E = +Evens
    n = Fraction(1,2)
    x = Symbol('x')
    assert Element(-2,E)==False
    assert Element(-1,E)==False
    assert Element(0,E)==False
    assert Element(1,E)==False
    assert Element(2,E)==True
    assert Element(3,E)==False
    assert Element(4,E)==True
    assert Element(5,E)==False
    assert Element(n,E)==False
    assert Element(x,E).is_Element

def test_negative_odds():
    O = Negative(Odds)
    n = Fraction(1,2)
    x = Symbol('x')
    assert Element(-3,O)==True
    assert Element(-2,O)==False
    assert Element(-1,O)==True
    assert Element(0,O)==False
    assert Element(1,O)==False
    assert Element(2,O)==False
    assert Element(3,O)==False
    assert Element(n,O)==False
    assert Element(x,O).is_Element

def test_primes():
    P = Primes
    n = Fraction(1,2)
    x = Symbol('x')
    assert Element(-3,P)==False
    assert Element(0,P)==False
    assert Element(1,P)==False
    assert Element(2,P)==True
    assert Element(3,P)==True
    assert Element(4,P)==False
    assert [i for i in range(15) if Element(i,P)]==[2,3,5,7,11,13]
    assert Element(n,P)==False
    assert Element(x,P).is_Element

    assert -P==Empty
    assert +P==P
    P1 = P+1
    assert [i for i in range(15) if P1.try_element(i)]==[3,4,6,8,12,14]
    P2 = P-1
    assert [i for i in range(15) if P2.try_element(i)]==[1,2,4,6,10,12]
    P3 = -(P-10)+10
    assert [i for i in range(-15,15) if P3.try_element(i)]==[2,3,5,7]
    P4 = +(P-5)+5
    assert [i for i in range(-15,15) if P4.try_element(i)]==[7,11,13]
    P5 = +(P3-5)+5
    assert [i for i in range(-15,15) if P5.try_element(i)]==[7]
    
def test_union():
    assert Union(Evens, Odds)==Integers
    assert Union(Evens, Integers)==Integers
    assert Union(Odds, Integers)==Integers

def test_intersection():
    assert Intersection(Evens, Integers)==Evens
    assert Intersection(Odds, Integers)==Odds
    assert Intersection(Odds, Odds)==Odds
    assert Intersection(Odds, Evens)==Empty
    assert Intersection(Evens, Odds)==Empty
    
def test_difference():
    assert Difference(Integers, Evens)==Odds
    assert Difference(Integers, Odds)==Evens
    assert Difference(Evens, Odds)==Evens
    assert Difference(Odds, Evens)==Odds



def test_set_subset():
    assert Subset(Set(1,2), Set(1,2))==True
    assert Subset(Set(1,2), Set(1,2,3))==True
    assert Subset(Set(1,2), Set(1))==False

    assert Subset(Set(1,2), Reals)==True
    assert Subset(Set(1,2), Integers)==True
    assert Subset(Set(1,2.2), Integers)==False
    assert Subset(Integers, Reals)==True

    assert Subset(Set(1,2), Range(0,10))==True
    assert Subset(Set(-1,2), Range(0,10))==False

if __name__=='__main__':
    pass
