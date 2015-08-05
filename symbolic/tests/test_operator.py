"""
Author: Pearu Peterson <pearu.peterson@gmail.com>
Created: January 2007
"""
from numpy.testing import *

set_package_path()
from symbolic.api import Symbolic
restore_path()
Symbolic.interactive = False

Diff = Symbolic.Differential
Int = Symbolic.Integral
Lambda = Symbolic.Lambda

class test_Lambda(NumpyTestCase):

    def check_simple(self):
        f = Lambda('x1','2*x1')
        assert_equal(f.torepr(),"Lambda(DummySymbol('x1'), Mul(Integer(2), DummySymbol('x1')))")
        assert_equal(f.tostr(),'lambda x1_: 2 * x1_')
        assert_equal(f('a').tostr(),'2 * a')
        assert_equal(f('3*a').tostr(),'6 * a')
        assert_equal(f.derivative(1).tostr(),'lambda x1_: 2')
        assert_equal(f.derivative(1).derivative(1).tostr(),'lambda x1_: 0')
        assert_equal(f.antiderivative(1).tostr(),'lambda x1_: x1_ ** 2')

    def check_correctness(self):
        f = Lambda('x','2*x')
        assert_equal((f+'x').tostr(),'lambda x_: x + 2 * x_')

    def check_add(self):
        f = Lambda('x','2*x')
        g = Lambda('y','y**2')
        a = f+g
        assert_equal(a.tostr(),'lambda x_: x_ ** 2 + 2 * x_')
        h = Lambda('z,w','3*z*w')
        try:
            result = h+f
        except ValueError, msg:
            assert_equal(str(msg),'cannot operate lambda functions with different number of arguments: expected 2 but got 1')
        else:
            raise AssertionError,'expected ValueError but got %r' % (result)
        p1 = Lambda('x,y','x**y')
        p2 = Lambda('y,z','y**z')

        p = p1+p2
        assert_equal(p.tostr(), 'lambda x_, y_: 2 * x_ ** y_')

        e = Symbolic('(lambda x:x)+1')
        assert_equal(e.tostr(),'lambda x_: 1 + x_')

        e = Symbolic('(lambda x:x)-(lambda y:3*y)')
        assert_equal(e.tostr(),'lambda x_: -2 * x_')
        
    def check_mul(self):
        f = Lambda('x','2*x')
        g = Lambda('y','y**2')
        a = f*g
        assert_equal(a.tostr(),'lambda x_: 2 * x_ ** 3')

        p1 = Lambda('x,y','x**y')
        p2 = Lambda('y,z','y**z')
        p = p1*p2
        assert_equal(p.tostr(), 'lambda x_, y_: x_ ** (2 * y_)')

    def check_power(self):
        f = Lambda('x','2*x')
        g = Lambda('y','y**2')
        a = f**g
        assert_equal(a.tostr(),'lambda x_: (2 * x_) ** (x_ ** 2)')

        p1 = Lambda('x,y','x**y')
        p2 = Lambda('y,z','y**z')
        p = p1**p2
        assert_equal(p.tostr(), 'lambda x_, y_: (x_ ** y_) ** (x_ ** y_)')

    def check_neg(self):
        f = Lambda('x','2*x')
        assert_equal((-f).tostr(),'lambda x_: -2 * x_')

    def check_pos(self):
        f = Lambda('x','2*x')
        assert_equal((+f).tostr(),'lambda x_: 2 * x_')

    def check_tilde(self):
        f = Lambda('x','x')
        assert_equal((~f).tostr(),'lambda x_: ~x_')

    def check_and(self):
        f = Lambda('x','x')
        g = Lambda('y','y')
        h = Lambda('y','~y')
        assert_equal((f & g).tostr(),'lambda x_: x_')
        assert_equal((f & h).tostr(),'lambda x_: FALSE')

        f = Lambda('x,y','x')
        g = Lambda('x,y','y')
        assert_equal((f & g).tostr(),'lambda x_, y_: x_ & y_')

    def check_or(self):
        f = Lambda('x','x')
        g = Lambda('y','y')
        h = Lambda('y','~y')
        assert_equal((f | g).tostr(),'lambda x_: x_')
        assert_equal((f | h).tostr(),'lambda x_: TRUE')

        f = Lambda('x,y','x')
        g = Lambda('x,y','y')
        assert_equal((f | g).tostr(),'lambda x_, y_: x_ | y_')

    def check_xor(self):
        f = Lambda('x','x')
        g = Lambda('y','y')
        h = Lambda('y','~y')
        assert_equal((f ^ g).tostr(),'lambda x_: FALSE')
        assert_equal((f ^ h).tostr(),'lambda x_: TRUE')

        f = Lambda('x,y','x')
        g = Lambda('x,y','y')
        assert_equal((f ^ g).tostr(),'lambda x_, y_: x_ ^ y_')

    def check_equiv(self):
        f = Lambda('x,y','x')
        g = Lambda('x,y','y')
        assert_equal((f.equiv(g)).tostr(),'lambda x_, y_: ~(x_ ^ y_)')

    def check_implies(self):
        f = Lambda('x,y','x')
        g = Lambda('x,y','y')
        assert_equal((f.implies(g)).tostr(),'lambda x_, y_: y_ | ~x_')
        

class test_Diff(NumpyTestCase):

    def check_simple(self):
        assert_equal(Diff('x')('a').tostr(),'0')
        assert_equal(Diff('x')('2/3').tostr(),'0')
        assert_equal(Diff('x')('x').tostr(),'1')
        assert_equal(Diff('x')('x*y').tostr(),'y')
        assert_equal(Diff('x')('x**2').tostr(),'2 * x')
        assert_equal(Diff('x')('2**x').tostr(),'ln(2) * 2 ** x')
        assert_equal(Diff('x')('E**x').tostr(),'E ** x')
        
    def check_general(self):
        print 'Fix %s.check_general()' % (self.__class__.__name__)
        return
        assert_equal(Diff('x')('f(x)').tostr(),'D[1](f)(x)')
        assert_equal(Diff('x')('f(x)+g(x)').tostr(),'D[1](f)(x) + D[1](g)(x)')
        assert_equal(Diff('x')('f(x)*g(x)').tostr(),'f(x) * D[1](g)(x) + g(x) * D[1](f)(x)')
        assert_equal(Diff('x')('f(g(x))').tostr(),'D[1](f)(g(x)) * D[1](g)(x)')

    def check_ofdiff(self):
        print 'Fix %s.check_ofdiff()' % (self.__class__.__name__)
        return
        assert_equal(Symbolic('Diff(y)(Diff(x)(y*f(x)))').tostr(),'D[1](f)(x)')
        assert_equal(Symbolic('Diff(y)(Diff(x)(g(y)*f(x)))').tostr(),'D[1](f)(x) * D[1](g)(y)')

    def check_substitute(self):
        D = Diff('x')
        assert_equal(D.substitute('x','y').tostr(),'Diff(y)')
        assert D.substitute('y','z') is D

class test_Int(NumpyTestCase):

    def check_simple(self):
        a = Symbolic.Symbol('a')
        assert_equal((Int(a)(Symbolic('2*b'))).tostr(),'2 * a * b')
        assert_equal((Int(a)(Symbolic('2*a'))).tostr(),'a ** 2')
        assert_equal((Int(a)(Symbolic('3*a'))).tostr(),'3/2 * a ** 2')
        assert_equal((Int(a)(3*a)).tostr(),'3/2 * a ** 2')
        assert_equal((Int('x')(Symbolic('f(x)*g(x)'))).tostr(),'Int(x)(f(x) * g(x))')

    def check_general(self):
        print 'Fix %s.check_general()' % (self.__class__.__name__)
        return
        assert_equal(Symbolic('f(x)').integrate('x').tostr(),'D[-1](f)(x)')

        assert_equal(Symbolic('f(x, y)').integrate('x').integrate('y').tostr(),'D[-2, -1](f)(x, y)')        

        assert_equal(Symbolic('f(x)+g(x)').integrate('x').tostr(),'D[-1](f)(x) + D[-1](g)(x)')
        assert_equal(Symbolic('2*f(x)').integrate('x').tostr(),'2 * D[-1](f)(x)')
        assert_equal(Symbolic('n*f(x)').integrate('x').tostr(),'n * D[-1](f)(x)')
        assert_equal(Symbolic('f(x)*g(x)').integrate('x').tostr(),'Int(x)(f(x) * g(x))')
        assert_equal(Symbolic('2*f(x)*g(x)').integrate('x').tostr(),'2 * Int(x)(f(x) * g(x))')

        assert_equal(Symbolic('f(x)').integrate('y').tostr(),'y * f(x)')
        assert_equal(Symbolic('f(x)*g(y)').integrate('y').tostr(),'f(x) * D[-1](g)(y)')
        assert_equal(Symbolic('f(x)*g(y)').integrate('x','y').tostr(),'D[-1](f)(x) * D[-1](g)(y)')

        assert_equal(Symbolic('4*x*y').integrate('y','x').tostr(),'x ** 2 * y ** 2')

        assert_equal(Symbolic('f(x)*g(x)').integrate('x','y').tostr(),'y * Int(x)(f(x) * g(x))')

        
        assert_equal(Symbolic('(f(x)*(g(x)+1))').expand().integrate('x').tostr(),
                     'D[-1](f)(x) + Int(x)(f(x) * g(x))')

    def check_substitute(self):
        integrate = Int('x')
        assert_equal(integrate.substitute('x','y').tostr(),'Int(y)')
        assert integrate.substitute('y','z') is integrate

        integrate = Int('x','a','b')
        assert_equal(integrate.substitute('x','y').tostr(),'Int(y, a, b)')
        assert integrate.substitute('y','z') is integrate
        assert_equal(integrate.substitute('a','c').tostr(),'Int(x, c, b)')
        assert_equal(integrate.substitute('b','c').tostr(),'Int(x, a, c)')


class test_SymbolicFunctionGenerator(NumpyTestCase):

    def check_simple(self):
        D = Symbolic('D')
        assert isinstance(D,Symbolic.SymbolicFunctionGenerator),`type(d)`
        assert isinstance(Symbolic('D[1]'), type(lambda : None))
        assert_equal(Symbolic('D[1](f)').tostr(),'D[1](f)')
        assert_equal(Symbolic('D[1,2](f)').tostr(),'D[1, 2](f)')
        assert_equal(Symbolic('D[2,1](f)(x, y)').tostr(),'D[1, 2](f)(x, y)')

class test_SymbolicFunction(NumpyTestCase):

    def check_simple(self):
        assert isinstance(Symbolic('f(x)'), Symbolic.Apply)
        assert isinstance(Symbolic('f(x)').coeff, Symbolic.UndefinedFunction)
        assert_equal(Symbolic('f(x)').tostr(),'f(x)')

    def check_sum(self):
        assert_equal(Symbolic('(f+g)(x)').tostr(),'f(x) + g(x)')
        assert_equal(Symbolic('(2+f)(x)').tostr(),'f(x) + 2 * x')

    def check_mul(self):
        assert_equal(Symbolic('(2*f)(x)').tostr(),'2 * f(x)')
        assert_equal(Symbolic('(g*f)(x)').tostr(),'g(f(x))')

    def check_substitute(self):
        e = Symbolic('f(x)')
        assert_equal(e.substitute('x','a').tostr(),'f(a)')
        assert_equal(e.substitute('f','g').tostr(),'g(x)')
        assert e.substitute('g','h') is e
        assert_equal(e.substitute('f','g+h').tostr(),'(g + h)(x)')


if __name__ == '__main__':
    NumpyTest().run()
