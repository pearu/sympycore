
from sympycore import *
#from sympy.core.methods import *

def xtest_mutable():
    a = BasicSymbol('a')
    b = BasicSymbol('b')
    c = BasicSymbol('c')
    s1 = MutableCompositeDict({a:c,c:b})
    s2 = MutableCompositeDict({b:b})
    s3 = MutableCompositeDict({a:c,c:b})

    assert s1.torepr()=='MutableCompositeDict({a: c, c: b})'
    assert s2.torepr()=='MutableCompositeDict({b: b})'
    assert s3.torepr()=='MutableCompositeDict({a: c, c: b})'
    
    assert s1.compare(s2)==1
    assert s2.compare(s1)==-1
    assert s2.compare(s2)==0

    assert s1==s3
    assert s1==s1
    assert s1!=s2
    assert s1!=a
    assert s1!=1
    
    assert s1.replace(s1,s2)==s2
    assert s1.replace(s2,s1)==s1
    assert s1.replace(c,c)==s1
