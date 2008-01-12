
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
    assert str(ab)=='a*b'
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
    assert a+0==a
    assert 0+a==a
    assert str(a+a)=='2*a'

    ab = a + b
    assert isinstance(ab+i, Integers)==True
    assert isinstance(ab+i, classes.IntegerTerms)==True
    assert str(ab+i)=='1 + a + b'
    assert str(ab+2)=='2 + a + b'
    assert str(ab+'3')=='3 + a + b'
    assert str(ab+ab)=='2*a + 2*b'
    assert str(ab+a)=='b + 2*a'
    assert str(ab+2*a)=='b + 3*a'
    assert str(ab+a*b)=='a + b + a*b'
    assert str(ab-ab)=='0'
    assert i+ab == ab+i
    assert 2+ab == ab+2
    assert '3'+ab == ab+'3'
    assert 0+ab == ab
    assert ab+0 == ab
    assert ab+a == a+ab
    assert ab+2*a == 2*a+ab
    assert ab + a*b == a*b + ab

    ab = a * b

    assert isinstance(ab+i, Integers)==True
    assert isinstance(ab+i, classes.IntegerTerms)==True
    assert str(ab+i)=='1 + a*b'
    assert str(ab+2)=='2 + a*b'
    assert str(ab+'3')=='3 + a*b'
    assert str(ab+ab)=='2*a*b'
    assert str(ab+a*ab)=='a*b + b*a**2'
    assert str(ab+a)=='a + a*b'
    assert str(ab-ab)=='0'
    assert i+ab == ab+i
    assert 2+ab == ab+2
    assert '3'+ab == ab+'3'
    assert ab+a==a+ab
    assert 0+ab == ab
    assert ab+0 == ab
    assert str(a + ab) == 'a + a*b'


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
    assert str(a*b)=='a*b'
    assert a*b==b*a

    assert isinstance(a+i, Integers)==True
    assert isinstance(a*i, classes.IntegerTerms)==True
    assert str(a*i)=='3*a'
    assert a*i==i*a
    assert a*3==a*i
    assert 3*a==a*i
    assert '3'*a==a*i
    assert a*'3'==a*i
    assert i*'a'==a*i
    assert 'a'*i==a*i
    assert a*1==a
    assert 1*a==a
    assert a*0==0
    assert 0*a==0
    assert str(a*a)=='a**2'

    
    ab = a + b
    assert isinstance(ab*i, Integers)==True
    assert isinstance(ab*i, classes.IntegerTerms)==True
    assert str(ab*i)=='3*a + 3*b'
    assert str(ab*2)=='2*a + 2*b'
    assert str(ab*'3')=='3*a + 3*b'
    assert str(ab*ab)=='(a + b)**2'
    assert str(ab*(1+ab))=='(a + b)*(1 + a + b)'
    assert i*ab == ab*i
    assert 2*ab == ab*2
    assert '3'*ab == ab*'3'
    assert 1*ab == ab
    assert ab*1 == ab
    assert 0*ab == 0
    assert ab*0 == 0
    assert str(a*ab)=='a*(a + b)'

    ab = a * b
    assert isinstance(ab*i, Integers)==True
    assert isinstance(ab*i, classes.IntegerTerms)==True
    assert str(ab*i)=='3*a*b'
    assert str(ab*2)=='2*a*b'
    assert str(ab*'3')=='3*a*b'
    assert str(ab*ab)=='a**2*b**2'
    assert str(ab*a**2)=='b*a**3'
    assert str((a+b)*ab)=='a*b*(a + b)'
    assert i*ab == ab*i
    assert 2*ab == ab*2
    assert '3'*ab == ab*'3'
    assert (a+b)*ab == ab*(a+b)
    assert ab*a**2==a**2*ab

    assert 1*ab == ab
    assert ab*1 == ab
    assert 0*ab == 0
    assert ab*0 == 0
    assert str(a*ab)=='b*a**2'
    assert str(a*(2*a))=='2*a**2'
    assert str(a*(2*b))=='2*a*b'
    assert a*ab==ab*a
    assert a*(2*a)==(2*a)*a
    assert a*(2*b)==(2*b)*a



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
    assert str((2*a)**2)=='4*a**2'

    assert a**1==a
    assert a**0==1
    assert Integers(1)**3==1

    assert 2**i==8

def test_int_long():
    assert isinstance(int(Integers(-4)), int)==True
    assert int(Integers(-4))==-4
    assert isinstance(long(Integers(-4)), long)==True
    assert long(Integers(-4))==-4L

def test_abs():
    assert abs(Integers(-4))==Integers(4)

def test_relational():
    assert bool(Integers(3)<Integers(4))==True
    assert bool(Integers(3)<=Integers(4))==True
    assert bool(Integers(3)>Integers(4))==False
    assert bool(Integers(3)>=Integers(4))==False
    assert bool(Integers(3)==Integers(4))==False
    assert bool(Integers(3)!=Integers(4))==True

    assert bool(Integers(5)<Integers(4))==False
    assert bool(Integers(5)<=Integers(4))==False
    assert bool(Integers(5)>Integers(4))==True
    assert bool(Integers(5)>=Integers(4))==True
    assert bool(Integers(5)==Integers(4))==False
    assert bool(Integers(5)!=Integers(4))==True

def test_as_terms_intcoeff():
    assert Integers('2').as_terms_intcoeff()==(1,2)

    assert Integers('2*a').as_terms_intcoeff()==(Integers('a'),2)
    assert Integers('-2*a').as_terms_intcoeff()==(Integers('a'),-2)
    
    assert Integers('2+a').as_terms_intcoeff()==(Integers('2+a'),1)
    assert Integers('-2-a').as_terms_intcoeff()==(Integers('2+a'),-1)
    assert Integers('2-a').as_terms_intcoeff()==(Integers('2-a'),1)
    assert Integers('-2+a').as_terms_intcoeff()==(Integers('-2+a'),1)
    
    assert Integers('2+2*a').as_terms_intcoeff()==(Integers('1+a'),2)
    assert Integers('2+4*a').as_terms_intcoeff()==(Integers('1+2*a'),2)
    assert Integers('2-4*a').as_terms_intcoeff()==(Integers('1-2*a'),2)
    assert Integers('-2-4*a').as_terms_intcoeff()==(Integers('1+2*a'),-2)
    assert Integers('-2+4*a').as_terms_intcoeff()==(Integers('-1+2*a'),2)
    
    assert Integers('2*a+2*b').as_terms_intcoeff()==(Integers('a+b'),2)
    assert Integers('2*a+4*b').as_terms_intcoeff()==(Integers('a+2*b'),2)
    assert Integers('2*a-4*b').as_terms_intcoeff()==(Integers('a-2*b'),2)
    assert Integers('-2*a-4*b').as_terms_intcoeff()==(Integers('a+2*b'),-2)
    assert Integers('-2*a+4*b').as_terms_intcoeff()==(Integers('-a+2*b'),2)


    assert Integers('(-2*a+4*b)*2*a').as_terms_intcoeff()==(Integers('(-a+2*b)*a'),4)

def test_expand():
    assert str(Integers('a+b').expand())=='a + b'
    assert str(Integers('a*(a+b)').expand())=='a*b + a**2'
    assert str(Integers('(a+b)*a').expand())=='a*b + a**2'
    assert str(Integers('(a+b)*(a-b)').expand())=='a**2 - b**2'
    assert str(Integers('(a+b)*(a+b+c)').expand())=='2*a*b + a*c + b*c + a**2 + b**2'
    
