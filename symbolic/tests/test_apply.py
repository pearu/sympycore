"""
Author: Pearu Peterson <pearu.peterson@gmail.com>
Created: January 2007
"""
from numpy.testing import *

set_package_path()
from symbolic.api import Exp, Ln, Log, Sin, Cos, Symbolic
restore_path()
Symbolic.interactive = False

Diff = Symbolic.Differential
Int = Symbolic.Integral

class test_Apply(NumpyTestCase):

    def check_simple(self):
        assert isinstance(Symbolic('f( x)'), Symbolic.Apply)
        assert_equal(Symbolic('f(  x)').tostr(),'f(x)')

    def check_derivative(self):
        assert_equal(Symbolic('f(  x)').diff('x').tostr(),'D[1](f)(x)')

    def check_integral(self):
        assert_equal(Symbolic('f(  x)').integrate('x').tostr(),'D[-1](f)(x)')
        assert_equal(Symbolic('f(  x)').integrate(Symbolic.Range('x',1,2)).tostr(),'Int(x, 1, 2)(f(x))')

    def check_symbols(self):
        a = Symbolic('a')
        b = Symbolic('b')
        f = Symbolic('f')
        assert_equal((f(a,b)).symbols(),set([f,a,b]))

    def check_free_symbols(self):
        a = Symbolic('a')
        b = Symbolic('b')
        f = Symbolic('f')
        x = Symbolic('x')
        e = f(x)
        assert_equal(e.free_symbols(),set([x]))
        assert_equal(e.integrate('x').free_symbols(),set([Symbolic('x')]))
        i = e.integrate(Symbolic.Range('x',a,b))
        assert_equal(i.free_symbols(), set([a,b]))

    def check_substitute(self):
        f = Symbolic('f')
        x = Symbolic('x')
        a = Symbolic('a')
        e = f(x)
        assert_equal(e.substitute(x,a).tostr(),'f(a)')
        assert e.substitute(a,2) is e
        
if __name__ == '__main__':
    NumpyTest().run()
