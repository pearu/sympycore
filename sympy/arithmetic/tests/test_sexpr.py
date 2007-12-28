# should be moved to sympy/arithmetic/tests.

from sympy import *
from sympy.core.sexpr import *
from sympy.arithmetic.sexpr import *
from sympy.arithmetic.sexpr import expand_mul, one, zero

def test_tostr():
    x = (SYMBOLIC, 'x')
    y = (SYMBOLIC, 'y')
    n = (NUMBER, 3)
    r = (NUMBER, Fraction(2,3))
    q = (NUMBER, Fraction(-5,6))
    assert tostr(x)=='x'
    assert tostr(n)=='3'
    assert tostr(r)=='2/3'
    assert tostr(q)=='-5/6'
    assert tostr(add(x,x))=='2*x'
    assert tostr(add(x,y))=='1*x + 1*y'
    assert tostr(add(x,r))=='1*x + 2/3*1'
    assert tostr(add(r,r))=='4/3'
    assert tostr(add(x,q))=='-5/6*1 + 1*x'
    assert tostr(mul(x,x))=='x**2'
    assert tostr(mul(x,y))=='x**1 * y**1'
    assert tostr(mul(x,n))=='3*x'
    assert tostr(mul(x,r))=='2/3*x'
    assert tostr(mul(x,q))=='-5/6*x'
    assert tostr(mul(r,r))=='4/9'
    assert tostr(power(x,2))=='x**2'
    assert tostr(power(add(x,y),2))=='(1*x + 1*y)**2'
    assert tostr(power(mul(x,y),2))=='x**2 * y**2'
    assert tostr(power(q,2))=='25/36'

def test_add():
    x = (SYMBOLIC, 'x')
    y = (SYMBOLIC, 'y')
    n = (NUMBER, -1)
    t = (NUMBER, 2)
    assert add(x,y)==(TERMS,frozenset([(x,1),(y,1)]))
    assert add(x,x)==(TERMS,frozenset([(x,2)]))
    assert add(x,add(x,y))==(TERMS,frozenset([(x,2),(y,1)]))
    assert add(add(x,y),x)==add(x,add(x,y))
    assert add(add(x,y),add(x,y))==\
           (TERMS,frozenset([(x,2),(y,2)]))
    assert add(x,mul(n,x))==zero
    assert add(n,add(x,y))==\
           (TERMS, frozenset([(x,1),(y,1),(one,-1)]))
    assert add(add(x,y), n)==add(n,add(x,y))
    assert add(x,n)==(TERMS,frozenset([(x,1),(one,-1)]))
    assert add(n,x)==add(x,n)
    assert add(add(n,x),one)==x
    assert add(add(n,x),mul(n,x))==n
    assert tostr(add(add(n,x),add(t,mul(n,y))))=='-1*y + 1*1 + 1*x'

def test_mul():
    x = (SYMBOLIC, 'x')
    y = (SYMBOLIC, 'y')
    z = (SYMBOLIC, 'z')
    n = (NUMBER, 3)
    assert mul(x,y)==(FACTORS,frozenset([(x,1),(y,1)]))
    assert mul(x,x)==(FACTORS,frozenset([(x,2)]))
    assert mul(x,mul(x,y))==(FACTORS,frozenset([(x,2),(y,1)]))
    assert mul(mul(x,y),x)==(FACTORS,frozenset([(x,2),(y,1)]))
    assert mul(mul(x,y),mul(x,y))==(FACTORS,
                                    frozenset([(x,2),(y,2)]))
    assert mul(x, power(x,-1))==one
    assert mul(n,mul(x,y))==\
           (TERMS,frozenset([(mul(x,y),n[1])]))
    assert mul(n,mul(x,y))==mul(mul(x,y),n)
    assert mul(mul(x,z),mul(x,y))==\
           (FACTORS,frozenset([(x,2),(y,1),(z,1)]))
    t = (NUMBER, 2)
    xy = mul(x,y)
    xy2 = mul(xy,t)
    assert xy2==(TERMS, frozenset([(xy,2)]))
    assert tostr(xy2)=='2*x**1 * y**1'

    assert mul(power(x,2),power(x,-1))==x
    assert tostr(mul(add(x,y), x))=='(1*x + 1*y)**1 * x**1'
    assert mul(add(x,y), x)==mul(x,add(x,y))
    assert tostr(mul(add(x,y), add(x,y)))=='(1*x + 1*y)**2'
    assert tostr(mul(add(x,y), n))=='3*x + 3*y'
    assert mul(add(x,y), n)==mul(n,add(x,y))
    assert tostr(mul(add(x,y), add(x,n)))=='(1*x + 1*y)**1 * (1*x + 3*1)**1'
    assert tostr(mul(add(x,y), power(x,2)))=='(1*x + 1*y)**1 * x**2'
    assert mul(add(x,y), power(x,2))==mul(power(x,2),add(x,y))
    assert tostr(mul(mul(n,x), x))=='3*x**2'
    assert tostr(mul(mul(n,x), mul(t,y)))=='6*x**1 * y**1'
    assert tostr(mul(mul(n,x), power(x,3)))=='3*x**4'

def test_power():
    x = (SYMBOLIC, 'x')
    y = (SYMBOLIC, 'y')
    n = (NUMBER, Integer(3))
    r = (NUMBER, Fraction(2,3))
    assert power(x, 2)==(FACTORS,frozenset([(x,2)]))
    assert power(x, -1)==(FACTORS,frozenset([(x,-1)]))
    assert power(n, 2)==(NUMBER, 9)
    assert power(n, -2)==(NUMBER, Fraction(1,9))
    assert power(r, 2)==(NUMBER, Fraction(4,9))
    assert power(r, -2)==(NUMBER, Fraction(9,4))
    assert power(add(x,x), 2)==mul(power((NUMBER,2),2),power(x,2))
    assert power(add(x,y), 1)==add(x,y)
    assert power(add(x,y), 0)==one
    assert power(zero, 0)==one

def test_expand_mul():
    x = (SYMBOLIC, 'x')
    y = (SYMBOLIC, 'y')
    t = (NUMBER, 2)
    x2 = mul(x,x)
    y2 = mul(y,y)

    xy = mul(x,y)
    xy2 = mul(t,xy)
    assert expand_mul(add(x,y),x)==add(x2, xy)
    assert expand_mul(y,add(x,y))==add(y2, xy)
    assert expand_mul(add(x,y),add(x,y))==\
           add(xy2, add(x2, y2))
    assert expand_mul(x,y)==xy

    assert expand_mul(add(x,y),mul(y,x))==\
           add(mul(y2,x), mul(x2,y))
    assert expand_mul(add(x,y),mul(y,x))==\
           expand_mul(mul(x,y),add(y,x))

    assert expand_mul(add(x,mul(y,x)),y)==\
           add(xy,mul(xy,y))
    assert tostr(expand_mul(add(x,y),add(x,t)))==\
          '1*x**1 * y**1 + 1*x**2 + 2*x + 2*y'
    assert tostr(expand_mul(add(x,y),t))==\
          '2*x + 2*y'
    assert tostr(expand_mul(add(x,y),power(x,-1)))==\
          '1*1 + 1*x**-1 * y**1'
    assert tostr(power(mul(x,add(x,y)),-2))=='(1*x + 1*y)**-2 * x**-2'
    assert tostr(power(add(t,mul(x,add(x,y))),-2))=='(1*(1*x + 1*y)**1 * x**1 + 2*1)**-2'
    
def test_expand():
    x = (SYMBOLIC, 'x')
    y = (SYMBOLIC, 'y')
    z = (SYMBOLIC, 'z')
    t = (NUMBER, 2)
    assert tostr(expand(mul(add(x,y),z)))==\
           '1*x**1 * z**1 + 1*y**1 * z**1'
    assert tostr(expand(power(add(x,y),2)))==\
           '1*x**2 + 1*y**2 + 2*x**1 * y**1'
    assert tostr(expand(power(add(t,mul(x,add(x,y))),-2)))=='(1*x**1 * y**1 + 1*x**2 + 2*1)**-2'
    assert tostr(expand(mul(add(x,y), add(x,mul(y,(NUMBER,-1))))))=='-1*y**2 + 1*x**2'

def test_sequence():
    x = (SYMBOLIC, 'x')
    y = (SYMBOLIC, 'y')
    t = (NUMBER, 2)
    nt = (NUMBER, -2)
    assert add_sequence([])==zero
    assert add_sequence([x])==x
    assert add_sequence([x,y])==add(x,y)
    assert add_sequence([x,add(mul(t,x),y)])==add(x,add(mul(t,x),y))
    assert add_sequence([add(mul(t,x),y),add(mul(nt,x),y)])==mul(t,y)
    
    assert mul_sequence([])==one
    assert mul_sequence([x])==x
    assert mul_sequence([x,y])==mul(x,y)
    assert mul_sequence([x,add(t,x)])==mul(x,add(t,x))
    assert mul_sequence([x,t])==mul(x,t)
    assert mul_sequence([x,mul(y,x)])==mul(power(x,2),y)
    assert mul_sequence([x,mul(t,x)])==mul(power(x,2),t)
    assert mul_sequence([x,mul(t,y)])==mul(mul(x,y),t)
