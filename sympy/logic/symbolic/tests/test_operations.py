
from sympy import *

def test_And():
    x = Boolean('x')
    y = Boolean('y')
    assert And()==True
    assert And(True)==True
    assert And(False)==False
    assert And(True,True)==True
    assert And(True,False)==False
    assert And(False,True)==False
    assert And(False,False)==False

    assert isinstance(And(x,y), classes.And)==True
    assert And(x,x)==x
    assert And(x,False)==False
    assert And(x,True)==x
    assert And(x,And(x,y))==And(x,y)

    assert And(x,y).tostr()=='And(x, y)'
    assert And(x,y).torepr()=="And(Boolean('x'), Boolean('y'))"

    assert And(x,y)==And(y,x)
    assert And(x,Not(x))==False

def test_Or():
    x = Boolean('x')
    y = Boolean('y')
    assert Or()==False
    assert Or(True)==True
    assert Or(False)==False
    assert Or(True,True)==True
    assert Or(True,False)==True
    assert Or(False,True)==True
    assert Or(False,False)==False

    assert isinstance(Or(x,y), classes.Or)==True
    assert Or(x,False)==x
    assert Or(x,True)==True
    assert Or(x,Or(x,y))==Or(x,y)
    assert Or(x,Or(x,y),y,x)==Or(x,y)

    assert Or(x,y).tostr()=='Or(x, y)'
    assert Or(x,y).torepr()=="Or(Boolean('x'), Boolean('y'))"

    assert Or(x,y)==Or(y,x)
    assert Or(x,Not(x))==True

def test_Xor():
    x = Boolean('x')
    y = Boolean('y')
    assert Xor()==False
    assert Xor(True)==True
    assert Xor(False)==False
    assert Xor(True,True)==False
    assert Xor(True,False)==True
    assert Xor(False,True)==True
    assert Xor(False,False)==False

    assert isinstance(Xor(x,y), classes.Xor)==True
    assert Xor(x,False)==x
    assert Xor(x,True)==Not(x)
    assert Xor(x,Xor(x,y))==y

    assert Xor(x,y).tostr()=='Xor(x, y)'
    assert Xor(x,y).torepr()=="Xor(Boolean('x'), Boolean('y'))"

    assert Xor(x,y)!=Xor(y,x)
    assert Xor(x,Not(x))==True

def test_Not():
    x = Boolean('x')
    assert Not(False)==True
    assert Not(True)==False
    assert isinstance(Not(x), classes.Not)==True
    assert Not(Not(x))==x

def test_Implies():
    assert Implies(False, True)==True
    assert Implies(True, True)==True
    assert Implies(True, False)==False
    assert Implies(False, False)==True

    x = Boolean('x')
    assert Implies(False, x)==True
    assert Implies(True, x)==x
    assert Implies(x,False)==Not(x)
    assert Implies(x,True)==True

def test_Equiv():
    assert Equiv(False, True)==False
    assert Equiv(True, True)==True
    assert Equiv(True, False)==False
    assert Equiv(False, False)==True

    x = Boolean('x')
    assert Equiv(False, x)==Not(x)
    assert Equiv(True, x)==x
    assert Equiv(x,False)==Not(x)
    assert Equiv(x,True)==x
