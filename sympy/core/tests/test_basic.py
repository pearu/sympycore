
from sympy import *
from sympy.core import *

def test_isinstance():
    class A(Basic):
        pass
    class T(BasicFunctionType):
        pass
    a = A()
    F = T('F')
    f = F()

    assert isinstance(a, Basic)
    assert not isinstance(a, BasicType)

    assert not isinstance(A, Basic)
    assert isinstance(A, BasicType)

    assert not isinstance(T, Basic)
    assert isinstance(T, BasicType)
    
    assert isinstance(F, Basic)
    assert isinstance(F, BasicType)

    assert isinstance(f, Basic)
    assert not isinstance(f, BasicType)

def test_compare():
    class A(Basic):
        pass
    class T(BasicFunctionType):
        pass
    a = A()
    a2 = A()
    F = T('F')
    F2 = T('F')
    G = T('G')
    f = F()
    f2 = F()
    g = F(a)
    g2 = F(a2)
    g3 = F(a)

    assert a.compare(a)==0
    assert A.compare(A)==0
    assert T.compare(T)==0
    assert F.compare(F)==0
    assert f.compare(f)==0

    assert a.compare(A)==-A.compare(a)!=0
    assert a.compare(T)==-T.compare(a)!=0
    assert a.compare(F)==-F.compare(a)!=0
    assert a.compare(f)==-f.compare(a)!=0

    assert A.compare(T)==-T.compare(A)!=0
    assert A.compare(F)==-F.compare(A)!=0
    assert A.compare(f)==-f.compare(A)!=0

    assert T.compare(F)==-F.compare(T)!=0
    assert T.compare(f)==-f.compare(T)!=0

    # basic objects are compared via pointers (unless overriding __eq__ method):
    assert a.compare(a2)==-a2.compare(a)!=0
    # classes with the same name are equal:
    assert F.compare(F2)==-F2.compare(F)==0
    assert F.compare(G)==-G.compare(F)!=0
    # function values are equal if arguments are equal:
    assert f.compare(f2)==-f2.compare(f)==0 
    assert g.compare(g2)==-g2.compare(g)!=0
    assert g.compare(g3)==-g3.compare(g)==0

    # comparisons with builtin types and instances:
    assert cmp(a,1)==a.compare(1)
    assert cmp(A,1)==A.compare(1)
    assert cmp(T,1)==T.compare(1)
    assert cmp(F,1)==F.compare(1)
    assert cmp(f,1)==f.compare(1)

    assert cmp(a,int)==a.compare(int)
    assert cmp(A,int)==A.compare(int)
    assert cmp(T,int)==T.compare(int)
    assert cmp(F,int)==F.compare(int)
    assert cmp(f,int)==f.compare(int)

    assert cmp(a,type)==a.compare(type)
    assert cmp(A,type)==A.compare(type)
    assert cmp(T,type)==T.compare(type)
    assert cmp(F,type)==F.compare(type)
    assert cmp(f,type)==f.compare(type)

    assert cmp(a,object)==a.compare(object)
    assert cmp(A,object)==A.compare(object)
    assert cmp(T,object)==T.compare(object)
    assert cmp(F,object)==F.compare(object)
    assert cmp(f,object)==f.compare(object)

    assert cmp(a,{})==a.compare({})
    assert cmp(A,{})==A.compare({})
    assert cmp(T,{})==T.compare({})
    assert cmp(F,{})==F.compare({})
    assert cmp(f,{})==f.compare({})

    assert cmp(a,[])==a.compare([])
    assert cmp(A,[])==A.compare([])
    assert cmp(T,[])==T.compare([])
    assert cmp(F,[])==F.compare([])
    assert cmp(f,[])==f.compare([])
