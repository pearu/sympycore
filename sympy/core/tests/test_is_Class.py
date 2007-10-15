
from sympy.sandbox import *

def test_simple():
    s = Symbol('s')
    i = Integer(2)
    f = Fraction(2,3)
    a = 2+s
    m = a * s

    assert s.is_Symbol==True
    assert s.is_Basic==True
    assert s.is_Atom==True
    assert s.is_Integer==False
    assert s.is_Number==False
    assert s.is_Add==False
    assert s.is_Mul==False

    assert i.is_Atom==True
    assert i.is_Integer==True
    assert i.is_Basic==True
    assert i.is_Number==True
    assert i.is_Rational==True
    assert i.is_Symbol==False
    assert i.is_Add==False
    assert i.is_Mul==False
    assert i.is_Fraction==False

    assert f.is_Fraction==True
    assert f.is_Basic==True
    assert f.is_Number==True
    assert f.is_Rational==True
    assert f.is_Atom==True
    assert f.is_Integer==False
    assert f.is_Symbol==False
    assert f.is_Add==False
    assert f.is_Mul==False

    assert a.is_Add==True
    assert a.is_Basic==True
    assert a.is_Integer==False
    assert a.is_Number==False
    assert a.is_Rational==False
    assert a.is_Symbol==False
    assert a.is_Mul==False

    assert m.is_Mul==True
    assert m.is_Basic==True
    assert m.is_Integer==False
    assert m.is_Number==False
    assert m.is_Rational==False
    assert m.is_Symbol==False
    assert m.is_Add==False
    assert m.is_Function==False
    assert m.is_FunctionClass==False
    assert m.is_sin==False

def test_sin_applied():
    s = sin(2)
    assert s.is_sin==True
    assert s.is_Function==True
    assert s.is_Basic==True
    assert s.is_FunctionClass==False
    assert s.is_Atom==False
    assert s.is_cos==False
    assert s.is_Symbol==False
    assert s.is_Number==False
    assert s.is_UndefinedFunction==False

def test_sin_unapplied():
    assert sin.is_Basic==True
    assert sin.is_Atom==True,`sin.is_Atom`
    assert sin.is_FunctionClass==True, `sin.is_FunctionClass`
    assert sin.is_Add==False,`sin.is_Add`
    assert sin.is_Symbol==False
    assert sin.is_Function==False
    assert sin.is_sin==False
    assert sin.is_cos==False
    assert sin.is_UndefinedFunction==False

def test_undefined_unapplied():
    f = Function('f')
    assert f.is_Basic==True
    assert f.is_Atom==True,`f.is_Atom`
    assert f.is_FunctionClass==True, `f.is_FunctionClass`
    assert f.is_Add==False,`f.is_Add`
    assert f.is_Symbol==False
    assert f.is_Function==False
    assert f.is_cos==False
    assert f.is_UndefinedFunction==False

def test_undefined_applied():
    f = Function('f')
    x = Symbol('x')
    g=f(x)
    assert g.is_Basic==True
    assert g.is_Function==True,`g.is_Function`
    assert g.is_FunctionClass==False
    assert g.is_Basic==True
    assert g.is_UndefinedFunction==True
    assert g.is_Add==False
    assert g.is_Symbol==False
    assert g.is_Function==True
    assert g.is_cos==False
