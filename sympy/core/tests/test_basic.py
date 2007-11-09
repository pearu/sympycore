
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
    w2 = BasicWildSymbol(predicate=lambda expr: not expr.is_Atom)
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

    assert A.compare(Basic)==-Basic.compare(A)!=0
    assert A.compare(T)==-T.compare(A)!=0
    assert A.compare(F)==-F.compare(A)!=0
    assert A.compare(f)==-f.compare(A)!=0

    assert T.compare(F)==-F.compare(T)!=0
    assert T.compare(f)==-f.compare(T)!=0

    assert Callable.compare(Basic)==-Basic.compare(Callable)!=0
    assert Number.compare(Basic)==-Basic.compare(Number)!=0
    assert Number.compare(Atom)==-Atom.compare(Number)!=0
    assert Number.compare(BasicSymbol)==-BasicSymbol.compare(Number)!=0

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

    l = [a,f,1,F,g,{}]
    l.sort(Basic.static_compare)
    assert l==[1,f,g,a,F,{}]

    assert bool(a)==False
    assert bool(f)==False

    
