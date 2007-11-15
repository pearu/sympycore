from sympy import *

a = Symbol("a")
b = Symbol("b")
c = Symbol("c")

def xtest_add_update(): # TOBEREMOVED
    s = MutableMul()
    assert dict(s)=={}
    s.update(a)
    assert dict(s)=={a:1}
    s.update(a)
    assert dict(s)=={a:2}
    s.update(b)
    assert dict(s)=={a:2,b:1}
    s.update(3)
    assert dict(s)=={a:2,b:1,3:1}
    s.update(b,-1)
    assert dict(s)=={a:2,b:0,3:1}
    s.update(3*a)
    assert dict(s)=={a:3,b:0,3:2}
    s.update(2,3)
    assert dict(s)=={a:3,b:0,3:2,2:3}
    assert Mul(s)==Add({a**3:Rational(72)})

def test_operations():
    assert Mul() == 1
    assert Mul(3) == 3
    assert Mul(0, 2) == 0
    assert Mul(2, 3, a) == 6*a
    assert Div() == 1
    assert Div(3) == Rational(1,3)
    assert Div(2,a) == 2/a
    assert Div(2,a,b) == 2/(a*b)
    assert Pow(a,2) == a*a
    assert Sqrt(a) == a**Rational(1,2)
    assert Sqrt(0) == 0
    assert Sqrt(-1) == I
    assert Pow(I, -1) == -I
