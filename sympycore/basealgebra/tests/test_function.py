
from sympycore import CommutativeRingWithPairs as Algebra

Symbol = Algebra.Symbol
Number = Algebra.Number
Add = Algebra.Add
Mul = Algebra.Mul
Pow = Algebra.Pow
Terms = Algebra.Terms
Factors = Algebra.Factors
Apply = Algebra.Apply

x,y,z = map(Symbol, 'xyz')

def foo(x):
    """ Python function can be used to construct applied functions.
    """
    if x==0:
        return x
    return Algebra(foo, x)

class bar(object):
    """ Python new-style class can be used to construct applied
    functions.
    """
    def __new__(cls, x):
        if x==0:
            return x
        return Algebra(cls, x)

class Fun:
    """ A callable class instance can be used to construct applied
    functions.
    """
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name
    
    def __call__(self, x):
        if x==0:
            return x
        return Algebra(self, x)

fun = Fun('fun')

def mysin(x):
    if x==0:
        return x
    return Algebra(mysin, x)

def mycos(x):
    if x==0:
        return Algebra.one
    return Algebra(mycos, x)

mysin.derivative = lambda arg: mycos(arg)
mycos.derivative = lambda arg: -mysin(arg)

def foo2(x, y):
    if x==y:
        return Algebra.one
    return Algebra(foo2, (x,y))

def foo2_1(x, y):
    return Algebra(foo2_1, (x,y))
def foo2_2(x, y):
    return Algebra(foo2_2, (x,y))

foo2.derivative = foo2_1,foo2_2

def bar2(x, y):
    return Algebra(bar2, (x,y))

def test_foo():
    assert str(foo(x))=='foo(x)'
    assert str(foo(0))=='0'
    assert str(foo(x+y))=='foo(x + y)'

    assert foo(x)==foo(x)
    assert foo(x).subs(x,z)==foo(z)
    assert foo(x).subs(x,0)==0
    assert (y+foo(x)).subs(x,0)==y

    assert str(foo(foo(x)))=='foo(foo(x))'
    assert str(foo(x)+foo(y))=='foo(x) + foo(y)'
    assert str(foo(x)+x*foo(y))=='foo(x) + x*foo(y)'

    assert str((foo(x)+foo(y))**2)=='(foo(x) + foo(y))**2'
    assert str(((foo(x)+foo(y))**2).expand()) in ['2*foo(x)*foo(y) + foo(x)**2 + foo(y)**2',
                                                  'foo(x)**2 + foo(y)**2 + 2*foo(x)*foo(y)']


def test_bar():
    assert str(bar(x))=='bar(x)'
    assert str(bar(0))=='0'
    assert str(bar(x+y))=='bar(x + y)'

    assert bar(x)==bar(x)
    assert bar(x).subs(x,z)==bar(z)
    assert bar(x).subs(x,0)==0
    assert (y+bar(x)).subs(x,0)==y

    assert str(bar(bar(x)))=='bar(bar(x))'
    assert str(bar(x)+bar(y))=='bar(x) + bar(y)'
    assert str(bar(x)+x*bar(y))=='bar(x) + x*bar(y)'

    assert str(((bar(x)+bar(y))**2).expand()) in ['2*bar(x)*bar(y) + bar(x)**2 + bar(y)**2',
                                                  'bar(x)**2 + bar(y)**2 + 2*bar(x)*bar(y)']

def test_fun():
    assert str(fun(x))=='fun(x)'
    assert str(fun(0))=='0'
    assert str(fun(x+y))=='fun(x + y)'

    assert fun(x)==fun(x)
    assert fun(x).subs(x,z)==fun(z)
    assert fun(x).subs(x,0)==0
    assert (y+fun(x)).subs(x,0)==y

    assert str(fun(fun(x)))=='fun(fun(x))'
    assert str(fun(x)+fun(y))=='fun(x) + fun(y)'
    assert str(fun(x)+x*fun(y))=='fun(x) + x*fun(y)'

    assert str(((fun(x)+fun(y))**2).expand()) in ['2*fun(x)*fun(y) + fun(x)**2 + fun(y)**2','fun(x)**2 + fun(y)**2 + 2*fun(x)*fun(y)']

def test_foo2():
    assert str(foo2(x,x))=='1'
    assert str(foo2(x,y))=='foo2(x, y)'
    assert str(foo2(x,y).subs(x,z))=='foo2(z, y)'

def test_bar2():
    assert str(bar2(x,y))=='bar2(x, y)'
    assert str(bar2(x,y).subs(x,z))=='bar2(z, y)'
