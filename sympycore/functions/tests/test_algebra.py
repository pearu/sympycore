
from sympycore import *

def test_add():
    x = Symbol('x')
    f = Function('f')
    g = Function('g')
    assert str(f+g)=='f + g'
    assert str((f+g)(x))=='f(x) + g(x)'
    assert str((f+g)(x, evaluate=False))=='(f + g)(x)'

def test_defined():
    x = Symbol('x')
    f = Function(Sin)
    g = Function('g')
    assert str(f(x))=='Sin(x)'
    assert str(f+g)=='Sin + g'
    assert str((f+g)(x))=='Sin(x) + g(x)'
    assert str((f+g)(x, evaluate=False))=='(Sin + g)(x)'


