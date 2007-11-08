
from sympy.core.utils import *

def test_get_object_by_name():
    a = 1
    assert get_object_by_name('a')==1
    def foo():
        a = 2
        return get_object_by_name('a')
    assert foo()==2
    def foo():
        r = get_object_by_name('a')
        return r
    assert foo()==1

    def foo():
        return get_object_by_name('a',3)
    assert foo()==1

    def foo():
        return get_object_by_name('_a',3)
    assert foo()==3

    def foo():
        return get_object_by_name('_a',4)
    assert foo()==4

    def foo():
        l = dir()
        r = get_object_by_name('a',3)
        l1 = dir()
        return r,l,set(l1)
    assert foo()==(1,[],set(['a','r','l']))

    def foo():
        l = dir()
        r = get_object_by_name('a')
        l1 = dir()
        return r,l,set(l1)
    assert foo()==(1,[],set(['l','r','a']))

    def foo():
        def bar():
            return get_object_by_name('_b',4)
        r = bar()
        r2 = get_object_by_name('_b',5)
        return r,r2
    assert foo()==(4,5)
    assert get_object_by_name('_b',6)==6

    def foo():
        _c = 7
        def bar():
            return get_object_by_name('_c',4)
        r = bar()
        r2 = get_object_by_name('_c',5)
        return r,r2
    assert foo()==(7,7)
    assert get_object_by_name('_c',8)==8

def test_UniversalMethod():
    class AType(type):
        pass
    class A(object):    
        __metaclass__ = AType
        @UniversalMethod
        def foo(self_or_cls):
            return self_or_cls.__class__.__name__

    assert A.foo()=='AType'
    assert A().foo()=='A'
    
    class AType(type):
        pass
    class B:
        __metaclass__ = AType
        @UniversalMethod
        def foo(self_or_cls):
            return self_or_cls.__class__.__name__

    assert B.foo()=='AType'
    assert B().foo()=='B'

    class C(object):
        @UniversalMethod
        def foo(self_or_cls):
            return self_or_cls.__class__.__name__

    assert C.foo()=='type'
    assert C().foo()=='C'

    class C:
        @UniversalMethod
        def foo(self_or_cls):
            return type(self_or_cls).__name__

    assert C.foo()=='classobj'
    assert C().foo()=='instance'

def test_DualMethod():
    class AType(type):
        def foo(cls):
            return 'AType.foo'

    class A(object):
        __metaclass__ = AType
        @DualMethod
        def foo(self):
            return 'A.foo'

    assert A.foo() == 'AType.foo'
    assert A().foo() == 'A.foo'

    class B:
        __metaclass__ = AType
        @DualMethod
        def foo(self):
            return 'B.foo'

    assert B.foo() == 'AType.foo'
    assert B().foo() == 'B.foo'

    class C(object):
        @DualMethod
        def foo(self):
            return 'C.foo'

    assert C().foo() == 'C.foo'
    try:
        C.foo()
    except AttributeError,msg:
        assert str(msg)=="type object 'type' has no attribute 'foo'"
    else:
        assert 0,'Expected AttributeError'

def test_DualProperty():
    class AType(type):
        @property
        def foo(cls):
            return 'AType.foo'

    class A(object):
        __metaclass__ = AType
        @DualProperty
        def foo(self):
            return 'A.foo'

    assert A.foo == 'AType.foo'
    assert A().foo == 'A.foo'
    
    class B(object):
        __metaclass__ = AType
        def foo(self):
            return 'B.foo'
        foo = DualProperty(foo, lambda cls:cls.__name__+' HEY')

        def bar(self):
            return 'B.bar'
        bar = DualProperty(bar, lambda cls:cls.__name__+' HEY')

    assert B.foo == 'AType.foo'
    assert B().foo == 'B.foo'

    assert B.bar == 'B HEY'
    assert B().bar == 'B.bar'

    class CType(type):
        foo = 'CType.foo'

    class C(object):
        __metaclass__ = CType
        @DualProperty
        def foo(self):
            return 'C.foo'

    assert C.foo=='CType.foo'
    assert C().foo=='C.foo'
