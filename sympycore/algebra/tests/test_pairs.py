
from sympycore.algebra.pairs import CommutativeRingWithPairs as Algebra

Symbol = Algebra.Symbol
Number = Algebra.Number
Add = Algebra.Add
Mul = Algebra.Mul
Pow = Algebra.Pow

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
