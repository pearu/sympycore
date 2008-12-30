
from sympycore import *

def test_add():
    x = Symbol('x')
    f = Function('f')
    g = Function('g')
    assert str(f+g) in ['f + g', 'g + f'], str(f+g)
    assert str((f+g)(x)) in ['f(x) + g(x)', 'g(x) + f(x)'],  str((f+g)(x))
    assert str((f+g)(x, evaluate=False)) in ['(f + g)(x)',
                                             '(g + f)(x)'], str((f+g)(x, evaluate=False))

def test_defined():
    x = Symbol('x')
    f = Function(Sin)
    g = Function('g')
    assert str(f(x))=='Sin(x)'
    assert str(f+g)=='Sin + g', str(f+g)
    assert str((f+g)(x))=='Sin(x) + g(x)'
    assert str((f+g)(x, evaluate=False))=='(Sin + g)(x)'


