from sympy import *

def test_defined_function():

    class Func(BasicFunction):
        
        signature = FunctionSignature((Basic, Basic), Basic)

        @classmethod
        def canonize(cls, (x,y)):
            if x==y:
                return x
            return

    assert hasattr(classes,'Func')==True
    assert isinstance(Func, classes.Func)==False
    assert isinstance(Func, classes.BasicFunctionType)==True

    x = BasicSymbol('x')
    y = BasicSymbol('y')

    f = Func(x,y)
    assert isinstance(f, classes.Func)==True
    assert isinstance(f, classes.BasicFunctionType)==False
    f = Func(x,x)
    assert isinstance(f, classes.Func)==False
    assert isinstance(f, classes.BasicSymbol)==True

def test_symbol_function():

    Foo = BasicFunctionType('Foo')
    assert hasattr(classes,'Foo')==False
    assert isinstance(Foo, classes.BasicFunctionType)==True
    assert isinstance(Foo, classes.BasicFunction)==False
    
    x = BasicSymbol('x')
    y = BasicSymbol('y')
    f = Foo(x, y)

    assert isinstance(f, classes.BasicFunctionType)==False
    assert isinstance(f, classes.BasicFunction)==True

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

def test_signature():
    s = FunctionSignature(None, None)
    assert s.validate('test',())==None
    assert s.validate('test',(1,2))==None
    assert repr(s)=='FunctionSignature(None, None)'

    s = FunctionSignature((object,), (object,))
    assert s.validate('test',(1,))==None
    assert s.validate('test',(1,2))=='function test: wrong number of arguments, expected 1, got 2'
    assert s.validate('test',())=='function test: wrong number of arguments, expected 1, got 0'
    assert s.validate_return('test',(1,))==None
    assert s.validate_return('test',(1,2))=='function test: wrong number of returns, expected 1, got 2'
    assert s.validate_return('test',())=='function test: wrong number of returns, expected 1, got 0'
    assert repr(s)=="FunctionSignature((<type 'object'>,), (<type 'object'>,))"

    s = FunctionSignature(object, None)
    assert s.validate('test',(1,))==None
    assert s.validate('test',({},))==None
    assert s.validate('test',(1,2))=='function test: wrong number of arguments, expected 1, got 2'
    assert s.validate('test',())=='function test: wrong number of arguments, expected 1, got 0'
    
    s = FunctionSignature((int,), None)
    assert s.validate('test',(1,))==None
    assert s.validate('test',(1,2))=='function test: wrong number of arguments, expected 1, got 2'
    assert s.validate('test',({},))=="function test: wrong argument[1] type 'dict', expected 'int'"

    s = FunctionSignature(((int,list),), None)
    assert s.validate('test',(1,))==None
    assert s.validate('test',([],))==None
    assert s.validate('test',(1,2))=='function test: wrong number of arguments, expected 1, got 2'
    assert s.validate('test',({},))=="function test: wrong argument[1] type 'dict', expected 'int|list'"
    assert repr(s)=="FunctionSignature(((<type 'int'>, <type 'list'>),), None)"

    s = FunctionSignature([int], [int])
    assert s.validate('test',(1,))==None
    assert s.validate('test',(1,2))==None
    assert s.validate('test',())==None
    assert s.validate('test',(1,{},2))=="function test: wrong argument[2] type 'dict', expected 'int'"
    assert s.validate_return('test',(1,))==None
    assert s.validate_return('test',(1,2))==None
    assert s.validate_return('test',())==None
    assert s.validate_return('test',(1,{},2))=="function test: wrong return[2] type 'dict', expected 'int'"

    s = FunctionSignature([int,list], [int])
    assert s.validate('test',(1,))==None
    assert s.validate('test',(1,[]))==None
    assert s.validate('test',(1,()))=="function test: wrong argument[2] type 'tuple', expected 'int|list'"
    assert repr(s)=="FunctionSignature([(<type 'int'>, <type 'list'>)], [(<type 'int'>,)])"

    try:
        FunctionSignature({}, None)
    except TypeError, msg:
        assert str(msg)=='FunctionSignature: wrong argument[1] type dict, expected NoneType|tuple|list|type'
    else:
        assert 0,'exprected TypeError on `FunctionSignature({}, None)`'

def test_basic_function():
    f = BasicFunction(1,2)
    f2 = BasicFunction(1,2)
    f3 = BasicFunction(1,2,3)
    g = BasicFunction(1,3)

    class F(BasicFunction):
        pass

    h = F(1,2)

    assert f.args==(1,2)
    assert f.func==BasicFunction
    assert f[:] == (1,2)
    assert len(f)==2
    assert f==f
    assert f==f2
    assert f!=f3
    assert f!=g
    assert f!=1
    assert f!=True
    assert f!=False
    assert f!=h

    assert f.replace(2,3)!=f
    assert f.replace(2,3)==g
    assert f.replace(f,g)==g
    assert f.replace(BasicFunction, F)==h
    assert f.replace(f3,h)==f
    assert f.replace(f2,h)==h

    assert BasicFunction.torepr()=="<class 'sympy.core.function.BasicFunction'>"
    assert BasicFunction.tostr()=='BasicFunction'

    assert F.torepr()=="<class 'test_function.F'>"
    assert F.tostr()=='F'

    assert f.tostr()=='BasicFunction(1, 2)'
    assert f.torepr()=='BasicFunction(Integer(1), Integer(2))'

    assert h.tostr()=='F(1, 2)'
    assert h.torepr()=='F(Integer(1), Integer(2))'

    assert f!='x'

    x = BasicSymbol('x')
    assert BasicLambda((x,),F(x))==F
    assert issubclass(BasicLambda((x,),F(x,x)), classes.BasicLambda)==True

    assert bool(f)==False
    assert bool(F)==False
    assert F!=1
    assert F!='x'
    assert F!=False
    assert F!=True
    assert F==F
    assert F!=BasicFunction

    k = F(F)
    assert k.tostr()=='F(F)'
    assert k.torepr()=="F(<class 'test_function.F'>)"
    assert k(x)==F(F(x))
    assert k(x).tostr()=='F(F(x))'

    assert F.atoms()==set([F])
    assert F.atoms(type=BasicFunctionType)==set([F])
    assert F.atoms(type=Basic)==set([F])
    assert F.atoms(type=BasicFunction)==set([])
    assert k.atoms()==set([F])


def test_instancemethod():
    import types
    d = {}
    for n,cls in classes.iterNameValue():
        if not isinstance(cls, type):
            continue
        if issubclass(cls, BasicFunction):
            for k,v in cls.__dict__.iteritems():
                if v.__class__.__name__.startswith('InstanceClassMethod'):
                    try:
                        d[k].append(n)
                    except KeyError:
                        d[k] = [n]
                elif isinstance(v, classmethod):
                    pass
                    #print k,type(v)
    for n,cls in classes.iterNameValue():
        if not isinstance(cls, type):
            continue
        if issubclass(cls, BasicFunction):
            for k,v in cls.__dict__.iteritems():
                if isinstance(v, (types.FunctionType, classmethod)):
                    if k in d:
                        print
                        print '%s.%s needs instancemethod wrapper as is used in %s' % (n,k, ', '.join(d[k]))
