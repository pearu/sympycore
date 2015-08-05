from numpy.testing import *

set_package_path()
from symbolic.api import Add, Number, Symbol, Symbolic
restore_path()
Symbolic.interactive = False

minf = Number(-1,0)
inf = Number(1,0)
nan = Number(0,0)
zero = Number(0)
one = Number(1)
mone = Number(-1)
half = Number(1,2)
sym = Symbol()
gt1 = Number(3,2)
lt1 = Number(1,4)

class test_Add(NumpyTestCase):

    def check_simple(self):
        a = Symbol('a')
        b = Symbol('b')
        e = Add(a,b)
        assert isinstance(e, Add)

    def check_sum(self):
        a = Symbol('a')
        assert Add(a,-a) is Number(0)
        assert Add(a*a,-a*a) is Number(0)

    def check_tostr(self):
        a = Symbol('a')
        b = Symbol('b')
        c = Symbol('c')
        d = Symbol('d')
        e = Symbol('e')
        assert_equal((a+b).tostr(),'a + b')
        assert_equal((a-b).tostr(),'a - b')
        assert_equal((2+b).tostr(),'2 + b')
        assert_equal((-2+b).tostr(),'-2 + b')
        assert_equal((-2-2*b).tostr(),'-2 - 2 * b')
        assert_equal((2*a+b).tostr(),'b + 2 * a')
        assert_equal((2*(a+b)).tostr(),'2 * a + 2 * b')
        assert_equal((2*(a-b)).tostr(),'2 * a - 2 * b')
        assert_equal((2*a+3*b).tostr(),'2 * a + 3 * b')
        assert_equal((3*a+2*b).tostr(),'2 * b + 3 * a')
        assert_equal((3*a-2*b).tostr(),'- 2 * b + 3 * a')
        assert_equal((-3*a-2*b).tostr(),'- 2 * b - 3 * a')
        assert_equal((a*b+c*d*e).tostr(),'a * b + c * d * e')

    def check_diff(self):
        a = Symbol('a')
        b = Symbol('b')
        assert_equal(((2*a+b).diff(a)).tostr(),'2')

    def check_integrate(self):
        a = Symbol('a')
        b = Symbol('b')
        assert_equal(((a+b).integrate(a)).tostr(),'a * b + 1/2 * a ** 2')
        assert_equal(((a+b).integrate(Symbolic.Range(a,1,3))).tostr(),'4 + 2 * b')

    def check_symbols(self):
        a = Symbol('a')
        b = Symbol('b')
        assert_equal((a+b+2).symbols(),set([a,b]))

    def check_substitute(self):
        a = Symbol('a')
        b = Symbol('b')
        c = Symbol('c')
        s = 2 + a + b
        assert_equal((2+a+b).substitute(b,a).tostr(),'2 + 2 * a')
        assert_equal((2+a+b).substitute(a+b,c).tostr(),'2 + c')
        assert_equal((s).substitute(a+b,5).tostr(),'7')
        assert_equal((s).substitute(a+b+3,c).tostr(),'-1 + c')
        assert_equal((s).substitute(a+1,c).tostr(),'1 + b + c')
        assert s.substitute('d',2) is s

if __name__ == '__main__':
    NumpyTest().run()
