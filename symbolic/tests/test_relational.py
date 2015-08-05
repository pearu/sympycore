from numpy.testing import *

set_package_path()
from symbolic.api import Keyword, Equal, NotEqual, Less, LessEqual, Number, Symbol, Mul, Power, Symbolic
restore_path()
Symbolic.interactive = False

class test_Equal(NumpyTestCase):

    def check_init(self):
        a = Symbol('a')
        b = Symbol('b')
        e = a==b
        assert isinstance(e, Equal)
        #assert not bool(e),`bool(e)`

    def check_invert(self):
        a = Symbol('a')
        b = Symbol('b')
        e = a==b
        assert isinstance(e, Equal)
        assert_equal((~ e).tostr(), 'a != b')

    def check_equal(self):
        a = Symbol('a')
        b = Symbol('b')
        p = (1+Mul(a,2))*b
        p2 = b+Mul(a,2)*b
        assert_equal(p, p2)

    def check_tostr(self):
        a = Symbol('a')
        b = Symbol('b')
        c = Symbol('c')
        assert_equal((a < b).tostr(),'a < b')
        assert_equal((b > a).tostr(),'a < b')
        ## Don't use the following:!!
        #assert_equal(((a < b) < c).tostr(),'(a < b) < c')
        #assert_equal(((a < b) > c).tostr(),'c < (a < b)')

    def check_substitute(self):
        a = Symbol('a')
        b = Symbol('b')
        e = a==b
        assert_equal(e.substitute(a,2).tostr(),'2 == b')
        assert_equal(e.substitute(b,2).tostr(),'a == 2')
        assert e.substitute('c',2) is e

class test_NotEqual(NumpyTestCase):

    def check_invert(self):
        a = Symbol('a')
        b = Symbol('b')
        e = a!=b
        assert isinstance(e, NotEqual)
        assert_equal((~ e).tostr(), 'a == b')

class test_Less(NumpyTestCase):

    def check_init(self):
        a = Symbol('a')
        b = Symbol('b')
        e = a<b
        assert isinstance(e, Less)
        
    def check_substitute(self):
        a = Symbol('a')
        b = Symbol('b')
        e = a<b
        assert_equal(e.substitute(a,2).tostr(),'2 < b')
        assert_equal(e.substitute(b,2).tostr(),'a < 2')
        assert e.substitute('c',2) is e

    def check_invert(self):
        a = Symbol('a')
        b = Symbol('b')
        e = a<b
        assert isinstance(e, Less)
        assert_equal((~ e).tostr(), 'b <= a')

class test_Greater(NumpyTestCase):

    def check_invert(self):
        a = Symbol('a')
        b = Symbol('b')
        e = a>b
        assert isinstance(e, Less)
        assert_equal((~ e).tostr(), 'a <= b')

class test_LessEqual(NumpyTestCase):

    def check_invert(self):
        a = Symbol('a')
        b = Symbol('b')
        e = a<=b
        assert isinstance(e, LessEqual)
        assert_equal((~ e).tostr(), 'b < a')

class test_GreaterEqual(NumpyTestCase):

    def check_invert(self):
        a = Symbol('a')
        b = Symbol('b')
        e = a>=b
        assert isinstance(e, LessEqual)
        assert_equal((~ e).tostr(), 'a < b')

class test_Keyword(NumpyTestCase):

    def check_init(self):
        a = Symbol('a')
        b = Symbol('b')
        e = Keyword(a,b)
        assert isinstance(e, Keyword)

    def check_tostr(self):
        a = Symbol('a')
        b = Symbol('b')
        e = Keyword(a,b)
        assert_equal(e.tostr(),'a = b')

if __name__ == '__main__':
    NumpyTest().run()
