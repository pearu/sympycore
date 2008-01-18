
from sympycore.algebra.pairs import CommutativeRingWithPairs as Algebra

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
