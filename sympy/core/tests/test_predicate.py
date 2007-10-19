
from sympy import *

'''
def test_truth_table():

    assert Not(False)==True
    assert Not(True)==False
    assert Or(False, False)==False
    assert Or(False, True)==True
    assert Or(True, False)==True
    assert Or(True, True)==True
    assert XOr(False, False)==False
    assert XOr(False, True)==True
    assert XOr(True, False)==True
    assert XOr(True, True)==False
    assert And(False, False)==False
    assert And(False, True)==False
    assert And(True, False)==False
    assert And(True, True)==True
    assert Implies(False, False)==True
    assert Implies(False, True)==True
    assert Implies(True, False)==False
    assert Implies(True, True)==True
    assert Equiv(False, False)==True
    assert Equiv(False, True)==False
    assert Equiv(True, False)==False
    assert Equiv(True, True)==True

def test_trivial():
    assert Or(False)==False
    assert Or(True)==True
    assert And(False)==False
    assert And(True)==True
    assert XOr(False)==False
    assert XOr(True)==True

    # logic: a <op> <nothing> -> a
    assert Or()==False   # a OR False -> a
    assert And()==True  # a AND True -> a
    assert XOr()==False # a XOR False -> a

def test_operators():
    a,b,c,d = map(Boolean,'abcd')
    assert (~a) & b & (~c) & d == ~a & b & ~c & d

def test_minimize1():
    a,b,c,d = map(Boolean,'abcd')
    f = ~a & b & ~c & ~d | a & ~b & ~c & ~d | a & ~b & c & ~d | a & ~b & c & d
    f = f | a & b & ~c & ~d | a & b & c & d
    f = f | a & ~b & ~c & d | a & b & c & ~d
    atoms, table = f.truth_table()
    fmin = f.minimize()
    table_min = fmin.truth_table(atoms)[1]
    assert table==table_min
    f1,f2 = a & c | b & ~c & ~d | a & ~b,a & c | b & ~c & ~d | a & ~d
    assert fmin in [f1,f2]

def test_minimize2():
    a,b,c,d = Less('x',2),Less('y',1),Equal('x','y+1'),Boolean('a')
    f = ~a & b & ~c & ~d | a & ~b & ~c & ~d | a & ~b & c & ~d | a & ~b & c & d
    f = f | a & b & ~c & ~d | a & b & c & d
    f = f | a & ~b & ~c & d | a & b & c & ~d
    atoms, table = f.truth_table()
    fmin = f.minimize()
    table_min = fmin.truth_table(atoms)[1]
    assert table==table_min
    f1,f2 = a & c | b & ~c & ~d | a & ~b,\
            a & c | b & ~c & ~d | a & ~d
    assert fmin in [f1,f2]

def test_normalize():
    x = Symbol('x')
    assert IsComplex(2*x/3)==IsComplex(x)
    assert IsReal(2*x/3)==IsReal(x)
    assert IsImaginary(2*x/3)==IsImaginary(x)
    assert IsRational(2*x/3)==IsRational(x)
    assert IsIrrational(2*x/3)==IsIrrational(x)
    assert IsInteger(2*x)==IsInteger(x)
    assert IsInteger(2*x/3)==IsInteger(x/3)
    assert IsInteger(-x/3)==IsInteger(x/3)
    assert IsFraction(-2*x)==IsFraction(2*x)
    assert IsOdd(-2*x)==IsOdd(x)
    assert IsOdd(-3*x)==IsOdd(3*x)
    assert IsEven(-3*x)==IsEven(x)
    assert IsEven(-3*x/2)==IsEven(3*x/2)
    assert IsComposite(-2*x)==IsComposite(2*x)
    assert IsPrime(-2*x)==IsPrime(-2*x)

    assert IsPositive(2*x)==IsPositive(x)
    assert IsNegative(2*x/3)==IsNegative(x)
    assert IsPositive(-2*x)==IsNegative(x)
    assert IsNegative(-2*x/3)==IsPositive(x)
    assert IsNonPositive(2*x)==IsNonPositive(x)
    assert IsNonNegative(2*x/3)==IsNonNegative(x)
    assert IsNonPositive(-2*x)==IsNonNegative(x)
    assert IsNonNegative(-2*x/3)==IsNonPositive(x)
    assert IsZero(-2*x/3)==IsZero(x)
    
def test_bug1():
    x = Symbol('x')
    r1 = And(IsInteger(x), IsReal(x)).test(IsInteger(x))
    r2 = And(IsInteger(x), IsReal(x)).refine().test(IsInteger(x))
    assert r1==r2

def test_inclusion():
    x = Symbol('x')
    a = IsInteger(x)
    assert a.test(IsInteger(x))==True
    assert a.test(IsFraction(x))==False
    assert a.test(IsRational(x))==True
    assert a.test(IsReal(x))==True
    assert a.test(IsImaginary(x))==False
    assert a.test(IsComplex(x))==True
    assert a.test(IsEven(x))==IsEven(x)
    assert a.test(IsPrime(x))==IsPrime(x)
    assert a.test(And(IsPrime(x),IsEven(x)))==And(IsPrime(x),IsEven(x))

    a = IsEven(x)
    assert a.test(IsInteger(x))==True
    assert a.test(IsFraction(x))==False
    assert a.test(IsRational(x))==True
    assert a.test(IsReal(x))==True
    assert a.test(IsImaginary(x))==False
    assert a.test(IsComplex(x))==True
    assert a.test(IsEven(x))==True
    assert a.test(IsOdd(x))==False
    assert a.test(IsPrime(x))==IsPrime(x)

def test_test_logic():
    a = Boolean('a')
    b = Boolean('b')
    assert a.test(a)==True
    assert Not(a).test(a)==False

    assert a.test(b)==b
    assert Not(a).test(b)==b
    assert a.test(Not(b))==Not(b)
    
    assert Or(a,b).test(a)==True
    assert Or(~a,b).test(a)==b
    assert And(a,b).test(a)==b
    assert And(~a,b).test(a)==False


def test_bug2():
    x = Symbol('x')
    a = IsEven(x)
    assert a.test(IsPrime(x))==IsPrime(x)

def test_signed():
    x = Symbol('x')
    a = IsPositive(x)
    assert a.test(IsPositive(x))==True
    assert a.test(IsNonPositive(x))==False
    assert a.test(IsNegative(x))==False
    assert a.test(IsNonNegative(x))==True
    assert a.test(IsZero(x))==False

    a = IsNegative(x)
    assert a.test(IsNegative(x))==True
    assert a.test(IsNonNegative(x))==False
    assert a.test(IsPositive(x))==False
    assert a.test(IsNonPositive(x))==True
    assert a.test(IsZero(x))==False

    a = IsNonPositive(x)
    assert a.test(IsPositive(x))==False
    assert a.test(IsNonPositive(x))==True
    assert a.test(IsNegative(x))==IsNonZero(x)
    assert a.test(IsNonNegative(x))==IsZero(x)
    assert a.test(IsZero(x))==IsNonNegative(x)

    a = IsNonNegative(x)
    assert a.test(IsNegative(x))==False
    assert a.test(IsNonNegative(x))==True
    assert a.test(IsPositive(x))==IsNonZero(x)
    assert a.test(IsNonPositive(x))==IsZero(x)
    assert a.test(IsZero(x))==IsNonPositive(x)


def test_ispositive():
    x = Symbol('x')
    a = Less(1,x)
    assert a.test(IsPositive(x))==True
    
'''
