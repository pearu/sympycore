
from sympycore import *

a,b,c = map(Symbol,'abc')

def test_as_term_coeff():
    assert (a*b).as_term_coeff()==(a*b,1)
    assert (2*a*b).as_term_coeff()==(a*b,2)
    assert (2+2*b).as_term_coeff()==(1+b,2)
    assert (4*a+2*b).as_term_coeff()==(2*a+b,2)
    assert (5*a/6+20*b/3).as_term_coeff()==(a/2+4*b,Fraction(5,3))


def test_as_term_coeff():
    assert (a*b).as_term_intcoeff()==(a*b,1)
    assert (2*a*b).as_term_intcoeff()==(a*b,2)
    assert (2+2*b).as_term_intcoeff()==(1+b,2)
    assert (4*a+2*b).as_term_intcoeff()==(2*a+b,2)
    assert (5*a/6+20*b/3).as_term_intcoeff()==(a/6+4*b/3,5)

    # 
    assert (4*a+2*b).as_term_intcoeff()==(2*a+b,2)
    assert (4*a-2*b).as_term_intcoeff()==(2*a-b,2)
    assert (-4*a+2*b).as_term_intcoeff()==(-2*a+b,2)
    assert (-4*a-2*b).as_term_intcoeff()==(2*a+b,-2)

    assert (2 + 4*a+2*b).as_term_intcoeff()==(1+2*a+b,2)
    assert (2 + 4*a-2*b).as_term_intcoeff()==(1+2*a-b,2)
    assert (2-4*a+2*b).as_term_intcoeff()==(1-2*a+b,2)
    assert (2-4*a-2*b).as_term_intcoeff()==(1-2*a-b,2)

    assert (-2 + 4*a+2*b).as_term_intcoeff()==(1-2*a-b,-2)
    assert (-2 + 4*a-2*b).as_term_intcoeff()==(1-2*a+b,-2)
    assert (-2-4*a+2*b).as_term_intcoeff()==(1+2*a-b,-2)
    assert (-2-4*a-2*b).as_term_intcoeff()==(1+2*a+b,-2)
