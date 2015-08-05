from numpy.testing import *

set_package_path()
from symbolic.api import Power, Number, Symbol, Mul, I, Symbolic, Int
restore_path()
Symbolic.interactive = False

class test_Power(NumpyTestCase):

    def check_init(self):
        p = Power('a',2)
        assert isinstance(p, Power)
        assert_equal(repr(p), "Power(Symbol('a'), Integer(2))")

    def check_simple(self):
        a = Symbol('a')
        b = Symbol('b')
        p = a ** b
        assert_equal(repr(p), "Power(Symbol('a'), Symbol('b'))")
        assert_equal(p.base, a)
        assert_equal(p.exponent, b)

    def check_todecimal(self):
        oldprec = Symbolic.set_precision()
        n = Number(2)**Number(1,2)
        Symbolic.set_precision(28)
        assert_equal(n.todecimal().tostr(),'1.414213562373095048801688724')
        Symbolic.set_precision(40)
        assert_equal(n.todecimal().tostr(),'1.41421356237309504880168872420969807857')
        assert_equal((n**2).todecimal().tostr(),'2')
        Symbolic.set_precision(10)
        assert_equal(n.todecimal().tostr(),'1.414213562')
        assert_equal((n**2).todecimal().tostr(),'2')
        Symbolic.set_precision(oldprec)

    def check_evaluate_number_power(self):
        n = Number(2)
        m = Number(3)
        p = Power(n,m)
        r = p
        assert_equal(r,8)
        
    def check_evaluate(self):
        n = Number(2)
        a = Symbol('a')
        assert_equal(Power(a,0),1)
        assert_equal(Power(a,1),a)
        assert_equal(Power(1,a),1)
        assert_equal(Power(0,2),0)
        assert_equal(Power(0,-2),n/0)
        assert_equal(Power(2,Number(3,2)),
                     Mul(2,Power(2,Number(1,2))))
        assert_equal(Power(2,Number(-5,2)),
                     Mul(Number(1,8),Power(2,1/n)))
        assert_equal(Power(4,Number(3,2)).tostr(),
                     '4 * 4 ** (1/2)')
        assert_equal(Power(2,-1),Number(1,2))
        assert_equal(Power(-1,Number(1,2)),I)

    def check_expand(self):
        assert_equal(Symbolic('(a+b)**2').expand().tostr(), 'a ** 2 + b ** 2 + 2 * a * b')
        assert_equal(Symbolic('(a+b)**3').expand().tostr(), 'a ** 3 + b ** 3 + 3 * a * b ** 2 + 3 * b * a ** 2')
        assert_equal(Symbolic('(a+b+c)**2').expand().tostr(), 'a ** 2 + b ** 2 + c ** 2 + 2 * a * b + 2 * a * c + 2 * b * c')
        assert_equal(Symbolic('(a+b+c)**3').expand().tostr(),
                     'a ** 3 + b ** 3 + c ** 3 + 3 * a * b ** 2 + 3 * a * c ** 2 + 3 * b * a ** 2 + 3 * b * c ** 2 + 3 * c * a ** 2 + 3 * c * b ** 2 + 6 * a * b * c')

    def check_dict(self):
        a = Symbol('a')
        p = Power(a,2)
        d = {}
        d[p] = 1
        assert d.has_key(p)
        assert d[p]==1
        assert len(d)==1
        d[p] = 2
        assert len(d)==1
        assert d[p]==2

    def check_hash(self):
        a = Symbol('a')
        p = Power(a,2)
        assert hash(p)==hash(Power(a,Number(2)))

    def check_tostr(self):
        a = Symbol('a')
        p = Power(a,2)
        assert_equal(p.tostr(),'a ** 2')
        assert_equal((a**-2).tostr(),'a ** (-2)')
        assert_equal((2**a).tostr(),'2 ** a')
        assert_equal(((-2)**a).tostr(),'(-2) ** a')
        assert_equal(((-a)**(-a)).tostr(),'(-a) ** (-a)')

        h = Number(1,2)
        assert_equal((h**a).tostr(),'(1/2) ** a')
        assert_equal((h**h).tostr(),'1/2 * 2 ** (1/2)')

    def check_symbols(self):
        a = Symbol('a')
        b = Symbol('b')
        assert_equal((a**b).symbols(),set([a,b]))

    def check_substitute(self):
        a = Symbol('a')
        b = Symbol('b')
        p = Power(a,2)
        assert_equal(p.substitute(a,b).tostr(),'b ** 2')
        assert p.substitute(b,a) is p

    def check_integrate(self):
        a = Symbol('a')
        integrate = Int(a)
        assert_equal(integrate('b**2').tostr(),'a * b ** 2')
        assert_equal(integrate('3*a**2').tostr(),'a ** 3')
        assert_equal(integrate('a**2').tostr(),'1/3 * a ** 3')
        
if __name__ == '__main__':
    NumpyTest().run()
