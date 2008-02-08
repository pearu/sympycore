
from sympycore import *

P = PolynomialRing

def test_default_ring():
    r = repr(P(0))
    assert r=="PolynomialRing('0')"
    assert P.zero==P(0)
    assert str(0)=='0'
    assert `P(2)`=="PolynomialRing('2')"

def test_X():
    X = PolynomialRing['x']
    assert `X.zero`=="PolynomialRing[x, Calculus]('0')"
    assert `X.one`=="PolynomialRing[x, Calculus]('1')"
    assert str(X.zero)=='0'
    assert str(X.one)=='1'

    assert `X({2:3})`=="PolynomialRing[x, Calculus]('3*x**2')"
    assert `X({2:3,4:5})`=="PolynomialRing[x, Calculus]('5*x**4 + 3*x**2')"
    assert `X([(2,3)])`=="PolynomialRing[x, Calculus]('3*x**2')"
    assert `X([(2,3),(4,5)])`=="PolynomialRing[x, Calculus]('5*x**4 + 3*x**2')"

    assert str(X({2:3}))=="3*x**2"
    assert str(X([(2,3),(4,5)]))=="5*x**4 + 3*x**2"

    assert `X('x*3*x')`=="PolynomialRing[x, Calculus]('3*x**2')"
    assert `X('x**4+4*x**4-3*x*x+6*x**2')`=="PolynomialRing[x, Calculus]('5*x**4 + 3*x**2')"

    assert `X([1,2,3])`=="PolynomialRing[x, Calculus]('3*x**2 + 2*x + 1')"

def test_univariate():
    X = PolynomialRing['x']
    x = X([0,1])
    assert `x`=="PolynomialRing[x, Calculus]('x')"
    assert X([1, 2, 3]) == 3*x**2 + 2*x + 1
    assert X([1, 2, 3]).degree == 2
    assert X([1, 2, 3]).ldegree == 0
    assert X([0]).degree == 0
    assert X([0]).ldegree == 0
    assert (x**3 + x) + (3*x + x**4) == x**4 + x**3 + 4*x
    assert X([1, 2, 3])*2 == X([2, 4, 6])
    assert X([1, 2, 3])/2.0 == X([0.5, 1.0, 1.5])
    assert X([4,-3,5])(6) == 166
    assert X([1,2,3])(X([4,5,6])) == 108*x**4 + 180*x**3 + 231*x**2 + 130*x + 57
    assert (x-1)*(x+1) == x**2 - 1
    assert (x-1)*(x+1) / (x-1) == (x+1)
    assert (x**3 + x).diff() == 3*x**2 + 1
    assert str(X([3, 0, 1])) == 'x**2 + 3'
    assert str(X([0])) == '0'
    assert str(X([1, 1])) == 'x + 1'
    assert str((5 + 3*x) / 5) == '3/5*x + 1'
    assert str(X([4, 11, 6]) / X([6, 12])) == '1/2*x + 2/3'
    assert str(X([2, 3, 4]) % X([1, 2, 3])) == '1/3*x + 2/3'