from sympy import Symbol, Rational
from sympy.arithmetic.add import MutableAdd, Add, Sub

a = Symbol("a")
b = Symbol("b")
c = Symbol("c")

def test_add_update():
    s = MutableAdd()
    assert dict(s)=={}
    s.update(a)
    assert dict(s)=={a:1}
    s.update(a)
    assert dict(s)=={a:2}
    s.update(b)
    assert dict(s)=={a:2,b:1}
    s.update(3)
    assert dict(s)=={a:2,b:1,1:3}
    s.update(-b)
    assert dict(s)=={a:2,b:0,1:3}
    assert dict(Add(s))=={a:2,1:3}
    s.update(s)
    assert dict(s)=={a:4,b:0,1:6}
    s.update(a+b)
    assert dict(s)=={a:5,b:1,1:6}
    s.update(a*b)
    assert dict(s)=={a:5,b:1,a*b:1,1:6}
    assert dict(s.canonical())=={a:5,b:1,a*b:1,1:6}
    assert s.__class__==Add

def test_operations():
    assert Add() == 0
    assert Add(a, 0) == a
    assert Add(2, a, 3) == 5+a
    assert Sub() == 0
    assert Sub(1, a) == 1-a
    assert Sub(a, 4, b) == a-(4+b)

def test_mutable():
    s1 = MutableAdd(4,2)
    s2 = MutableAdd(3,2)
    s3 = MutableAdd(2,2,2)

    assert s1.torepr()=='MutableAdd({1: 6})'
    assert s2.torepr()=='MutableAdd({1: 5})'
    assert s3.torepr()=='MutableAdd({1: 6})'
    
    assert s1.canonical().compare(s2.canonical())==1
    assert s1.compare(s2)==1
    assert s2.compare(s1)==-1
    assert s2.compare(s2)==0

    assert s1==s3
    assert s1==s1
    assert s1!=s2

    assert s1.replace(s1,s2)==s2
