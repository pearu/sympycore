
from sympy import *
from sympy.core import *

def test_isinstance():
    class A(Basic):
        pass
    class S(Atom):
        pass
    class C(Composite, tuple):
        pass
    class T(BasicFunctionType):
        pass
    a = A()
    s = S()
    c = C((s,s))
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

    assert a.torepr().startswith('<A instance at 0x')==True
    assert a.tostr()==a.torepr()

    assert s.torepr()=='S()'
    # Below is inconsistency with `c=C((s,s))`,
    # one usually needs to redefine __new__() and torepr().
    assert c.torepr()=='C(S(), S())' 

    assert c.atoms()==set([s])
    assert c.atoms(type=S)==set([s])
    assert c.atoms(type=s)==set([s])
    assert c.atoms(type=A)==set()
    assert c.atoms(type=a)==set()

    assert c.has()==True
    assert c.has(s)==True
    assert c.has(s,a)==True
    assert c.has(a)==False
    assert c.has(a,f)==False

    w = BasicWild()
    w2 = BasicWildSymbol(predicate=lambda expr: not isinstance(expr, classes.Atom))
    w3 = BasicWildSymbol(predicate=lambda expr: isinstance(expr,int))
    assert c.has(c)==True
    assert c.has(w)==True
    assert c.has(w2)==True
    assert c.has(w3)==False
    assert c.has(True)==False

    assert c.matches(c)=={}
    assert c.matches(c,{c:c})=={c:c}
    assert s.matches(s)=={}
    assert s.matches(s,{s:s})=={s:s}
    assert c.matches(s,{c:s})=={c:s}
    assert s.matches(c,{s:c})=={s:c}
    assert s.matches(c,{s:s})==None
    assert c.matches(s,{c:c})==None
    assert w.matches(s,{w:s})=={w:s}
    assert w.matches(s,{w:c})==None

    
def xtest_compare():
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

    assert cmp(a, a)==0
    assert cmp(A, A)==0
    assert cmp(T, T)==0
    assert cmp(F, F)==0
    assert cmp(f, f)==0

    assert cmp(a, A)==-cmp(A, a)!=0
    assert cmp(a, T)==-cmp(T, a)!=0
    assert cmp(a, F)==-cmp(F, a)!=0
    assert cmp(a, f)==-cmp(f, a)!=0

    assert cmp(A, Basic)==-cmp(Basic, A)!=0
    assert cmp(A, T)==-cmp(T, A)!=0
    assert cmp(A, F)==-cmp(F, A)!=0
    assert cmp(A, f)==-cmp(f, A)!=0

    assert cmp(T, F)==-cmp(F, T)!=0
    assert cmp(T, f)==-cmp(f, T)!=0

    assert cmp(Callable, Basic)==-cmp(Basic, Callable)!=0
    assert cmp(Number, Basic)==-cmp(Basic, Number)!=0
    assert cmp(Number, Atom)==-cmp(Atom, Number)!=0
    assert cmp(Number, BasicSymbol)==-cmp(BasicSymbol, Number)!=0

    # basic objects are compared via pointers (unless overriding __eq__ method):
    assert cmp(a, a2)==-cmp(a2, a)!=0
    # classes with the same name are equal:
    assert cmp(F, F2)==-cmp(F2, F)==0
    assert cmp(F, G)==-cmp(G, F)!=0
    # function values are equal if arguments are equal:
    assert cmp(f, f2)==-cmp(f2, f)==0 
    assert cmp(g, g2)==-cmp(g2, g)!=0
    assert cmp(g, g3)==-cmp(g3, g)==0
    return
    # comparisons with builtin types and instances:
    assert cmp(a,1)==cmp(a, 1)
    assert cmp(A,1)==cmp(A, 1)
    assert cmp(T,1)==cmp(T, 1)
    assert cmp(F,1)==cmp(F, 1)
    assert cmp(f,1)==cmp(f, 1)

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

    #l = [a,f,1,F,g,{}]
    #l.sort(Basic.static_compare)
    #assert l==[1,f,g,a,{},F]

    assert bool(a)==False
    assert bool(f)==False

    
