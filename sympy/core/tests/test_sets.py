
from sympy import *

def test_integers():
    Z = Integers
    n = Fraction(1,2)
    x = Symbol('x')
    assert Z.contains(1)==True
    assert Z.contains(0)==True
    assert Z.contains(-1)==True
    assert Z.contains(45)==True
    assert Z.contains(-450)==True
    assert Z.contains(n)==False
    assert Z.contains(x)==Element(x, Z)

def test_positive_integers():
    P = +Integers
    n = Fraction(1,2)
    x = Symbol('x')
    assert P.contains(1)==True
    assert P.contains(45)==True
    assert P.contains(0)==False
    assert P.contains(-1)==False
    assert P.contains(-5)==False
    assert P.contains(n)==False
    assert P.contains(x)==Element(x, P)

def test_negative_integers():
    N = -Integers
    n = Fraction(1,2)
    x = Symbol('x')
    assert N.contains(1)==False
    assert N.contains(45)==False
    assert N.contains(0)==False
    assert N.contains(-1)==True
    assert N.contains(-5)==True
    assert N.contains(n)==False
    assert N.contains(x)==Element(x, N)

def test_shifted_positive_integers():
    P = +Integers + 3
    n = Fraction(1,2)
    x = Symbol('x')
    assert P.contains(1)==False
    assert P.contains(3)==False
    assert P.contains(4)==True
    assert P.contains(45)==True
    assert P.contains(0)==False
    assert P.contains(-1)==False
    assert P.contains(-5)==False
    assert P.contains(n)==False
    assert P.contains(x)==Element(x, P)

    P = +Integers - 3
    assert P.contains(1)==True
    assert P.contains(45)==True
    assert P.contains(0)==True
    assert P.contains(-1)==True
    assert P.contains(-2)==True
    assert P.contains(-3)==False
    assert P.contains(n)==False
    assert P.contains(x)==Element(x, P)

def test_shifted_negative_integers():
    N = -Integers + 3
    n = Fraction(1,2)
    x = Symbol('x')
    assert N.contains(2)==True
    assert N.contains(3)==False
    assert N.contains(30)==False
    assert N.contains(-5)==True
    assert N.contains(n)==False
    assert N.contains(x)==Element(x, N)

    N = -Integers - 3
    assert N.contains(1)==False
    assert N.contains(45)==False
    assert N.contains(0)==False
    assert N.contains(-1)==False
    assert N.contains(-3)==False
    assert N.contains(-4)==True
    assert N.contains(n)==False
    assert N.contains(x)==Element(x, N)

def test_range_of_integers():
    R = +(-Integers +3) # (0,3) in Z <=> {1,2}
    assert R.contains(-10)==False
    assert R.contains(-1)==False
    assert R.contains(0)==False
    assert R.contains(1)==True
    assert R.contains(2)==True
    assert R.contains(3)==False
    assert R.contains(35)==False

    R = (+(-Integers +5)) + 20 # (20,25) in Z <=> {21,22,23,24}
    assert R.contains(-10)==False
    assert R.contains(-1)==False
    assert R.contains(20)==False
    assert R.contains(21)==True
    assert R.contains(24)==True
    assert R.contains(25)==False
    assert R.contains(35)==False

def test_evens():
    E = Evens
    n = Fraction(1,2)
    x = Symbol('x')
    assert E.contains(-2)==True
    assert E.contains(-1)==False
    assert E.contains(0)==True
    assert E.contains(1)==False
    assert E.contains(2)==True
    assert E.contains(3)==False
    assert E.contains(n)==False
    assert E.contains(x)==Element(x, E)

def test_odds():
    O = Odds
    n = Fraction(1,2)
    x = Symbol('x')
    assert O.contains(-3)==True
    assert O.contains(-2)==False
    assert O.contains(-1)==True
    assert O.contains(0)==False
    assert O.contains(1)==True
    assert O.contains(2)==False
    assert O.contains(3)==True
    assert O.contains(n)==False
    assert O.contains(x)==Element(x, O)

def test_positive_evens():
    E = +Evens
    n = Fraction(1,2)
    x = Symbol('x')
    assert E.contains(-2)==False
    assert E.contains(-1)==False
    assert E.contains(0)==False
    assert E.contains(1)==False
    assert E.contains(2)==True
    assert E.contains(3)==False
    assert E.contains(4)==True
    assert E.contains(5)==False
    assert E.contains(n)==False
    assert E.contains(x)==Element(x, E)

def test_negative_odds():
    O = -Odds
    n = Fraction(1,2)
    x = Symbol('x')
    assert O.contains(-3)==True
    assert O.contains(-2)==False
    assert O.contains(-1)==True
    assert O.contains(0)==False
    assert O.contains(1)==False
    assert O.contains(2)==False
    assert O.contains(3)==False
    assert O.contains(n)==False
    assert O.contains(x)==Element(x, O)

def test_primes():
    P = Primes
    n = Fraction(1,2)
    x = Symbol('x')
    assert P.contains(-3)==False
    assert P.contains(0)==False
    assert P.contains(1)==False
    assert P.contains(2)==True
    assert P.contains(3)==True
    assert P.contains(4)==False
    assert [i for i in range(15) if P.contains(i)]==[2,3,5,7,11,13]
    assert P.contains(n)==False
    assert P.contains(x)==Element(x, P)

    assert -P==Empty
    assert +P==P
    P1 = P+1
    assert [i for i in range(15) if P1.contains(i)]==[3,4,6,8,12,14]
    P2 = P-1
    assert [i for i in range(15) if P2.contains(i)]==[1,2,4,6,10,12]
    P3 = -(P-10)+10
    assert [i for i in range(-15,15) if P3.contains(i)]==[2,3,5,7]
    P4 = +(P-5)+5
    assert [i for i in range(-15,15) if P4.contains(i)]==[7,11,13]
    P5 = +(P3-5)+5
    assert [i for i in range(-15,15) if P5.contains(i)]==[7]
    
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
    
def test_minus():
    assert Minus(Integers, Evens)==Odds
    assert Minus(Integers, Odds)==Evens
    assert Minus(Evens, Odds)==Evens
    assert Minus(Odds, Evens)==Odds

def test_integer_range():
    r = OORange(3,9,Integers)
    assert [i for i in range(0,20) if r.contains(i)]==[4,5,6,7,8]
    r = OCRange(3,9,Integers)
    assert [i for i in range(0,20) if r.contains(i)]==[4,5,6,7,8,9]
    r = CORange(3,9,Integers)
    assert [i for i in range(0,20) if r.contains(i)]==[3,4,5,6,7,8]
    r = CCRange(3,9,Integers)
    assert [i for i in range(0,20) if r.contains(i)]==[3,4,5,6,7,8,9]

def test_range_bounds():
    r = OORange(3,9,Integers)
    assert Min(r)==4
    assert Max(r)==8
    assert Element(3,r)==False
    assert Element(9,r)==False
    r = OCRange(3,9,Integers)
    assert Min(r)==4
    assert Max(r)==9
    assert Element(3,r)==False
    assert Element(9,r)==True
    r = CORange(3,9,Integers)
    assert Min(r)==3
    assert Max(r)==8
    assert Element(3,r)==True
    assert Element(9,r)==False
    r = CCRange(3,9,Integers)
    assert Min(r)==3
    assert Max(r)==9
    assert Element(3,r)==True
    assert Element(9,r)==True

    r = OORange(3,9,Reals)
    assert Min(r)==3
    assert Max(r)==9
    assert Element(3,r)==False
    assert Element(9,r)==False
    r = OCRange(3,9,Reals)
    assert Min(r)==3
    assert Max(r)==9
    assert Element(3,r)==False
    assert Element(9,r)==True
    r = CORange(3,9,Reals)
    assert Min(r)==3
    assert Max(r)==9
    assert Element(3,r)==True
    assert Element(9,r)==False
    r = CCRange(3,9,Reals)
    assert Min(r)==3
    assert Max(r)==9
    assert Element(3,r)==True
    assert Element(9,r)==True

def test_shifted_integer_range():
    r = Shifted(OORange(3,9,Integers),3)
    assert [i for i in range(0,20) if r.contains(i)]==[4+3,5+3,6+3,7+3,8+3]
    r = Shifted(OCRange(3,9,Integers),3)
    assert [i for i in range(0,20) if r.contains(i)]==[4+3,5+3,6+3,7+3,8+3,9+3]
    r = Shifted(CORange(3,9,Integers),3)
    assert [i for i in range(0,20) if r.contains(i)]==[3+3,4+3,5+3,6+3,7+3,8+3]
    r = Shifted(CCRange(3,9,Integers),3)
    assert [i for i in range(0,20) if r.contains(i)]==[3+3,4+3,5+3,6+3,7+3,8+3,9+3]

def test_maximum_range():
    assert OORange(-oo,oo,Integers)==Integers
    assert OCRange(-oo,oo,Integers)==Integers
    assert CORange(-oo,oo,Integers)==Integers
    assert CCRange(-oo,oo,Integers)==Integers

    assert OORange(-oo,oo,Reals)==Reals
    assert OCRange(-oo,oo,Reals)==Reals
    assert CORange(-oo,oo,Reals)==Reals
    assert CCRange(-oo,oo,Reals)==Reals

    assert OORange(oo,-oo,Integers)==Empty

def test_pos_neg_integer_range():
    r = CCRange(-3,3,Integers)
    assert [i for i in range(-10,10) if r.contains(i)]==[-3,-2,-1,0,1,2,3]
    assert [i for i in range(-10,10) if Positive(r).contains(i)]==[1,2,3]
    assert [i for i in range(-10,10) if Negative(r).contains(i)]==[-3,-2,-1]

if __name__=='__main__':
    pass
