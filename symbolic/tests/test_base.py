
from numpy.testing import *

set_package_path()
from symbolic.base import AttributeHolder
from symbolic.api import Symbolic
restore_path()
Symbolic.interactive = False

class test_AttributeHolder(NumpyTestCase):

    def check_get(self):
        a = AttributeHolder(a='hey')
        assert a.a=='hey'

    def check_get_disallowed_attribute(self):
        a = AttributeHolder(a='hey')
        try:
            a.b
            raise AssertionError
        except AttributeError, msg:
            assert_equal(str(msg),"AttributeHolder instance has no attribute 'b', expected attributes: a")

    def check_set(self):
        a = AttributeHolder(a='hey')
        assert a.a=='hey'
        a.a = 'hoi'
        assert a.a=='hoi'

    def check_set_disallowed_attribute(self):
        a = AttributeHolder(a='hey')
        try:
            a.b = 'tere'
            raise AssertionError
        except AttributeError, msg:
            assert_equal(str(msg),"AttributeHolder instance has no attribute 'b', expected attributes: a")

    def check_callable(self):
        f = lambda :2
        a = AttributeHolder(a='hey',f=f)
        assert a.a=='hey'
        assert a.f==2
        try:
            a.f = 3
            raise AssertionError
        except AttributeError, msg:
            assert_equal(str(msg),"AttributeHolder instance attribute 'f' is readonly")

    def check_set(self):
        a = Symbolic('a')
        b = Symbolic('b')
        c = Symbolic('c')
        x = Symbolic('x')
        
        s = Symbolic('a * b(a)').free_symbols()
        assert a in s,`s,a`
        assert c not in s,`s,c`

        m = Symbolic('f(x) * g(x)')
        assert x in m.free_symbols()
        for t in m.seq:
            assert x in t.free_symbols()

    def check_diff(self):
        assert_equal(Symbolic('f(x)').diff('x').tostr(),'D[1](f)(x)')
        assert_equal(Symbolic('2*f(x)').diff('x').tostr(),'2 * D[1](f)(x)')
        assert_equal(Symbolic('2*f(x)').diff('x').diff('x').tostr(),'2 * D[1, 1](f)(x)')
        assert_equal(Symbolic('f(x)+g(x)').diff('x').tostr(),'D[1](f)(x) + D[1](g)(x)')

class test_Range(NumpyTestCase):

    def check_simpel(self):
        assert_equal(Symbolic.Range('x','1','y+1').tostr(),'x = (1, 1 + y)')
        assert isinstance(Symbolic.Range('x'), Symbolic.Symbol)

        try:
            r = Symbolic.Range('x',1,'x')
        except ValueError, msg:
            assert_equal(str(msg), 'Range() boundary contains variable symbol')
        else:
            raise AssertionError, 'expected ValueError on %r' % (r.tostr())

        try:
            r = Symbolic.Range('x+1',1,'y')
        except TypeError, msg:
            assert_equal(str(msg), 'Range() 1st argument must be Symbol object but got Add object')
        else:
            raise AssertionError, 'expected TypeError on %r' % (r.tostr())

    def check_free_symbols(self):
        r = Symbolic.Range('x','a','b')
        assert_equal(r.free_symbols(),set(map(Symbolic,['a','b'])))
        
if __name__=='__main__':
    NumpyTest().run()
