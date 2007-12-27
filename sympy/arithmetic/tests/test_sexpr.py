# should be moved to sympy/arithmetic/tests.

from sympy import *
from sympy.arithmetic import sexpr

def test_tostr():
    x = (sexpr.SYMBOLIC, 'x')
    y = (sexpr.SYMBOLIC, 'y')
    n = (sexpr.NUMBER, 3)
    r = (sexpr.NUMBER, Fraction(2,3))
    assert sexpr.tostr(x)=='x'
    assert sexpr.tostr(n)=='3'
    assert sexpr.tostr(r)=='2/3'
    assert sexpr.tostr(sexpr.add(x,x))=='2*x'
    assert sexpr.tostr(sexpr.add(x,y))=='1*x + 1*y'
    assert sexpr.tostr(sexpr.mul(x,x))=='x**2'
    assert sexpr.tostr(sexpr.mul(x,y))=='x**1 * y**1'
    assert sexpr.tostr(sexpr.power(x,2))=='x**2'
    assert sexpr.tostr(sexpr.add(x,r))=='2/3*1 + 1*x'
    assert sexpr.tostr(sexpr.add(r,r))=='4/3'

def test_add():
    x = (sexpr.SYMBOLIC, 'x')
    y = (sexpr.SYMBOLIC, 'y')
    assert sexpr.add(x,y)==(sexpr.TERMS,frozenset([(x,1),(y,1)]))
    assert sexpr.add(x,x)==(sexpr.TERMS,frozenset([(x,2)]))
    assert sexpr.add(x,sexpr.add(x,y))==(sexpr.TERMS,frozenset([(x,2),(y,1)]))
    assert sexpr.add(sexpr.add(x,y),x)==(sexpr.TERMS,frozenset([(x,2),(y,1)]))
    assert sexpr.add(sexpr.add(x,y),sexpr.add(x,y))==(sexpr.TERMS,frozenset([(x,2),(y,2)]))

def test_mul():
    x = (sexpr.SYMBOLIC, 'x')
    y = (sexpr.SYMBOLIC, 'y')
    assert sexpr.mul(x,y)==(sexpr.FACTORS,frozenset([(x,1),(y,1)]))
    assert sexpr.mul(x,x)==(sexpr.FACTORS,frozenset([(x,2)]))
    assert sexpr.mul(x,sexpr.mul(x,y))==(sexpr.FACTORS,frozenset([(x,2),(y,1)]))
    assert sexpr.mul(sexpr.mul(x,y),x)==(sexpr.FACTORS,frozenset([(x,2),(y,1)]))
    assert sexpr.mul(sexpr.mul(x,y),sexpr.mul(x,y))==(sexpr.FACTORS,frozenset([(x,2),(y,2)]))

def test_power():
    x = (sexpr.SYMBOLIC, 'x')
    y = (sexpr.SYMBOLIC, 'y')
    n = (sexpr.NUMBER, Integer(3))
    r = (sexpr.NUMBER, Fraction(2,3))
    assert sexpr.power(x, 2)==(sexpr.FACTORS,frozenset([(x,2)]))
    assert sexpr.power(x, -1)==(sexpr.FACTORS,frozenset([(x,-1)]))
    assert sexpr.power(n, 2)==(sexpr.NUMBER, 9)
    assert sexpr.power(n, -2)==(sexpr.NUMBER, Fraction(1,9))
    assert sexpr.power(r, 2)==(sexpr.NUMBER, Fraction(4,9))
    assert sexpr.power(r, -2)==(sexpr.NUMBER, Fraction(9,4))
    assert sexpr.power(sexpr.add(x,x), 2)==sexpr.mul(sexpr.power((sexpr.NUMBER,2),2),sexpr.power(x,2))

def test_expand_mul():
    x = (sexpr.SYMBOLIC, 'x')
    y = (sexpr.SYMBOLIC, 'y')
    x2 = sexpr.mul(x,x)
    xy = sexpr.mul(x,y)
    assert sexpr.expand_mul(sexpr.add(x,y),x)==sexpr.add(x2, xy)
