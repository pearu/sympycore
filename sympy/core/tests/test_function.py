from sympy import *

def test_defined_function():

    class Func(BasicFunction):
        
        signature = FunctionSignature((Basic, Basic), Basic)

        @classmethod
        def canonize(cls, (x,y)):
            if x==y:
                return x
            return

    assert hasattr(Basic,'Func')==True
    assert Func.is_Func==False
    assert Func.is_Callable==True
    assert Func.is_BasicFunctionType==True

    x = BasicSymbol('x')
    y = BasicSymbol('y')

    f = Func(x,y)
    assert f.is_Func==True
    assert f.is_Callable==False
    f = Func(x,x)
    assert f.is_Func==False
    assert f.is_BasicSymbol==True

def test_symbol_function():

    Foo = BasicFunctionType('Foo')
    assert hasattr(Basic,'Foo')==False
    assert Foo.is_Callable==True
    assert Foo.is_BasicFunctionType==True
    assert Foo.is_BasicFunction==False
    
    x = BasicSymbol('x')
    y = BasicSymbol('y')
    f = Foo(x, y)

    assert f.is_Callable==False
    assert f.is_BasicFunction==True

def test_defined_symbol_function():

    class Bar(BasicFunction):
        
        signature = FunctionSignature((Basic, Basic), int)

        @classmethod
        def canonize(cls, (x,y)):
            if x==y:
                return x
            return

        def mth(self):
            return 2
    
    Foo = BasicFunctionType('Foo', Bar)

    x = BasicSymbol('x')
    y = BasicSymbol('y')

    assert Foo(x,y).mth()==2
    
def test_lambda():
    x = BasicSymbol('x')
    y = BasicSymbol('y')
    assert BasicLambda(x, x)(y) == y
    # verify that bound and unbound variables don't get mixed up on evaluation
    assert BasicLambda((x, y), x)(y, x) == y
    assert BasicLambda((x, y), y)(x, y) == y
    assert BasicLambda((x, y), x)(x, y) == x
    assert BasicLambda((x, y), y)(y, x) == x
