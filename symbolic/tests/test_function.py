"""
Author: Pearu Peterson <pearu.peterson@gmail.com>
Created: January 2007
"""
from numpy.testing import *

set_package_path()
from symbolic.api import Exp, Ln, Log, Sin, Cos, Symbolic, UndefinedFunction
restore_path()
Symbolic.interactive = False

class test_UndefinedFunction(NumpyTestCase):

    def check_simple(self):
        f = UndefinedFunction('f',0)
        assert_equal(f.tostr(),'f')

        f = UndefinedFunction('f',0,2,0,3)
        assert_equal(f.tostr(),'f[x2_ ** 2, x4_ ** 3]')


class test_Ln(NumpyTestCase):

    def check_simple(self):
        ln = Ln()
        assert isinstance(ln, Ln)
        assert_equal(ln('x').tostr(),'ln(x)')
        assert_equal(ln('E').tostr(),'1')
        assert_equal(ln('E**2').tostr(),'2')
        assert_equal(ln('E**-3').tostr(),'-3')
        assert_equal(ln('2').tostr(),'ln(2)')
        assert_equal(ln('-2').tostr(),'ln(2) + I * Pi')
        assert_equal(ln('2**4 * 3 ** 2').tostr(),'2 * ln(12)')
        assert_equal(ln('-1').tostr(),'I * Pi')

    def check_derivative(self):
        ln = Ln()
        assert isinstance(ln, Ln)
        assert_equal(ln('x').diff('x').tostr(),'x ** (-1)')
        assert_equal(ln('x').diff('x','x').tostr(),'-x ** (-2)')

    def check_primitive(self):
        ln = Ln()
        assert isinstance(ln, Ln)
        assert_equal(ln('x').integrate('x').tostr(),'- x + x * ln(x)')
        assert_equal(ln('2*x').integrate('x').tostr(),'- x + x * ln(2 * x)')

    def check_substitute(self):
        ln = Ln()
        e = ln('x')
        assert_equal(e.substitute('x','y').tostr(),'ln(y)')
        assert e.substitute('y','z') is e
        assert_equal(e.substitute('x','y+1').tostr(),'ln(1 + y)')
        assert_equal(e.substitute('ln','exp').tostr(),'exp(x)')
        assert_equal(e.substitute('ln','f+g').tostr(),'(f + g)(x)')

class test_Log(NumpyTestCase):

    def check_simple(self):
        log = Log()
        assert isinstance(log, Log)
        assert_equal(log('x').tostr(),'ln(x)')
        assert_equal(log('x',2).tostr(),'ln(x) * ln(2) ** (-1)')
        assert_equal(log(2,2).tostr(),'1')
        assert_equal(log('2**4',2).tostr(),'4')
        assert_equal(log('E**-3').tostr(),'-3')

    def check_derivative(self):
        log = Log()
        assert isinstance(log, Log)
        assert_equal(log('x').diff('x').tostr(),'x ** (-1)')
        assert_equal(log('x',3).diff('x').tostr(),'x ** (-1) * ln(3) ** (-1)')

class test_Exp(NumpyTestCase):

    def check_simple(self):
        exp = Exp()
        assert isinstance(exp, Exp)
        assert_equal(exp('x').tostr(),'exp(x)')

    def check_derivative(self):
        exp = Exp()
        assert isinstance(exp, Exp)
        assert_equal(exp('x').diff('x').tostr(),'exp(x)')
        assert_equal(exp('n*x').diff('x').tostr(),'n * exp(n * x)')

class test_Sin(NumpyTestCase):

    def check_simple(self):
        sin = Sin()
        assert isinstance(sin, Sin)
        assert_equal(sin('x').tostr(),'sin(x)')
        assert_equal(sin('-x').tostr(),'-sin(x)')
        assert_equal(sin('-2').tostr(),'-sin(2)')

    def check_derivative(self):
        sin = Sin()
        assert isinstance(sin, Sin)
        assert_equal(sin('x').diff('x').tostr(),'cos(x)')
        assert_equal(sin('a*x').diff('x').tostr(),'a * cos(a * x)')


class test_Cos(NumpyTestCase):

    def check_simple(self):
        cos = Cos()
        assert isinstance(cos, Cos)
        assert_equal(cos('x').tostr(),'cos(x)')
        assert_equal(cos('-x').tostr(),'cos(x)')
        assert_equal(cos('-2').tostr(),'cos(2)')

    def check_derivative(self):
        cos = Cos()
        assert isinstance(cos, Cos)
        assert_equal(cos('x').diff('x').tostr(),'-sin(x)')
        assert_equal(cos('a*x').diff('x').tostr(),'-a * sin(a * x)')

if __name__ == '__main__':
    NumpyTest().run()
