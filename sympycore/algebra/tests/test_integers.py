
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
    assert str(ab)=='a + b'
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

    ab = Integers('a+b')
    assert isinstance(-ab, Integers)==True
    assert isinstance(-ab, classes.IntegerTerms)==True
    assert str(-ab) == '-a - b'

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
    assert str(a+b)=='a + b'
    assert a+b==b+a

    assert isinstance(a+i, Integers)==True
    assert isinstance(a+i, classes.IntegerTerms)==True
    assert str(a+i)=='1 + a'
    assert a+i==i+a
    assert a+1==a+i
    assert 1+a==a+i
    assert '1'+a==a+i
    assert a+'1'==a+i
    assert i+'a'==a+i
    assert 'a'+i==a+i

    ab = a + b
    assert isinstance(ab+i, Integers)==True
    assert isinstance(ab+i, classes.IntegerTerms)==True
    assert str(ab+i)=='1 + a + b'
    assert str(ab+2)=='2 + a + b'
    assert str(ab+'3')=='3 + a + b'
    assert str(ab+ab)=='2*a + 2*b'
    assert str(ab-ab)=='0'

    ab = a * b

    assert isinstance(ab+i, Integers)==True
    assert isinstance(ab+i, classes.IntegerTerms)==True
    assert str(ab+i)=='1 + a*b'
    assert str(ab+2)=='2 + a*b'
    assert str(ab+'3')=='3 + a*b'
    assert str(ab+ab)=='2*a*b'
    assert str(ab-ab)=='0'

def test_mul():
    i = Integers(3)
    j = Integers(2)
    assert isinstance(i*j, Integers)==True
    assert isinstance(i*j, IntegerNumber)==True
    assert isinstance(3*j, IntegerNumber)==True
    assert bool(i*j==6)==True
    assert bool(i*2==6)==True
    assert bool(3*j==6)==True

    a = Integers('a')
    b = Integers('b')

    assert isinstance(a*b, Integers)==True
    assert isinstance(a*b, classes.IntegerFactors)==True
    assert str(a*b) in ['a*b', 'b*a']
    assert a*b==b*a

    assert isinstance(a+i, Integers)==True
    assert isinstance(a*i, classes.IntegerTerms)==True
    assert str(a*i) in ['a*3', '3*a']
    assert a*i==i*a
    assert a*3==a*i
    assert 3*a==a*i
    assert '3'*a==a*i
    assert a*'3'==a*i
    assert i*'a'==a*i
    assert 'a'*i==a*i

    ab = a + b
    assert isinstance(ab*i, Integers)==True
    assert isinstance(ab*i, classes.IntegerTerms)==True
    assert str(ab*i)=='3*a + 3*b'
    assert str(ab*2)=='2*a + 2*b'
    assert str(ab*'3')=='3*a + 3*b'
    assert str(ab*ab)=='(a + b)**2'
    assert str(ab*(1+ab))=='(a + b)*(1 + a + b)'

    ab = a * b
    assert isinstance(ab*i, Integers)==True
    assert isinstance(ab*i, classes.IntegerTerms)==True
    assert str(ab*i)=='3*a*b'
    assert str(ab*2)=='2*a*b'
    assert str(ab*'3')=='3*a*b'
    assert str(ab*ab)=='a**2*b**2'

def test_pow():
    i = Integers(3)
    j = Integers(2)
    assert isinstance(i**j, Integers)==True
    assert isinstance(i**j, IntegerNumber)==True
    assert i**j==9

    a = Integers('a')
    b = Integers('b')
    
    assert isinstance(a**j, Integers)==True
    assert isinstance(a**j, classes.IntegerFactors)==True
    assert str(a**j)=='a**2'
    assert str(a**3)=='a**3'
    assert str(a**'4')=='a**4'
    assert str(a**b)=='a**b'
    assert str(a**'b')=='a**b'
    assert str(a**(b+1))=='a**(1 + b)'
    assert str(a**(2*b))=='(a**b)**2'
    assert str(j**(2*b))=='4**b'
    assert str(a**(2*a+2))=='(a**(1 + a))**2'
    assert str(a**(-a))=='a**(-a)'
    assert str((2*a)**2)=='4*a**2'
    assert str((2*a)**(3*a))=='8*(a**a)**3'
