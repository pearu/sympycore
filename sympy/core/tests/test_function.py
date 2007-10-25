from sympy import Symbol, Lambda

def test_lambda():
    x = Symbol('x')
    y = Symbol('y')
    assert Lambda(x, x**2)(3) == 9
    assert Lambda((x, y), x + 2*y)(3, 1) == 5
    # verify that bound and unbound variables don't get mixed up on evaluation
    assert Lambda((x, y), x*y)(y, x) == x*y
    assert Lambda((x, y), x*y)(x, y) == x*y
