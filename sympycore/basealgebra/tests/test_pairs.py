
from sympycore import CommutativeRingWithPairs as Algebra

Symbol = Algebra.Symbol
Number = Algebra.Number
Add = Algebra.Add
Mul = Algebra.Mul
Pow = Algebra.Pow
Terms = Algebra.Terms
Factors = Algebra.Factors

def test_symbol():
    a = Symbol('a')
    assert str(a)=='a'

def test_number():
    n = Number(2)
    assert str(n)=='2'

def test_add():
    a = Symbol('a')
    n = Number(2)
    s = Add(n,a)
    assert str(s)=='2 + a'

def test_mul():
    a = Symbol('a')
    n = Number(2)
    s = Mul(n,a)
    assert str(s)=='2*a'

def test_pow():
    a = Symbol('a')
    n = Number(2)
    s = Pow(a,3)
    assert str(s)=='a**3'

def test_terms():
    a = Symbol('a')
    n = Number(2)
    s = Terms((a,2))
    assert str(s)=='2*a'

def test_factors():
    a = Symbol('a')
    n = Number(2)
    s = Factors((a,2))
    assert str(s)=='a**2'

def test_new():
    a = Algebra('a')
    assert str(a)=='a'
    assert isinstance(a, Algebra)==True
    assert (a is Algebra(a))==True

def test_copy():
    a = Symbol('a')
    assert (a.copy() is a)==True

def test_func_args():
    a = Symbol('a')
    b = Symbol('b')
    n = Number(2)
    s = a + n
    s1 = 2*a
    m = a ** 2
    m2 = a*b
    assert a.func(*a.args)==a
    assert n.func(*n.args)==n
    assert s.func(*s.args)==s
    assert s1.func(*s1.args)==s1
    assert m.func(*m.args)==m
    assert m2.func(*m2.args)==m2
    
def test_Add_args():
    a = Symbol('a')
    b = Symbol('b')
    n = Number(2)
    s = a + n
    s1 = 2*a
    m = a ** 2
    m2 = a*b

    assert Add(*a.as_Add_args())==a
    assert Add(*n.as_Add_args())==n
    assert Add(*s.as_Add_args())==s
    assert Add(*s1.as_Add_args())==s1
    assert Add(*m.as_Add_args())==m
    assert Add(*m2.as_Add_args())==m2

def test_Mul_args():
    a = Symbol('a')
    b = Symbol('b')
    n = Number(2)
    s = a + n
    s1 = 2*a
    m = a ** 2
    m2 = a*b

    assert Mul(*a.as_Mul_args())==a
    assert Mul(*n.as_Mul_args())==n
    assert Mul(*s.as_Mul_args())==s
    assert Mul(*s1.as_Mul_args())==s1
    assert Mul(*m.as_Mul_args())==m
    assert Mul(*m2.as_Mul_args())==m2

def test_Pow_args():
    a = Symbol('a')
    b = Symbol('b')
    n = Number(2)
    s = a + n
    s1 = 2*a
    m = a ** 2
    m2 = a*b

    assert Pow(*a.as_Pow_args())==a
    assert Pow(*n.as_Pow_args())==n
    assert Pow(*s.as_Pow_args())==s
    assert Pow(*s1.as_Pow_args())==s1
    assert Pow(*m.as_Pow_args())==m
    assert Pow(*m2.as_Pow_args())==m2

def test_Terms_args():
    a = Symbol('a')
    b = Symbol('b')
    n = Number(2)
    s = a + n
    s1 = 2*a
    m = a ** 2
    m2 = a*b

    assert Terms(*a.as_Terms_args())==a
    assert Terms(*n.as_Terms_args())==n
    assert Terms(*s.as_Terms_args())==s
    assert Terms(*s1.as_Terms_args())==s1
    assert Terms(*m.as_Terms_args())==m
    assert Terms(*m2.as_Terms_args())==m2

def test_Factors_args():
    a = Symbol('a')
    b = Symbol('b')
    n = Number(2)
    s = a + n
    s1 = 2*a
    m = a ** 2
    m2 = a*b

    assert Factors(*a.as_Factors_args())==a
    assert Factors(*n.as_Factors_args())==n
    assert Factors(*s.as_Factors_args())==s
    assert Factors(*s1.as_Factors_args())==s1
    assert Factors(*m.as_Factors_args())==m
    assert Factors(*m2.as_Factors_args())==m2

def test_as_primitive():
    a = Symbol('a')
    b = Symbol('b')
    n = Number(2)
    t = Number(-3)
    s = a + n
    s1 = 2*a
    m = a ** 2
    m2 = a*b

    assert str(a.as_primitive())=='a'
    assert str(n.as_primitive())=='2'
    assert str(t.as_primitive())=='-3'
    assert str(s.as_primitive())=='2 + a'
    assert str(s1.as_primitive())=='2*a'
    assert str(m.as_primitive())=='a**2'
    assert str(m2.as_primitive())=='a*b'

def test_Mul():
    a = Symbol('a')
    b = Symbol('b')
    n = Number(2)
    assert Mul(a,a**-1)==1
    assert Mul(n,n**-1)==1

def test_number_add():
    n = Number(3)
    a = Symbol('a')
    b = Symbol('b')
    s = 2 + a
    s1 = 2*a
    m = a*b
    m1 = a**2
    assert n+2==5
    assert n-1==2
    assert n+n==6
    assert str(n+a)==str('3 + a')
    assert str(n+s)==str('5 + a')
    assert str(n+s1)==str('3 + 2*a')
    assert str(n+m)==str('3 + a*b')
    assert str(n+m1)==str('3 + a**2')

def test_number_mul():
    n = Number(3)
    a = Symbol('a')
    b = Symbol('b')
    s = 2 + a
    s1 = 2*a
    m = a*b
    m1 = a**2
    assert n*2==6
    assert n*n==9
    assert str(n*a)==str('3*a')
    assert str(n*s)==str('6 + 3*a')
    assert str(n*s1)==str('6*a')
    assert str(n*m)==str('3*a*b')
    assert str(n*m1)==str('3*a**2')

def test_number_pow():
    n = Number(3)
    a = Symbol('a')
    b = Symbol('b')
    s = 2 + a
    s1 = 2*a
    m = a*b
    m1 = a**2
    assert n**1==3
    assert n**0==1
    assert n**2==9
    assert n**n==27
    assert str(n**a)==str('3**a')
    assert str(n**s)==str('3**(2 + a)')
    assert str(n**s1)==str('9**a')
    assert str(n**m)==str('3**(a*b)')
    assert str(n**m1)==str('3**(a**2)')

def test_symbol_add():
    n = Number(3)
    a = Symbol('a')
    b = Symbol('b')
    s = 2 + a
    s1 = 2*a
    m = a*b
    m1 = a**2
    assert str(a+2)==str('2 + a')
    assert str(a+a)==str('2*a')
    assert str(a+n)==str('3 + a')
    assert str(a+s)==str('2 + 2*a')
    assert str(a+s1)==str('3*a')
    assert str(b+s1)==str('b + 2*a')
    assert str(a+m)==str('a + a*b')
    assert str(a+m1)==str('a + a**2')

def test_symbol_mul():
    n = Number(3)
    a = Symbol('a')
    b = Symbol('b')
    s = 2 + a
    s1 = 2*a
    m = a*b
    m1 = a**2
    assert str(a*2)=='2*a'
    assert str(a*a)=='a**2'
    assert str(a*n)==str('3*a')
    assert str(a*s)==str('a*(2 + a)')
    assert str(a*s1)==str('2*a**2')
    assert str(b*s1)==str('2*a*b')
    assert str(a*m)==str('b*a**2')
    assert str(a*m1)==str('a**3')
    assert str(b*m1)==str('b*a**2')

def test_symbol_pow():
    n = Number(3)
    a = Symbol('a')
    b = Symbol('b')
    s = 2 + a
    s1 = 2*a
    m = a*b
    m1 = a**2
    assert a**1==a
    assert a**0==1
    assert str(a**2)=='a**2'
    assert str(a**n)=='a**3'
    assert str(a**a)==str('a**a')
    assert str(a**s)==str('a**(2 + a)')
    assert str(a**s1)==str('(a**a)**2')
    assert str(a**m)==str('a**(a*b)')
    assert str(a**m1)==str('a**(a**2)')

def test_add_add():
    n = Number(3)
    a = Symbol('a')
    b = Symbol('b')
    s = 2 + a
    s1 = 2*a
    m = a*b
    m1 = a**2
    assert str(s+2)==str('4 + a')
    assert str(s+a)==str('2 + 2*a')
    assert str(s+n)==str('5 + a')
    assert str(s+s)==str('4 + 2*a')
    assert str(s+s1)==str('2 + 3*a')
    assert str(s+m)==str('2 + a + a*b')
    assert str(s+m1)==str('2 + a + a**2')

    assert str(s1+2)==str('2 + 2*a')
    assert str(s1+a)==str('3*a')
    assert str(s1+n)==str('3 + 2*a')
    assert str(s1+s)==str('2 + 3*a')
    assert str(s1+s1)==str('4*a')
    assert str(s1+m)==str('2*a + a*b')
    assert str(s1+m1)==str('2*a + a**2')

def test_add_mul():
    n = Number(3)
    a = Symbol('a')
    b = Symbol('b')
    s = 2 + a
    s1 = 2*a
    m = a*b
    m1 = a**2
    assert str(s*2)=='4 + 2*a'
    assert str(s*a)=='a*(2 + a)'
    assert str(s*n)==str('6 + 3*a')
    assert str(s*s)==str('(2 + a)**2')
    assert str(s*s1)==str('2*a*(2 + a)')
    assert str(s*m)==str('a*b*(2 + a)')
    assert str(s*m1)==str('(2 + a)*a**2')

    assert str(s1*2)=='4*a'
    assert str(s1*a)=='2*a**2'
    assert str(s1*n)==str('6*a')
    assert str(s1*s)==str('2*a*(2 + a)')
    assert str(s1*s1)==str('4*a**2')
    assert str(s1*m)==str('2*b*a**2')
    assert str(s1*m1)==str('2*a**3')

def test_add_pow():
    n = Number(3)
    a = Symbol('a')
    b = Symbol('b')
    s = 2 + a
    s1 = 2*a
    m = a*b
    m1 = a**2
    
    assert s**1==s
    assert s**0==1
    assert str(s**2)=='(2 + a)**2'
    assert str(s**n)=='(2 + a)**3'
    assert str(s**a)==str('(2 + a)**a')
    assert str(s**s)==str('(2 + a)**(2 + a)')
    assert str(s**s1)==str('(2 + a)**(2*a)')
    assert str(s**m)==str('(2 + a)**(a*b)')
    assert str(s**m1)==str('(2 + a)**(a**2)')

    assert s1**1==s1
    assert s1**0==1
    assert str(s1**2)=='4*a**2'
    assert str(s1**n)=='8*a**3'
    assert str(s1**a)==str('(2*a)**a')
    assert str(s1**s)==str('2**(2 + a)*a**(2 + a)')
    assert str(s1**s1)==str('4**a*a**(2*a)')
    assert str(s1**m)==str('(2*a)**(a*b)')
    assert str(s1**m1)==str('(2*a)**(a**2)')

def test_mul_add():
    n = Number(3)
    a = Symbol('a')
    b = Symbol('b')
    s = 2 + a
    s1 = 2*a
    m = a*b
    m1 = a**2
    assert str(m+2)==str('2 + a*b')
    assert str(m+a)==str('a + a*b')
    assert str(m+n)==str('3 + a*b')
    assert str(m+s)==str('2 + a + a*b')
    assert str(m+s1)==str('2*a + a*b')
    assert str(m+m)==str('2*a*b')
    assert str(m+m1)==str('a*b + a**2')

    assert str(m1+2)==str('2 + a**2')
    assert str(m1+a)==str('a + a**2')
    assert str(m1+n)==str('3 + a**2')
    assert str(m1+s)==str('2 + a + a**2')
    assert str(m1+s1)==str('2*a + a**2')
    assert str(m1+m)==str('a*b + a**2')
    assert str(m1+m1)==str('2*a**2')

def test_mul_mul():
    n = Number(3)
    a = Symbol('a')
    b = Symbol('b')
    s = 2 + a
    s1 = 2*a
    m = a*b
    m1 = a**2
    assert str(m*2)=='2*a*b'
    assert str(m*a)=='b*a**2'
    assert str(m*n)==str('3*a*b')
    assert str(m*s)==str('a*b*(2 + a)')
    assert str(m*s1)==str('2*b*a**2')
    assert str(m*m)==str('a**2*b**2')
    assert str(m*m1)==str('b*a**3')

    assert str(m1*2)=='2*a**2'
    assert str(m1*a)=='a**3'
    assert str(m1*n)==str('3*a**2')
    assert str(m1*s)==str('(2 + a)*a**2')
    assert str(m1*s1)==str('2*a**3')
    assert str(m1*m)==str('b*a**3')
    assert str(m1*m1)==str('a**4')

def test_mul_pow():
    n = Number(3)
    a = Symbol('a')
    b = Symbol('b')
    s = 2 + a
    s1 = 2*a
    m = a*b
    m1 = a**2

    assert m**1==m
    assert m**0==1
    assert str(m**2)=='a**2*b**2'
    assert str(m**n)=='a**3*b**3'
    assert str(m**a)==str('(a*b)**a')
    assert str(m**s)==str('(a*b)**(2 + a)')
    assert str(m**s1)==str('(a*b)**(2*a)')
    assert str(m**m)==str('(a*b)**(a*b)')
    assert str(m**m1)==str('(a*b)**(a**2)')

    assert str(m1**2)=='a**4'
    assert str(m1**n)=='a**6'
    assert str(m1**a)==str('(a**a)**2')
    assert str(m1**s)==str('a**(4 + 2*a)')
    assert str(m1**s1)==str('a**(4*a)')
    assert str(m1**m)==str('a**(2*a*b)')
    assert str(m1**m1)==str('a**(2*a**2)')


def test_expand():
    x,y,z = map(Symbol, 'xyz')
    assert ((x+y)**2).expand()==x**2+y**2+2*x*y
    assert str(((x+y)**2).expand())=='2*x*y + x**2 + y**2'
    assert ((x-y)**2).expand()==x**2+y**2-2*x*y
    assert ((x+y)**3).expand()==x**3+y**3+3*x**2*y+3*x*y**2
    assert ((x-y)**3).expand()==x**3-y**3-3*x**2*y+3*x*y**2
    assert ((x+y)**3).expand()==-((-x-y)**3).expand()
    assert str((x*(x+y)).expand())=='x*y + x**2'
    assert str(((x+y)*x).expand())=='x*y + x**2'
    
    assert str(((x+y+z)**2).expand())=='2*x*y + 2*x*z + 2*y*z + x**2 + y**2 + z**2'
    assert str(((x+y+z)**3).expand())==\
           '3*x*y**2 + 3*x*z**2 + 3*y*x**2 + 3*y*z**2 + 3*z*x**2 + 3*z*y**2 + 6*x*y*z + x**3 + y**3 + z**3'

    assert str(((2*x+y)**2).expand())=='4*x**2 + 4*x*y + y**2'
    assert str(((2*x-y)**2).expand())=='4*x**2 + y**2 - 4*x*y'
    assert str(((x+y)**2-x**2-y**2).expand())=='2*x*y'
    assert str((((x+y)**2-x**2-y**2)*(x*y)).expand())=='2*x**2*y**2'
    assert str(((x*y)*((x+y)**2-x**2-y**2)).expand())=='2*x**2*y**2'
    assert str(((3*x*y)*((x+y)**2-x**2-y**2)).expand())=='6*x**2*y**2'
    assert str(((1/x)*((x+y)**2-x**2-y**2)).expand())=='2*y'
    assert str(((3/x)*((x+y)**2-x**2-y**2)).expand())=='6*y'
    assert str(((x**2)*((x+y)**2-x**2-y**2)).expand())=='2*y*x**3'
    assert str((((x+y)**2-x**2-y**2)*(x**2)).expand())=='2*y*x**3'
    two = ((x+y)**2-x**2-y**2)/x/y
    assert str((two).expand())=='2'
    assert str((two*x).expand())=='2*x'
    assert str((two*(2*x)).expand())=='4*x'
    assert str((two*(x+y)).expand())=='2*x + 2*y'
    assert str((x*two).expand())=='2*x'
    assert str(((x-y)*two).expand())=='2*x - 2*y'

    two_y = ((x+y)**2-x**2-y**2)/x
    assert str((two_y).expand())=='2*y'
    assert str((two_y*x).expand())=='2*x*y'
    assert str((two_y*(2*x)).expand())=='4*x*y'
    assert str((two_y*(x+y)).expand())=='2*y**2 + 2*x*y'
    assert str((x*two_y).expand())=='2*x*y'
    assert str(((x-y)*two_y).expand())=='2*x*y - 2*y**2'

    x2 = ((x+y)**2-x**2-y**2)/y*x/2
    assert str((x2).expand())=='x**2'
    assert str((2*x2).expand())=='2*x**2'
    assert str((x*x2).expand())=='x**3'
    assert str((x**2*x2).expand())=='x**4'
    assert str((y*x2).expand())=='y*x**2'

    assert str(((x+y)*(x+y+z)).expand())=='x*z + y*z + 2*x*y + x**2 + y**2'
    assert str(((x+y+z)*(x+y)).expand())=='x*z + y*z + 2*x*y + x**2 + y**2'
    assert str(((1/x+x)*x).expand())=='1 + x**2'
    assert str((x**2*(1/x+x)**2).expand())=='1 + 2*x**2 + x**4'

def test_diff():
    x = Symbol('x')
    assert Number(2).diff(x) == 0
    assert x.diff(x) == 1
    assert (3*x).diff(x) == 3
    assert (3*x+1).diff(x) == 3
    assert (2*x**2 + x).diff(x) == 4*x + 1
    assert (x**3).diff(x) == 3*x**2

def test_integrate():
    x = Symbol('x')
    y = Symbol('y')
    assert Number(3).integrate(x) == 3*x
    assert x.integrate(x) == x**2 / 2
    assert (2*x).integrate(x) == x**2
    r1 = (1 + 4*y*x + 3*x**2).integrate(x)
    r2 = x + 4*Number(2)**-1*y*x**2 + x**3
    assert r1 == r2
