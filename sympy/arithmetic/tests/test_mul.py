from sympy import Symbol, Rational
from sympy.arithmetic.add import MutableAdd, Add
from sympy.arithmetic.mul import MutableMul, Mul


a = Symbol("a")
b = Symbol("b")
c = Symbol("c")


def test_add_update():
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

