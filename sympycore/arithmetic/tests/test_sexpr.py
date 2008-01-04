# should be moved to sympy/arithmetic/tests.

from sympycore import *
from sympycore.core.sexpr import *
from sympycore.arithmetic.sexpr import *
from sympycore.arithmetic.sexpr import expand_mul, s_one, s_zero

def test_s_tostr():
    x = (SYMBOLIC, 'x')
    y = (SYMBOLIC, 'y')
    n = (NUMBER, 3)
    r = (NUMBER, Fraction(2,3))
    q = (NUMBER, Fraction(-5,6))
    assert s_tostr(x)=='x'
    assert s_tostr(n)=='3'
    assert s_tostr(r)=='2/3'
    assert s_tostr(q)=='-5/6'
    assert s_tostr(s_add(x,x))=='2*x'
    assert s_tostr(s_add(x,y))=='1*x + 1*y'
    assert s_tostr(s_add(x,r))=='1*x + 2/3*1'
    assert s_tostr(s_add(r,r))=='4/3'
    assert s_tostr(s_add(x,q))=='-5/6*1 + 1*x'
    assert s_tostr(s_mul(x,x))=='x**2'
    assert s_tostr(s_mul(x,y))=='x**1 * y**1'
    assert s_tostr(s_mul(x,n))=='3*x'
    assert s_tostr(s_mul(x,r))=='2/3*x'
    assert s_tostr(s_mul(x,q))=='-5/6*x'
    assert s_tostr(s_mul(r,r))=='4/9'
    assert s_tostr(s_power(x,2))=='x**2'
    assert s_tostr(s_power(s_add(x,y),2))=='(1*x + 1*y)**2'
    assert s_tostr(s_power(s_mul(x,y),2))=='x**2 * y**2'
    assert s_tostr(s_power(q,2))=='25/36'

def test_s_add():
    x = (SYMBOLIC, 'x')
    y = (SYMBOLIC, 'y')
    n = (NUMBER, -one)
    t = (NUMBER, sympify(2))
    assert s_add(x,s_zero)==x
    assert s_add(x,y)==(TERMS,frozenset([(x,one),(y,one)]), zero)
    assert s_add(x,x)==(TERMS,frozenset([(x,2)]), zero)
    assert s_add(x,s_add(x,y))==(TERMS,frozenset([(x,2),(y,one)]), zero)
    assert s_add(s_add(x,y),x)==s_add(x,s_add(x,y))
    assert s_add(s_add(x,y),s_add(x,y))==\
           (TERMS,frozenset([(x,2),(y,2)]),zero)
    assert s_add(x,s_mul(n,x))==s_zero
    assert s_add(n,s_add(x,y))==\
           (TERMS, frozenset([(x,one),(y,one),(s_one,-one)]), -one)
    assert s_add(s_add(x,y), n)==s_add(n,s_add(x,y))
    assert s_add(x,n)==(TERMS,frozenset([(x,one),(s_one,-one)]), -one)
    assert s_add(n,x)==s_add(x,n)
    assert s_add(s_add(n,x),s_one)==x
    assert s_add(s_add(n,x),s_mul(n,x))==n
    assert s_tostr(s_add(s_add(n,x),s_add(t,s_mul(n,y))))=='-1*y + 1*1 + 1*x'

def test_s_mul():
    x = (SYMBOLIC, 'x')
    y = (SYMBOLIC, 'y')
    z = (SYMBOLIC, 'z')
    n = (NUMBER, 3)
    assert s_mul(x,s_zero)==s_zero
    assert s_mul(s_zero,x)==s_zero
    assert s_mul(x,s_one)==x
    assert s_mul(s_one,x)==x
    assert s_mul(x,y)==(FACTORS,frozenset([(x,one),(y,one)]),one)
    assert s_mul(x,x)==(FACTORS,frozenset([(x,2)]),one)
    assert s_mul(x,s_mul(x,y))==(FACTORS,frozenset([(x,2),(y,one)]),one)
    assert s_mul(s_mul(x,y),x)==(FACTORS,frozenset([(x,2),(y,one)]),one)
    assert s_mul(s_mul(x,y),s_mul(x,y))==(FACTORS,
                                    frozenset([(x,2),(y,2)]),one)
    assert s_mul(x, s_power(x,-one))==s_one
    assert s_mul(n,s_mul(x,y))==\
           (TERMS,frozenset([(s_mul(x,y),n[1])]), zero)
    assert s_mul(n,s_mul(x,y))==s_mul(s_mul(x,y),n)
    assert s_mul(s_mul(x,z),s_mul(x,y))==\
           (FACTORS,frozenset([(x,2),(y,one),(z,one)]), one)
    t = (NUMBER, 2)
    xy = s_mul(x,y)
    xy2 = s_mul(xy,t)
    assert xy2==(TERMS, frozenset([(xy,2)]), zero)
    assert s_tostr(xy2)=='2*x**1 * y**1'

    assert s_mul(s_power(x,2),s_power(x,-one))==x
    assert s_tostr(s_mul(s_add(x,y), x))=='(1*x + 1*y)**1 * x**1'
    assert s_mul(s_add(x,y), x)==s_mul(x,s_add(x,y))
    assert s_tostr(s_mul(s_add(x,y), s_add(x,y)))=='(1*x + 1*y)**2'
    assert s_tostr(s_mul(s_add(x,y), n))=='3*x + 3*y'
    assert s_mul(s_add(x,y), n)==s_mul(n,s_add(x,y))
    assert s_tostr(s_mul(s_add(x,y), s_add(x,n)))=='(1*x + 1*y)**1 * (1*x + 3*1)**1'
    assert s_tostr(s_mul(s_add(x,y), s_power(x,2)))=='(1*x + 1*y)**1 * x**2'
    assert s_mul(s_add(x,y), s_power(x,2))==s_mul(s_power(x,2),s_add(x,y))
    assert s_tostr(s_mul(s_mul(n,x), x))=='3*x**2'
    assert s_tostr(s_mul(s_mul(n,x), s_mul(t,y)))=='6*x**1 * y**1'
    assert s_tostr(s_mul(s_mul(n,x), s_power(x,3)))=='3*x**4'

def test_s_power():
    x = (SYMBOLIC, 'x')
    y = (SYMBOLIC, 'y')
    n = (NUMBER, Integer(3))
    r = (NUMBER, Fraction(2,3))
    assert s_power(x, 2)==(FACTORS,frozenset([(x,2)]), one)
    assert s_power(x, -one)==(FACTORS,frozenset([(x,-one)]), one)
    assert s_power(n, 2)==(NUMBER, 9)
    assert s_power(n, -2)==(NUMBER, Fraction(1,9))
    assert s_power(r, 2)==(NUMBER, Fraction(4,9))
    assert s_power(r, -2)==(NUMBER, Fraction(9,4))
    assert s_power(s_add(x,x), 2)==s_mul(s_power((NUMBER,2),2),s_power(x,2))
    assert s_power(s_add(x,y), one)==s_add(x,y)
    assert s_power(s_add(x,y), zero)==s_one
    assert s_power(s_zero, zero)==s_one
    assert s_power(s_mul(x,n),2)==s_mul(s_power(x,2),s_power(n,2))
    print s_tostr(s_power(s_mul(x,(NUMBER,-one)),2))
    assert s_power(s_mul(x,(NUMBER,-one)),2)==s_power(x,2)

def test_expand_mul():
    x = (SYMBOLIC, 'x')
    y = (SYMBOLIC, 'y')
    t = (NUMBER, 2)
    x2 = s_mul(x,x)
    y2 = s_mul(y,y)

    xy = s_mul(x,y)
    xy2 = s_mul(t,xy)
    assert expand_mul(s_add(x,y),x)==s_add(x2, xy)
    assert expand_mul(y,s_add(x,y))==s_add(y2, xy)
    assert expand_mul(s_add(x,y),s_add(x,y))==\
           s_add(xy2, s_add(x2, y2))
    assert expand_mul(x,y)==xy

    assert expand_mul(s_add(x,y),s_mul(y,x))==\
           s_add(s_mul(y2,x), s_mul(x2,y))
    assert expand_mul(s_add(x,y),s_mul(y,x))==\
           expand_mul(s_mul(x,y),s_add(y,x))

    assert expand_mul(s_add(x,s_mul(y,x)),y)==\
           s_add(xy,s_mul(xy,y))
    assert s_tostr(expand_mul(s_add(x,y),s_add(x,t)))==\
          '1*x**1 * y**1 + 1*x**2 + 2*x + 2*y'
    assert s_tostr(expand_mul(s_add(x,y),t))==\
          '2*x + 2*y'
    assert s_tostr(expand_mul(s_add(x,y),s_power(x,-one)))==\
          '1*1 + 1*x**-1 * y**1'
    assert s_tostr(s_power(s_mul(x,s_add(x,y)),-2))=='(1*x + 1*y)**-2 * x**-2'
    assert s_tostr(s_power(s_add(t,s_mul(x,s_add(x,y))),-2))=='(1*(1*x + 1*y)**1 * x**1 + 2*1)**-2'
    
def test_s_expand():
    x = (SYMBOLIC, 'x')
    y = (SYMBOLIC, 'y')
    z = (SYMBOLIC, 'z')
    t = (NUMBER, 2)
    assert s_tostr(s_expand(s_mul(s_add(x,y),z)))==\
           '1*x**1 * z**1 + 1*y**1 * z**1'
    assert s_tostr(s_expand(s_power(s_add(x,y),2)))==\
           '1*x**2 + 1*y**2 + 2*x**1 * y**1'
    assert s_tostr(s_expand(s_power(s_add(t,s_mul(x,s_add(x,y))),-2)))=='(1*x**1 * y**1 + 1*x**2 + 2*1)**-2'
    assert s_tostr(s_expand(s_mul(s_add(x,y), s_add(x,s_mul(y,(NUMBER,-one))))))=='-1*y**2 + 1*x**2'

def test_sequence():
    x = (SYMBOLIC, 'x')
    y = (SYMBOLIC, 'y')
    t = (NUMBER, sympify(2))
    nt = (NUMBER, -sympify(2))
    assert s_add_sequence([])==s_zero
    assert s_add_sequence([x])==x
    assert s_add_sequence([x,s_zero])==x
    assert s_add_sequence([x,y])==s_add(x,y)
    assert s_add_sequence([x,s_add(s_mul(t,x),y)])==s_add(x,s_add(s_mul(t,x),y))
    assert s_add_sequence([s_add(s_mul(t,x),y),s_add(s_mul(nt,x),y)])==s_mul(t,y)
    
    assert s_mul_sequence([])==s_one
    assert s_mul_sequence([x])==x
    assert s_mul_sequence([x,s_one])==x
    assert s_mul_sequence([x,s_zero])==s_zero
    assert s_mul_sequence([x,y])==s_mul(x,y)
    assert s_mul_sequence([x,s_add(t,x)])==s_mul(x,s_add(t,x))
    assert s_mul_sequence([x,t])==s_mul(x,t)
    assert s_mul_sequence([x,s_mul(y,x)])==s_mul(s_power(x,2),y)
    assert s_mul_sequence([x,s_mul(t,x)])==s_mul(s_power(x,2),t)
    assert s_mul_sequence([x,s_mul(t,y)])==s_mul(s_mul(x,y),t)

def test_naninf():
    x = (SYMBOLIC, 'x')
    y = (SYMBOLIC, 'y')
    t = (NUMBER, sympify(2))
    f = (NUMBER, sympify(-4))
    s_inf = oo.as_sexpr()
    s_nan = nan.as_sexpr()
    s_minf = moo.as_sexpr()

    assert s_add(t,s_inf)==s_inf
    assert s_add(t,s_minf)==s_minf
    assert s_add(t,s_nan)==s_nan
    assert s_add(s_inf,t)==s_inf
    assert s_add(s_minf,t)==s_minf
    assert s_add(s_nan,t)==s_nan

    assert s_add(s_minf, s_minf)==s_minf
    assert s_add(s_minf, s_inf)==s_nan
    assert s_add(s_inf, s_minf)==s_nan
    assert s_add(s_inf, s_inf)==s_inf

    assert s_add(s_inf, s_nan)==s_nan
    assert s_add(s_nan, s_nan)==s_nan
    assert s_add(s_minf, s_nan)==s_nan
    assert s_add(s_nan, s_inf)==s_nan
    assert s_add(s_nan, s_minf)==s_nan

    assert s_mul(t,s_inf)==s_inf
    assert s_mul(s_inf,t)==s_inf
    assert s_mul(t,s_minf)==s_minf
    assert s_mul(s_minf,t)==s_minf
    assert s_mul(s_nan,t)==s_nan

    assert s_mul(f,s_inf)==s_minf
    assert s_mul(s_inf,f)==s_minf
    assert s_mul(f,s_minf)==s_inf
    assert s_mul(s_minf,f)==s_inf
    assert s_mul(s_nan,f)==s_nan
    assert s_mul(f,s_nan)==s_nan

    assert s_mul(s_zero,s_inf)==s_nan
    assert s_mul(s_zero,s_minf)==s_nan
    assert s_mul(s_zero,s_nan)==s_nan
    assert s_mul(s_nan,s_zero)==s_nan
    assert s_mul(s_inf,s_zero)==s_nan
    assert s_mul(s_minf,s_zero)==s_nan

    assert s_mul(s_minf,s_minf)==s_inf
    assert s_mul(s_inf, s_minf)==s_minf
    assert s_mul(s_minf,s_inf)==s_minf
    assert s_mul(s_inf,s_inf)==s_inf
    
    assert s_add_sequence([t,s_inf])==s_inf
    assert s_add_sequence([t,s_minf])==s_minf
    assert s_add_sequence([t,s_nan])==s_nan
    assert s_add_sequence([s_inf,t])==s_inf
    assert s_add_sequence([s_minf,t])==s_minf
    assert s_add_sequence([s_nan,t])==s_nan

    assert s_add_sequence([s_minf, s_minf])==s_minf
    assert s_add_sequence([s_minf, s_inf])==s_nan
    assert s_add_sequence([s_inf, s_minf])==s_nan
    assert s_add_sequence([s_inf, s_inf])==s_inf

    assert s_add_sequence([s_inf, s_nan])==s_nan
    assert s_add_sequence([s_nan, s_nan])==s_nan
    assert s_add_sequence([s_minf, s_nan])==s_nan
    assert s_add_sequence([s_nan, s_inf])==s_nan
    assert s_add_sequence([s_nan, s_minf])==s_nan

    assert s_mul_sequence([t,s_inf])==s_inf
    assert s_mul_sequence([s_inf,t])==s_inf
    assert s_mul_sequence([t,s_minf])==s_minf
    assert s_mul_sequence([s_minf,t])==s_minf
    assert s_mul_sequence([s_nan,t])==s_nan

    assert s_mul_sequence([f,s_inf])==s_minf
    assert s_mul_sequence([s_inf,f])==s_minf
    assert s_mul_sequence([f,s_minf])==s_inf
    assert s_mul_sequence([s_minf,f])==s_inf
    assert s_mul_sequence([s_nan,f])==s_nan
    assert s_mul_sequence([f,s_nan])==s_nan

    assert s_mul_sequence([s_zero,s_inf])==s_nan
    assert s_mul_sequence([s_zero,s_minf])==s_nan
    assert s_mul_sequence([s_zero,s_nan])==s_nan
    assert s_mul_sequence([s_nan,s_zero])==s_nan
    assert s_mul_sequence([s_inf,s_zero])==s_nan
    assert s_mul_sequence([s_minf,s_zero])==s_nan

    assert s_mul_sequence([s_minf,s_minf])==s_inf
    assert s_mul_sequence([s_inf, s_minf])==s_minf
    assert s_mul_sequence([s_minf,s_inf])==s_minf
    assert s_mul_sequence([s_inf,s_inf])==s_inf
