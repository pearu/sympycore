
from sympy import *

def test_sympify():
    assert sympify('x+2/3')==Symbol('x')+Fraction(2,3)

def test_and():
    assert sympify('x and y')==And(Boolean('x'),Boolean('y'))
    assert sympify('x and +y')==And(Boolean('x'),Equal(Symbol('y'),0))
    assert sympify('x and -y')==And(Boolean('x'),Equal(-Symbol('y'),0))
    assert sympify('x and y+1')==And(Boolean('x'),Equal(Symbol('y')+1,0))
    assert sympify('x and y-1')==And(Boolean('x'),Equal(Symbol('y')-1,0))
    assert sympify('x and 2*y')==And(Boolean('x'),Equal(2*Symbol('y'),0))
    assert sympify('x and 2**y')==And(Boolean('x'),Equal(2**Symbol('y'),0))

def test_or():
    assert sympify('x or y')==Or(Boolean('x'),Boolean('y'))
    assert sympify('x or +y')==Or(Boolean('x'),Equal(Symbol('y'),0))
    assert sympify('x or -y')==Or(Boolean('x'),Equal(-Symbol('y'),0))
    assert sympify('x or y+1')==Or(Boolean('x'),Equal(Symbol('y')+1,0))
    assert sympify('x or y-1')==Or(Boolean('x'),Equal(Symbol('y')-1,0))
    assert sympify('x or 2*y')==Or(Boolean('x'),Equal(2*Symbol('y'),0))
    assert sympify('x or 2**y')==Or(Boolean('x'),Equal(2**Symbol('y'),0))

def test_not():
    assert sympify('not x')==Not(Boolean('x'))
    assert sympify('not +x')==Not(Equal(Symbol('x'),0))
    assert sympify('not -x')==Not(Equal(-Symbol('x'),0))
    assert sympify('not x+1')==Not(Equal(Symbol('x')+1,0))
    assert sympify('not x-1')==Not(Equal(Symbol('x')-1,0))
    assert sympify('not 2*x')==Not(Equal(Symbol('x')*2,0))
    assert sympify('not x**2')==Not(Equal(Symbol('x')**2,0))
    assert sympify('not 1')==Not(Equal(1,0))
    z = Symbol('z')
    assert sympify('not z')==Not(Equal(z,0))


def test_comparison():
    assert sympify('x==y')==Equal(Symbol('x'),Symbol('y'))
    assert sympify('x!=y')==Not(Equal(Symbol('x'),Symbol('y')))
    assert sympify('x<y')==Less(Symbol('x'),Symbol('y'))
    assert sympify('x>y')==Less(Symbol('y'),Symbol('x'))
    assert sympify('x<=y')==Or(Less(Symbol('x'),Symbol('y')),Equal(Symbol('x'), Symbol('y')))
    assert sympify('x>=y')==Or(Less(Symbol('y'),Symbol('x')),Equal(Symbol('x'), Symbol('y')))

    assert sympify('x<y<2')==And(Less(Symbol('x'),Symbol('y')),Less(Symbol('y'),2))

def test_is():
    assert sympify('x is x')==True
    assert sympify('x is not x')==False
    assert sympify('x is y')==False
    assert sympify('x is not y')==True

def test_contains():
    sympify('x in y')==Element(Symbol('x'),SetSymbol('y'))
    sympify('x not in y')==Not(Element(Symbol('x'),SetSymbol('y')))

def test_arith():
    assert sympify('+x')==Symbol('x')
    assert sympify('-x')==-Symbol('x')
    assert sympify('x + y')==Add(Symbol('x'),Symbol('y'))
    assert sympify('x - y')==Add(Symbol('x'),-Symbol('y'))
    assert sympify('x * y')==Mul(Symbol('x'),Symbol('y'))
    assert sympify('x / y')==Mul(Symbol('x'),1/Symbol('y'))
    assert sympify('x * 2')==Mul(Symbol('x'),2)
    assert sympify('x ** 2')==Mul(Symbol('x')**2)

def test_call():
    assert sympify('f(x)')==FunctionType('f')(Symbol('x'))
    assert sympify('not f(x)')==Not(Equal(FunctionType('f')(Symbol('x')),0))

    b = PredicateType('b')
    assert sympify('b(x)')==b('x')
    assert sympify('not b(x)')==Not(b('x'))
