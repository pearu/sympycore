
from sympy import *

def test_simple():
    s = Symbol('s')
    i = Integer(2)
    f = Fraction(2,3)
    a = 2+s
    m = a * s

    assert isinstance(s, classes.Symbol)==True
    assert isinstance(s, classes.Basic)==True
    assert isinstance(s, classes.Atom)==True
    assert isinstance(s, classes.Integer)==False
    assert isinstance(s, classes.Number)==False
    assert isinstance(s, classes.Add)==False
    assert isinstance(s, classes.Mul)==False

    assert isinstance(i, classes.Atom)==True
    assert isinstance(i, classes.Integer)==True
    assert isinstance(i, classes.Basic)==True
    assert isinstance(i, classes.Number)==True
    assert isinstance(i, classes.Rational)==True
    assert isinstance(i, classes.Symbol)==False
    assert isinstance(i, classes.Add)==False
    assert isinstance(i, classes.Mul)==False
    assert isinstance(i, classes.Fraction)==False

    assert isinstance(f, classes.Fraction)==True
    assert isinstance(f, classes.Basic)==True
    assert isinstance(f, classes.Number)==True
    assert isinstance(f, classes.Rational)==True
    assert isinstance(f, classes.Atom)==True
    assert isinstance(f, classes.Integer)==False
    assert isinstance(f, classes.Symbol)==False
    assert isinstance(f, classes.Add)==False
    assert isinstance(f, classes.Mul)==False

    assert isinstance(a, classes.Add)==True
    assert isinstance(a, classes.Basic)==True
    assert isinstance(a, classes.Integer)==False
    assert isinstance(a, classes.Number)==False
    assert isinstance(a, classes.Rational)==False
    assert isinstance(a, classes.Symbol)==False
    assert isinstance(a, classes.Mul)==False

    assert isinstance(m, classes.Mul)==True
    assert isinstance(m, classes.Basic)==True
    assert isinstance(m, classes.Integer)==False
    assert isinstance(m, classes.Number)==False
    assert isinstance(m, classes.Rational)==False
    assert isinstance(m, classes.Symbol)==False
    assert isinstance(m, classes.Add)==False
    assert isinstance(m, classes.BasicFunction)==True
    assert isinstance(m, classes.BasicFunctionType)==False
    assert isinstance(m, classes.Sin)==False

def test_Sin_applied():
    s = Sin(2)
    assert isinstance(s, classes.Sin)==True
    assert isinstance(s, classes.BasicFunction)==True
    assert isinstance(s, classes.Basic)==True
    assert isinstance(s, classes.BasicFunctionType)==False
    assert isinstance(s, classes.Atom)==False
    assert isinstance(s, classes.Cos)==False
    assert isinstance(s, classes.Symbol)==False
    assert isinstance(s, classes.Number)==False
    #assert isinstance(s, classes.UndefinedFunction)==False

def test_Sin_unapplied():
    assert isinstance(Sin, classes.Basic)==True
    assert isinstance(Sin, classes.Atom)==True,`isinstance(Sin, classes.Atom)`
    assert isinstance(Sin, classes.BasicFunctionType)==True, `isinstance(Sin, classes.BasicFunctionType)`
    assert isinstance(Sin, classes.Add)==False,`isinstance(Sin, classes.Add)`
    assert isinstance(Sin, classes.Symbol)==False
    assert isinstance(Sin, classes.BasicFunction)==False
    assert isinstance(Sin, classes.Sin)==False
    assert isinstance(Sin, classes.Cos)==False
    #assert isinstance(Sin, classes.UndefinedFunction)==False

def test_undefined_unapplied():
    f = FunctionType('f')
    assert isinstance(f, classes.Basic)==True
    assert isinstance(f, classes.Atom)==True,`isinstance(f, classes.Atom)`
    assert isinstance(f, classes.BasicFunctionType)==True, `isinstance(f, classes.BasicFunctionType)`
    assert isinstance(f, classes.Add)==False,`isinstance(f, classes.Add)`
    assert isinstance(f, classes.Symbol)==False
    assert isinstance(f, classes.BasicFunction)==False
    assert isinstance(f, classes.Cos)==False
    #assert isinstance(f, classes.UndefinedFunction)==False

def test_undefined_applied():
    f = FunctionType('f')
    x = Symbol('x')
    g=f(x)
    assert isinstance(g, classes.Basic)==True
    assert isinstance(g, classes.BasicFunction)==True,`isinstance(g, classes.BasicFunction)`
    assert isinstance(g, classes.BasicFunctionType)==False
    assert isinstance(g, classes.Basic)==True
    assert isinstance(g, classes.Add)==False
    assert isinstance(g, classes.Symbol)==False
    assert isinstance(g, classes.BasicFunction)==True
    assert isinstance(g, classes.Cos)==False
    #assert isinstance(g, classes.UndefinedFunction)==True
