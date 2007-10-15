from sympy.sandbox.core import Symbol, Rational
from sympy.sandbox.core.add import MutableAdd, Add

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
