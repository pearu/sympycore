
from sympy import *

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

def test_union_range():
    r1 = OORange(0,10,Integers)
    r2 = OORange(5,15,Integers)
    assert Union(r1,r2)==OORange(0,15,Integers)

    r3 = OORange(10,15,Integers)
    assert Union(r1,r3).is_Union
    assert Union(r1,r3-1)==OORange(0,14,Integers)
    r3 = CORange(10,15,Integers)
    assert Union(r1,r3)==OORange(0,15,Integers)

    r4 = OORange(2,7,Integers)
    assert Union(r1,r4)==r1

    assert Union(Positive(Integers),Negative(Integers)).is_Union
    assert Union(Positive(Integers),Negative(Integers)+1)==Integers
    assert Union(Positive(Integers)-1,Negative(Integers))==Integers
    assert Union(Positive(Integers)+3,OORange(0,4,Integers))==Positive(Integers)

def test_minus_range():
    r1 = OORange(0,10,Integers)
    r2 = OORange(5,15,Integers)
    assert Minus(r1,r2)==OCRange(0,5,Integers)
    r2 = CORange(5,15,Integers)
    assert Minus(r1,r2)==OORange(0,5,Integers)

    rbig = OORange(0,20,Integers)
    r0 = OORange(5,15,Integers)
    assert Minus(rbig,r0)==Union(CORange(15, 20, Integers), OCRange(0, 5, Integers))

def test_intersection_range():
    r1 = OORange(0,10,Integers)
    r2 = OORange(5,15,Integers)
    assert Intersection(r1,r2)==OORange(5,10,Integers)

def xtest_bug1_intersection_range():
    assert Intersection(Range(0,10), Range(3,15))==CCRange(3,10,Reals)

def test_union_real_ranges():
    OO = Range
    OC = lambda s,e: OCRange(s,e,Reals)
    CO = lambda s,e: CORange(s,e,Reals)
    CC = lambda s,e: CCRange(s,e,Reals)

    assert Union(OO(1,4),OO(1,6))==OO(1,6)
    assert Union(OO(1,4),OO(2,3))==OO(1,4)
    assert Union(OO(1,4),OO(2,4))==OO(1,4)
    assert Union(OO(1,4),OO(2,6))==OO(1,6)
    assert Union(OO(1,4),OO(4,6)).is_Union
    assert Union(OO(1,4),OO(5,6)).is_Union

    assert Union(OO(1,4),CO(1,4))==CO(1,4)
    assert Union(OO(1,4),CO(1,6))==CO(1,6)
    assert Union(OO(1,4),CO(2,3))==OO(1,4)
    assert Union(OO(1,4),CO(2,4))==OO(1,4)
    assert Union(OO(1,4),CO(2,6))==OO(1,6)
    assert Union(OO(1,4),CO(4,6))==OO(1,6)
    assert Union(OO(1,4),CO(5,6)).is_Union

    assert Union(OO(1,4),OC(1,4))==OC(1,4)
    assert Union(OO(1,4),OC(1,6))==OC(1,6)
    assert Union(OO(1,4),OC(2,3))==OO(1,4)
    assert Union(OO(1,4),OC(2,4))==OC(1,4)
    assert Union(OO(1,4),OC(2,6))==OC(1,6)
    assert Union(OO(1,4),OC(4,6)).is_Union
    assert Union(OO(1,4),OC(5,6)).is_Union

    assert Union(OO(1,4),CC(1,4))==CC(1,4)
    assert Union(OO(1,4),CC(1,6))==CC(1,6)
    assert Union(OO(1,4),CC(2,3))==OO(1,4)
    assert Union(OO(1,4),CC(2,4))==OC(1,4)
    assert Union(OO(1,4),CC(2,6))==OC(1,6)
    assert Union(OO(1,4),CC(4,6))==OC(1,6)
    assert Union(OO(1,4),CC(5,6)).is_Union

    assert Union(CO(1,4),CO(1,4))==CO(1,4)
    assert Union(CO(1,4),CO(1,6))==CO(1,6)
    assert Union(CO(1,4),CO(2,3))==CO(1,4)
    assert Union(CO(1,4),CO(2,4))==CO(1,4)
    assert Union(CO(1,4),CO(2,6))==CO(1,6)
    assert Union(CO(1,4),CO(4,6))==CO(1,6)
    assert Union(CO(1,4),CO(5,6)).is_Union

    assert Union(CO(1,4),OC(1,4))==CC(1,4)
    assert Union(CO(1,4),OC(1,6))==CC(1,6)
    assert Union(CO(1,4),OC(2,3))==CO(1,4)
    assert Union(CO(1,4),OC(2,4))==CC(1,4)
    assert Union(CO(1,4),OC(2,6))==CC(1,6)
    assert Union(CO(1,4),OC(4,6)).is_Union
    assert Union(CO(1,4),OC(5,6)).is_Union

    assert Union(CO(1,4),CC(1,4))==CC(1,4)
    assert Union(CO(1,4),CC(1,6))==CC(1,6)
    assert Union(CO(1,4),CC(2,3))==CO(1,4)
    assert Union(CO(1,4),CC(2,4))==CC(1,4)
    assert Union(CO(1,4),CC(2,6))==CC(1,6)
    assert Union(CO(1,4),CC(4,6))==CC(1,6)
    assert Union(CO(1,4),CC(5,6)).is_Union

    assert Union(OC(1,4),OC(1,4))==OC(1,4)
    assert Union(OC(1,4),OC(1,6))==OC(1,6)
    assert Union(OC(1,4),OC(2,3))==OC(1,4)
    assert Union(OC(1,4),OC(2,4))==OC(1,4)
    assert Union(OC(1,4),OC(2,6))==OC(1,6)
    assert Union(OC(1,4),OC(4,6))==OC(1,6)
    assert Union(OC(1,4),OC(5,6)).is_Union

    assert Union(OC(1,4),CC(1,4))==CC(1,4)
    assert Union(OC(1,4),CC(1,6))==CC(1,6)
    assert Union(OC(1,4),CC(2,3))==OC(1,4)
    assert Union(OC(1,4),CC(2,4))==OC(1,4)
    assert Union(OC(1,4),CC(2,6))==OC(1,6)
    assert Union(OC(1,4),CC(4,6))==OC(1,6)
    assert Union(OC(1,4),CC(5,6)).is_Union

    assert Union(CC(1,4),CC(1,4))==CC(1,4)
    assert Union(CC(1,4),CC(1,6))==CC(1,6)
    assert Union(CC(1,4),CC(2,3))==CC(1,4)
    assert Union(CC(1,4),CC(2,4))==CC(1,4)
    assert Union(CC(1,4),CC(2,6))==CC(1,6)
    assert Union(CC(1,4),CC(4,6))==CC(1,6)
    assert Union(CC(1,4),CC(5,6)).is_Union

def test_union_symbolic_ranges():
    OO = Range
    OC = lambda s,e: OCRange(s,e,Reals)
    CO = lambda s,e: CORange(s,e,Reals)
    CC = lambda s,e: CCRange(s,e,Reals)
    a = Symbol('a')
    b = Symbol('b')
    assert Union(OO(b-1,b+1), OO(b,b+2))==OO(b-1,b+2)
    assert Union(OO(b-1,b+1), OC(b,b+2))==OC(b-1,b+2)
    assert Union(OO(b-1,b), CO(b,b+2))==OO(b-1,b+2)
    assert Union(OO(b-1,a), CO(a,b+2))==OO(b-1,b+2)
    assert Union(OO(b-1,a), CC(a,b+2))==OC(b-1,b+2)
    assert Union(OC(b-1,b+1), OC(b,b+2))==OC(b-1,b+2)
    assert Union(OC(b-1,b+1), CC(b,b+2))==OC(b-1,b+2)
    assert Union(OC(b-1,a), OC(a,b+2))==OC(b-1,b+2)
    assert Union(CC(b-1,a), OC(a,b+2))==CC(b-1,b+2)
    assert Union(CC(b-1,b+1), OC(b,b+2))==CC(b-1,b+2)

def test_intersection_real_ranges():
    OO = Range
    OC = lambda s,e: OCRange(s,e,Reals)
    CO = lambda s,e: CORange(s,e,Reals)
    CC = lambda s,e: CCRange(s,e,Reals)

    assert Intersection(OO(1,4),OO(1,3))==OO(1,3)
    assert Intersection(OO(1,4),OO(1,4))==OO(1,4)
    assert Intersection(OO(1,4),OO(1,6))==OO(1,4)
    assert Intersection(OO(1,4),OO(2,3))==OO(2,3)
    assert Intersection(OO(1,4),OO(2,4))==OO(2,4)
    assert Intersection(OO(1,4),OO(2,6))==OO(2,4)
    assert Intersection(OO(1,4),OO(4,6))==Empty
    assert Intersection(OO(1,4),OO(5,6))==Empty

    assert Intersection(OO(1,4),OC(1,3))==OC(1,3)
    assert Intersection(OO(1,4),OC(1,4))==OO(1,4)
    assert Intersection(OO(1,4),OC(1,6))==OO(1,4)
    assert Intersection(OO(1,4),OC(2,3))==OC(2,3)
    assert Intersection(OO(1,4),OC(2,4))==OO(2,4)
    assert Intersection(OO(1,4),OC(2,6))==OO(2,4)
    assert Intersection(OO(1,4),OC(4,6))==Empty
    assert Intersection(OO(1,4),OC(5,6))==Empty

    assert Intersection(OO(1,4),CO(1,3))==OO(1,3)
    assert Intersection(OO(1,4),CO(1,4))==OO(1,4)
    assert Intersection(OO(1,4),CO(1,6))==OO(1,4)
    assert Intersection(OO(1,4),CO(2,3))==CO(2,3)
    assert Intersection(OO(1,4),CO(2,4))==CO(2,4)
    assert Intersection(OO(1,4),CO(2,6))==CO(2,4)
    assert Intersection(OO(1,4),CO(4,6))==Empty
    assert Intersection(OO(1,4),CO(5,6))==Empty

    assert Intersection(OO(1,4),CC(1,3))==OC(1,3)
    assert Intersection(OO(1,4),CC(1,4))==OO(1,4)
    assert Intersection(OO(1,4),CC(1,6))==OO(1,4)
    assert Intersection(OO(1,4),CC(2,3))==CC(2,3)
    assert Intersection(OO(1,4),CC(2,4))==CO(2,4)
    assert Intersection(OO(1,4),CC(2,6))==CO(2,4)
    assert Intersection(OO(1,4),CC(4,6))==Empty
    assert Intersection(OO(1,4),CC(5,6))==Empty

    assert Intersection(OC(1,4),OC(1,3))==OC(1,3)
    assert Intersection(OC(1,4),OC(1,4))==OC(1,4)
    assert Intersection(OC(1,4),OC(1,6))==OC(1,4)
    assert Intersection(OC(1,4),OC(2,3))==OC(2,3)
    assert Intersection(OC(1,4),OC(2,4))==OC(2,4)
    assert Intersection(OC(1,4),OC(2,6))==OC(2,4)
    assert Intersection(OC(1,4),OC(4,6))==Empty
    assert Intersection(OC(1,4),OC(5,6))==Empty

    assert Intersection(OC(1,4),CO(1,3))==OO(1,3)
    assert Intersection(OC(1,4),CO(1,4))==OO(1,4)
    assert Intersection(OC(1,4),CO(1,6))==OC(1,4)
    assert Intersection(OC(1,4),CO(2,3))==CO(2,3)
    assert Intersection(OC(1,4),CO(2,4))==CO(2,4)
    assert Intersection(OC(1,4),CO(2,6))==CC(2,4)
    assert Intersection(OC(1,4),CO(4,6))==Set(4)
    assert Intersection(OC(1,4),CO(5,6))==Empty

    assert Intersection(OC(1,4),CC(1,3))==OC(1,3)
    assert Intersection(OC(1,4),CC(1,4))==OC(1,4)
    assert Intersection(OC(1,4),CC(1,6))==OC(1,4)
    assert Intersection(OC(1,4),CC(2,3))==CC(2,3)
    assert Intersection(OC(1,4),CC(2,4))==CC(2,4)
    assert Intersection(OC(1,4),CC(2,6))==CC(2,4)
    assert Intersection(OC(1,4),CC(4,6))==Set(4)
    assert Intersection(OC(1,4),CC(5,6))==Empty

    assert Intersection(CO(1,4),CO(1,3))==CO(1,3)
    assert Intersection(CO(1,4),CO(1,4))==CO(1,4)
    assert Intersection(CO(1,4),CO(1,6))==CO(1,4)
    assert Intersection(CO(1,4),CO(2,3))==CO(2,3)
    assert Intersection(CO(1,4),CO(2,4))==CO(2,4)
    assert Intersection(CO(1,4),CO(2,6))==CO(2,4)
    assert Intersection(CO(1,4),CO(4,6))==Empty
    assert Intersection(CO(1,4),CO(5,6))==Empty

    assert Intersection(CO(1,4),CC(1,3))==CC(1,3)
    assert Intersection(CO(1,4),CC(1,4))==CO(1,4)
    assert Intersection(CO(1,4),CC(1,6))==CO(1,4)
    assert Intersection(CO(1,4),CC(2,3))==CC(2,3)
    assert Intersection(CO(1,4),CC(2,4))==CO(2,4)
    assert Intersection(CO(1,4),CC(2,6))==CO(2,4)
    assert Intersection(CO(1,4),CC(4,6))==Empty
    assert Intersection(CO(1,4),CC(5,6))==Empty

    assert Intersection(CC(1,4),CC(1,3))==CC(1,3)
    assert Intersection(CC(1,4),CC(1,4))==CC(1,4)
    assert Intersection(CC(1,4),CC(1,6))==CC(1,4)
    assert Intersection(CC(1,4),CC(2,3))==CC(2,3)
    assert Intersection(CC(1,4),CC(2,4))==CC(2,4)
    assert Intersection(CC(1,4),CC(2,6))==CC(2,4)
    assert Intersection(CC(1,4),CC(4,6))==Set(4)
    assert Intersection(CC(1,4),CC(5,6))==Empty

def test_minus_real_ranges():
    OO = Range
    OC = lambda s,e: OCRange(s,e,Reals)
    CO = lambda s,e: CORange(s,e,Reals)
    CC = lambda s,e: CCRange(s,e,Reals)

    assert Minus(OO(1,4),OO(-1,0))==OO(1,4)
    assert Minus(OO(1,4),OO(-1,1))==OO(1,4)
    assert Minus(OO(1,4),OO(-1,2))==CO(2,4)
    assert Minus(OO(1,4),OO(-1,4))==Empty
    assert Minus(OO(1,4),OO(-1,5))==Empty
    assert Minus(OO(1,4),OO(1,3))==CO(3,4)
    assert Minus(OO(1,4),OO(1,4))==Empty
    assert Minus(OO(1,4),OO(1,5))==Empty
    assert Minus(OO(1,4),OO(2,3))==Union(OC(1,2),CO(3,4))
    assert Minus(OO(1,4),OO(2,4))==OC(1,2)
    assert Minus(OO(1,4),OO(2,5))==OC(1,2)
    assert Minus(OO(1,4),OO(4,5))==OO(1,4)
    assert Minus(OO(1,4),OO(5,6))==OO(1,4)

    assert Minus(OO(1,4),OC(-1,0))==OO(1,4)
    assert Minus(OO(1,4),OC(-1,1))==OO(1,4)
    assert Minus(OO(1,4),OC(-1,2))==OO(2,4)
    assert Minus(OO(1,4),OC(-1,4))==Empty
    assert Minus(OO(1,4),OC(-1,5))==Empty
    assert Minus(OO(1,4),OC(1,3))==OO(3,4)
    assert Minus(OO(1,4),OC(1,4))==Empty
    assert Minus(OO(1,4),OC(1,5))==Empty
    assert Minus(OO(1,4),OC(2,3))==Union(OC(1,2),OO(3,4))
    assert Minus(OO(1,4),OC(2,4))==OC(1,2)
    assert Minus(OO(1,4),OC(2,5))==OC(1,2)
    assert Minus(OO(1,4),OC(4,5))==OO(1,4)
    assert Minus(OO(1,4),OC(5,6))==OO(1,4)

    assert Minus(OO(1,4),CO(-1,0))==OO(1,4)
    assert Minus(OO(1,4),CO(-1,1))==OO(1,4)
    assert Minus(OO(1,4),CO(-1,2))==CO(2,4)
    assert Minus(OO(1,4),CO(-1,4))==Empty
    assert Minus(OO(1,4),CO(-1,5))==Empty
    assert Minus(OO(1,4),CO(1,3))==CO(3,4)
    assert Minus(OO(1,4),CO(1,4))==Empty
    assert Minus(OO(1,4),CO(1,5))==Empty
    assert Minus(OO(1,4),CO(2,3))==Union(OO(1,2),CO(3,4))
    assert Minus(OO(1,4),CO(2,4))==OO(1,2)
    assert Minus(OO(1,4),CO(2,5))==OO(1,2)
    assert Minus(OO(1,4),CO(4,5))==OO(1,4)
    assert Minus(OO(1,4),CO(5,6))==OO(1,4)

    assert Minus(OO(1,4),CC(-1,0))==OO(1,4)
    assert Minus(OO(1,4),CC(-1,1))==OO(1,4)
    assert Minus(OO(1,4),CC(-1,2))==OO(2,4)
    assert Minus(OO(1,4),CC(-1,4))==Empty
    assert Minus(OO(1,4),CC(-1,5))==Empty
    assert Minus(OO(1,4),CC(1,3))==OO(3,4)
    assert Minus(OO(1,4),CC(1,4))==Empty
    assert Minus(OO(1,4),CC(1,5))==Empty
    assert Minus(OO(1,4),CC(2,3))==Union(OO(1,2),OO(3,4))
    assert Minus(OO(1,4),CC(2,4))==OO(1,2)
    assert Minus(OO(1,4),CC(2,5))==OO(1,2)
    assert Minus(OO(1,4),CC(4,5))==OO(1,4)
    assert Minus(OO(1,4),CC(5,6))==OO(1,4)

    assert Minus(OC(1,4),OO(-1,0))==OC(1,4)
    assert Minus(OC(1,4),OO(-1,1))==OC(1,4)
    assert Minus(OC(1,4),OO(-1,2))==CC(2,4)
    assert Minus(OC(1,4),OO(-1,4))==Set(4)
    assert Minus(OC(1,4),OO(-1,5))==Empty
    assert Minus(OC(1,4),OO(1,3))==CC(3,4)
    assert Minus(OC(1,4),OO(1,4))==Set(4)
    assert Minus(OC(1,4),OO(1,5))==Empty
    assert Minus(OC(1,4),OO(2,3))==Union(OC(1,2),CC(3,4))
    assert Minus(OC(1,4),OO(2,4))==Union(OC(1,2),Set(4))
    assert Minus(OC(1,4),OO(2,5))==OC(1,2)
    assert Minus(OC(1,4),OO(4,5))==OO(1,4)
    assert Minus(OC(1,4),OO(5,6))==OC(1,4)

    assert Minus(OC(1,4),OC(-1,0))==OC(1,4)
    assert Minus(OC(1,4),OC(-1,1))==OC(1,4)
    assert Minus(OC(1,4),OC(-1,2))==OC(2,4)
    assert Minus(OC(1,4),OC(-1,4))==Empty
    assert Minus(OC(1,4),OC(-1,5))==Empty
    assert Minus(OC(1,4),OC(1,3))==OC(3,4)
    assert Minus(OC(1,4),OC(1,4))==Empty
    assert Minus(OC(1,4),OC(1,5))==Empty
    assert Minus(OC(1,4),OC(2,3))==Union(OC(1,2),OC(3,4))
    assert Minus(OC(1,4),OC(2,4))==OC(1,2)
    assert Minus(OC(1,4),OC(2,5))==OC(1,2)
    assert Minus(OC(1,4),OC(4,5))==OO(1,4)
    assert Minus(OC(1,4),OC(5,6))==OC(1,4)

    assert Minus(OC(1,4),CO(-1,0))==OC(1,4)
    assert Minus(OC(1,4),CO(-1,1))==OC(1,4)
    assert Minus(OC(1,4),CO(-1,2))==CC(2,4)
    assert Minus(OC(1,4),CO(-1,4))==Set(4)
    assert Minus(OC(1,4),CO(-1,5))==Empty
    assert Minus(OC(1,4),CO(1,3))==CC(3,4)
    assert Minus(OC(1,4),CO(1,4))==Set(4)
    assert Minus(OC(1,4),CO(1,5))==Empty
    assert Minus(OC(1,4),CO(2,3))==Union(OO(1,2),CC(3,4))
    assert Minus(OC(1,4),CO(2,4))==Union(OO(1,2),Set(4))
    assert Minus(OC(1,4),CO(2,5))==OO(1,2)
    assert Minus(OC(1,4),CO(4,5))==OO(1,4)
    assert Minus(OC(1,4),CO(5,6))==OC(1,4)

    assert Minus(OC(1,4),CC(-1,0))==OC(1,4)
    assert Minus(OC(1,4),CC(-1,1))==OC(1,4)
    assert Minus(OC(1,4),CC(-1,2))==OC(2,4)
    assert Minus(OC(1,4),CC(-1,4))==Empty
    assert Minus(OC(1,4),CC(-1,5))==Empty
    assert Minus(OC(1,4),CC(1,3))==OC(3,4)
    assert Minus(OC(1,4),CC(1,4))==Empty
    assert Minus(OC(1,4),CC(1,5))==Empty
    assert Minus(OC(1,4),CC(2,3))==Union(OO(1,2),OC(3,4))
    assert Minus(OC(1,4),CC(2,4))==OO(1,2)
    assert Minus(OC(1,4),CC(2,5))==OO(1,2)
    assert Minus(OC(1,4),CC(4,5))==OO(1,4)
    assert Minus(OC(1,4),CC(5,6))==OC(1,4)

    assert Minus(CO(1,4),OO(-1,0))==CO(1,4)
    assert Minus(CO(1,4),OO(-1,1))==CO(1,4)
    assert Minus(CO(1,4),OO(-1,2))==CO(2,4)
    assert Minus(CO(1,4),OO(-1,4))==Empty
    assert Minus(CO(1,4),OO(-1,5))==Empty
    assert Minus(CO(1,4),OO(1,3))==Union(Set(1),CO(3,4))
    assert Minus(CO(1,4),OO(1,4))==Set(1)
    assert Minus(CO(1,4),OO(1,5))==Set(1)
    assert Minus(CO(1,4),OO(2,3))==Union(CC(1,2),CO(3,4))
    assert Minus(CO(1,4),OO(2,4))==CC(1,2)
    assert Minus(CO(1,4),OO(2,5))==CC(1,2)
    assert Minus(CO(1,4),OO(4,5))==CO(1,4)
    assert Minus(CO(1,4),OO(5,6))==CO(1,4)

    assert Minus(CO(1,4),OC(-1,0))==CO(1,4)
    assert Minus(CO(1,4),OC(-1,1))==OO(1,4)
    assert Minus(CO(1,4),OC(-1,2))==OO(2,4)
    assert Minus(CO(1,4),OC(-1,4))==Empty
    assert Minus(CO(1,4),OC(-1,5))==Empty
    assert Minus(CO(1,4),OC(1,3))==Union(Set(1),OO(3,4))
    assert Minus(CO(1,4),OC(1,4))==Set(1)
    assert Minus(CO(1,4),OC(1,5))==Set(1)
    assert Minus(CO(1,4),OC(2,3))==Union(CC(1,2),OO(3,4))
    assert Minus(CO(1,4),OC(2,4))==CC(1,2)
    assert Minus(CO(1,4),OC(2,5))==CC(1,2)
    assert Minus(CO(1,4),OC(4,5))==CO(1,4)
    assert Minus(CO(1,4),OC(5,6))==CO(1,4)

    assert Minus(CO(1,4),CC(-1,0))==CO(1,4)
    assert Minus(CO(1,4),CC(-1,1))==OO(1,4)
    assert Minus(CO(1,4),CC(-1,2))==OO(2,4)
    assert Minus(CO(1,4),CC(-1,4))==Empty
    assert Minus(CO(1,4),CC(-1,5))==Empty
    assert Minus(CO(1,4),CC(1,3))==OO(3,4)
    assert Minus(CO(1,4),CC(1,4))==Empty
    assert Minus(CO(1,4),CC(1,5))==Empty
    assert Minus(CO(1,4),CC(2,3))==Union(CO(1,2),OO(3,4))
    assert Minus(CO(1,4),CC(2,4))==CO(1,2)
    assert Minus(CO(1,4),CC(2,5))==CO(1,2)
    assert Minus(CO(1,4),CC(4,5))==CO(1,4)
    assert Minus(CO(1,4),CC(5,6))==CO(1,4)

    assert Minus(CC(1,4),OO(-1,0))==CC(1,4)
    assert Minus(CC(1,4),OO(-1,1))==CC(1,4)
    assert Minus(CC(1,4),OO(-1,2))==CC(2,4)
    assert Minus(CC(1,4),OO(-1,4))==Set(4)
    assert Minus(CC(1,4),OO(-1,5))==Empty
    assert Minus(CC(1,4),OO(1,3))==Union(Set(1),CC(3,4))
    assert Minus(CC(1,4),OO(1,4))==Set(1,4)
    assert Minus(CC(1,4),OO(1,5))==Set(1)
    assert Minus(CC(1,4),OO(2,3))==Union(CC(1,2),CC(3,4))
    assert Minus(CC(1,4),OO(2,4))==Union(CC(1,2),Set(4))
    assert Minus(CC(1,4),OO(2,5))==CC(1,2)
    assert Minus(CC(1,4),OO(4,5))==CC(1,4)
    assert Minus(CC(1,4),OO(5,6))==CC(1,4)

    assert Minus(CC(1,4),OC(-1,0))==CC(1,4)
    assert Minus(CC(1,4),OC(-1,1))==OC(1,4)
    assert Minus(CC(1,4),OC(-1,2))==OC(2,4)
    assert Minus(CC(1,4),OC(-1,4))==Empty
    assert Minus(CC(1,4),OC(-1,5))==Empty
    assert Minus(CC(1,4),OC(1,3))==Union(Set(1),OC(3,4))
    assert Minus(CC(1,4),OC(1,4))==Set(1)
    assert Minus(CC(1,4),OC(1,5))==Set(1)
    assert Minus(CC(1,4),OC(2,3))==Union(CC(1,2),OC(3,4))
    assert Minus(CC(1,4),OC(2,4))==CC(1,2)
    assert Minus(CC(1,4),OC(2,5))==CC(1,2)
    assert Minus(CC(1,4),OC(4,5))==CC(1,4)
    assert Minus(CC(1,4),OC(5,6))==CC(1,4)

    assert Minus(CC(1,4),CO(-1,0))==CC(1,4)
    assert Minus(CC(1,4),CO(-1,1))==CC(1,4)
    assert Minus(CC(1,4),CO(-1,2))==CC(2,4)
    assert Minus(CC(1,4),CO(-1,4))==Set(4)
    assert Minus(CC(1,4),CO(-1,5))==Empty
    assert Minus(CC(1,4),CO(1,3))==CC(3,4)
    assert Minus(CC(1,4),CO(1,4))==Set(4)
    assert Minus(CC(1,4),CO(1,5))==Empty
    assert Minus(CC(1,4),CO(2,3))==Union(CO(1,2),CC(3,4))
    assert Minus(CC(1,4),CO(2,4))==Union(CO(1,2),Set(4))
    assert Minus(CC(1,4),CO(2,5))==CO(1,2)
    assert Minus(CC(1,4),CO(4,5))==CO(1,4)
    assert Minus(CC(1,4),CO(5,6))==CC(1,4)

    assert Minus(CC(1,4),CC(-1,0))==CC(1,4)
    assert Minus(CC(1,4),CC(-1,1))==OC(1,4)
    assert Minus(CC(1,4),CC(-1,2))==OC(2,4)
    assert Minus(CC(1,4),CC(-1,4))==Empty
    assert Minus(CC(1,4),CC(-1,5))==Empty
    assert Minus(CC(1,4),CC(1,3))==OC(3,4)
    assert Minus(CC(1,4),CC(1,4))==Empty
    assert Minus(CC(1,4),CC(1,5))==Empty
    assert Minus(CC(1,4),CC(2,3))==Union(CO(1,2),OC(3,4))
    assert Minus(CC(1,4),CC(2,4))==CO(1,2)
    assert Minus(CC(1,4),CC(2,5))==CO(1,2)
    assert Minus(CC(1,4),CC(4,5))==CO(1,4)
    assert Minus(CC(1,4),CC(5,6))==CC(1,4)
