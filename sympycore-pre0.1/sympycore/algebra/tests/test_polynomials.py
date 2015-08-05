from sympycore.algebra.polynomials import *

def test_polynomials():
    x = poly([0, 1])
    assert poly([1, 2, 3]) == 3*x**2 + 2*x + 1
    assert poly([1, 2, 3]).degree == 2
    assert poly([1, 2, 3, 0]).degree == 2
    assert poly([0]).degree == -1
    assert (x**3 + x) + (3*x + x**4) == x**4 + x**3 + 4*x
    assert poly([1, 2, 3])*2 == poly([2, 4, 6])
    assert poly([1, 2, 3])/2.0 == poly([0.5, 1.0, 1.5])
    assert poly([4,-3,5])(6) == 166
    assert poly([1,2,3])(poly([4,5,6])) == 108*x**4 + 180*x**3 + 231*x**2 + 130*x + 57
    assert (x-1)*(x+1) == x**2 - 1
    assert (x-1)*(x+1) / (x-1) == (x+1)
    assert (x**3 + x).diff() == 3*x**2 + 1
    assert str(poly([3, 0, 1])) == '3 + x**2'
    assert str(poly([0])) == '0'
    assert str(poly([1, 1])) == '1 + x'