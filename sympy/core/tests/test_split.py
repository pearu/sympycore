from sympy import *

x = Symbol('x')
y = Symbol('y')

def test_split_add():
    assert list((x).split(Add)[1]) == [x]
    assert sorted((3+x).split(Add)[1]) == sorted([3, x])
    assert sorted((3+x+y).split(Add)[1]) == sorted([3, x, y])
    assert sorted((1+4*x+y).split(Add)[1]) == sorted([1, 4*x, y])
    assert list((3*x).split(Add)[1]) == [3*x]
    assert list((3*x*y).split(Add)[1]) == [3*x*y]

def test_split_mul():
    assert list((x).split(Mul)[1]) == [x]
    assert list((3+x).split(Mul)[1]) == [3+x]
    assert sorted((3*x).split(Mul)[1]) == sorted([3, x])
    assert sorted((3*x*y).split(Mul)[1]) == sorted([3, x, y])
    assert sorted((3*x**2*y).split(Mul)[1]) == sorted([3, x**2, y])

def test_split_pow():
    assert list((x).split(Pow)[1]) == [x]
    assert list((3+x).split(Pow)[1]) == [3+x]
    assert list((3*x).split(Pow)[1]) == [3*x]
    assert list((x**4).split(Pow)[1]) == [x, 4]
