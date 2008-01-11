
from sympycore import *
from sympycore.algebra import *

def test_numbers():
    i = Integers(1)
    assert isinstance(i, Integers)==True
    assert isinstance(i, IntegerNumber)==True
    assert str(i)=='1'
    assert bool(i==1)==True
    assert bool(i==2)==False
    assert bool(i=='a')==False

def test_symbols():
    i = Integers('a')
    assert isinstance(i, Integers)==True
    assert isinstance(i, IntegerSymbol)==True
    assert str(i)=='a'
    assert bool(i==1)==False
    assert bool(i=='a')==True

def test_terms():
    ab = Integers.Add(['a','b'])
    assert isinstance(ab, Integers)==True
    assert isinstance(ab, classes.IntegerTerms)==True
    assert str(ab) in ['a + b','b + a']
    assert bool(ab=='a+b')==True
    assert bool(ab=='b+a')==True

def test_Factors():
    ab = Integers.Mul(['a','b'])
    assert isinstance(ab, Integers)==True
    assert isinstance(ab, classes.IntegerFactors)==True
    assert str(ab) in ['a*b','b*a']
    assert bool(ab=='a*b')==True
    assert bool(ab=='b*a')==True

def test_pos():
    assert +Integers(2)==2
    assert +Integers('a')==Integers('a')

def test_neg():
    assert -Integers(2)==-2
    b = -Integers('a')
    assert isinstance(b, Integers)==True
    assert isinstance(b, classes.IntegerTerms)==True
    assert str(b) == '-a'

def test_add():
    i = Integers(1)
    j = Integers(2)
    assert isinstance(i+j, Integers)==True
    assert isinstance(i+j, IntegerNumber)==True
    assert isinstance(1+j, IntegerNumber)==True
    assert bool(i+j==3)==True
    assert bool(i+2==3)==True
    assert bool(1+j==3)==True

    a = Integers('a')
    b = Integers('b')

    assert isinstance(a+b, Integers)==True
    assert isinstance(a+b, classes.IntegerTerms)==True
    assert str(a+b) in ['a + b', 'b + a']
    assert a+b==b+a

    assert isinstance(a+i, Integers)==True
    assert isinstance(a+i, classes.IntegerTerms)==True
    assert str(a+i) in ['a + 1', '1 + a']
    assert a+i==i+a
    assert a+1==a+i
    assert 1+a==a+i
    assert '1'+a==a+i
    assert a+'1'==a+i
    assert i+'a'==a+i
    assert 'a'+i==a+i
