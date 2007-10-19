
from sympy import Symbol, sympify, Fraction, sin, Function, pi

def test_parser():
    x = Symbol('x')
    f = Function('f')
    assert sympify('x')==x
    assert sympify('x+1')==1+x
    assert sympify('x*2')==2*x
    assert sympify('x**(3/2)')==x**Fraction(3,2)
    assert sympify('1/2')==Fraction(1,2)
    assert sympify('5/15')==Fraction(1,3)
    assert sympify('x*2')==2*x
    assert sympify('sin(x)')==sin(x)
    assert sympify('pi')==pi
    assert sympify('f(x)')==f(x)
    assert sympify('sin(x)+1')==sin(x)+1
    assert sympify('f(x)+1')==f(x)+1
    assert sympify('f(x)+sin(x)')==f(x)+sin(x)
    
if __name__ == '__main__':
    test_parser()
