
from sympy import *

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
    assert m.is_BasicFunction==False
    assert m.is_BasicFunctionType==False
    assert m.is_Sin==False

def test_Sin_applied():
    s = Sin(2)
    assert s.is_Sin==True
    assert s.is_BasicFunction==True
    assert s.is_Basic==True
    assert s.is_BasicFunctionType==False
    assert s.is_Atom==False
    assert s.is_Cos==False
    assert s.is_Symbol==False
    assert s.is_Number==False
    #assert s.is_UndefinedFunction==False

def test_Sin_unapplied():
    assert Sin.is_Basic==True
    assert Sin.is_Atom==True,`Sin.is_Atom`
    assert Sin.is_BasicFunctionType==True, `Sin.is_BasicFunctionType`
    assert Sin.is_Add==False,`Sin.is_Add`
    assert Sin.is_Symbol==False
    assert Sin.is_BasicFunction==False
    assert Sin.is_Sin==False
    assert Sin.is_Cos==False
    #assert Sin.is_UndefinedFunction==False

def test_undefined_unapplied():
    f = FunctionType('f')
    assert f.is_Basic==True
    assert f.is_Atom==True,`f.is_Atom`
    assert f.is_BasicFunctionType==True, `f.is_BasicFunctionType`
    assert f.is_Add==False,`f.is_Add`
    assert f.is_Symbol==False
    assert f.is_BasicFunction==False
    assert f.is_Cos==False
    #assert f.is_UndefinedFunction==False

def test_undefined_applied():
    f = FunctionType('f')
    x = Symbol('x')
    g=f(x)
    assert g.is_Basic==True
    assert g.is_BasicFunction==True,`g.is_BasicFunction`
    assert g.is_BasicFunctionType==False
    assert g.is_Basic==True
    assert g.is_Add==False
    assert g.is_Symbol==False
    assert g.is_BasicFunction==True
    assert g.is_Cos==False
    #assert g.is_UndefinedFunction==True
