from numpy.testing import *

set_package_path()
from symbolic.api import Mul, Number, Symbol, Symbolic
restore_path()
Symbolic.interactive = False

class test_Mul(NumpyTestCase):

    def check_simple(self):
        a = Symbol('a')
        b = Symbol('b')
        e = Mul(a,b)
        assert isinstance(e, Mul)
        assert_equal(e.tostr(), 'a * b')
        assert_equal((e**2).tostr(), 'a ** 2 * b ** 2')

    def check_equal(self):
        a = Symbol('a')
        b = Symbol('b')
        e = Mul(a,b)
        assert e-e is Number(0)

    def check_tostr(self):
        a = Symbol('a')
        b = Symbol('b')
        assert_equal((a*b).tostr(),'a * b')
        assert_equal((2*a).tostr(),'2 * a')
        assert_equal((-2*a).tostr(),'-2 * a')
        assert_equal((-a).tostr(),'-a')
        assert_equal((2*a/3).tostr(),'2/3 * a')
        assert_equal((-2*a/3).tostr(),'-2/3 * a')
        assert_equal((2*a**2).tostr(),'2 * a ** 2')
        assert_equal((2*2**a).tostr(),'2 * 2 ** a')
        assert_equal((2*(-2)**a).tostr(),'2 * (-2) ** a')
        assert_equal((2*a*b).tostr(),'2 * a * b')
        assert_equal((2/a).tostr(),'2 * a ** (-1)')

        assert_equal((a**2*b**2).tostr(),'a ** 2 * b ** 2')
        assert_equal((a**3*b**2).tostr(),'b ** 2 * a ** 3')
        assert_equal((a**3*b**-2).tostr(),'b ** (-2) * a ** 3')

    def check_expand(self):
        a = Symbol('a')
        b = Symbol('b')
        c = Symbol('c')
        assert_equal((a*(b+c)).tostr(),'a * (b + c)')
        assert_equal(Symbolic('a*(f(x)+g(x))').expand().tostr(),'a * f(x) + a * g(x)')
        assert_equal(Symbolic('(a+b)*(c+d)').expand().tostr(), 'a * c + a * d + b * c + b * d')

    def check_free_symbols(self):
        a = Symbol('a')
        b = Symbol('b')
        c = Symbol('c')
        assert_equal(Symbolic('a*b').free_symbols(),set([a,b]))
        assert_equal(Symbolic('a(b)*c(b)').free_symbols(),set([b]))

    def check_integrate(self):
        a = Symbol('a')
        assert_equal(((3*a).integrate()).tostr(),'3 * a')
        assert_equal(((3*a).integrate(a)).tostr(),'3/2 * a ** 2')
        assert_equal(((3*a).integrate(Symbolic.Range(a,1,5))).tostr(),'36')

    def check_symbols(self):
        a = Symbol('a')
        b = Symbol('b')
        assert_equal((a*b*2).symbols(),set([a,b]))

    def check_substitute(self):
        a = Symbol('a')
        b = Symbol('b')
        c = Symbol('c')
        t = 2*a*b
        assert_equal(t.substitute(b,a).tostr(),'2 * a ** 2')
        assert_equal(t.substitute(a*b,c).tostr(),'2 * c')
        assert t.substitute('d',2) is t
        
if __name__ == '__main__':
    NumpyTest().run()
