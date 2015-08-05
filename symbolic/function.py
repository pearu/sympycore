"""
Author: Pearu Peterson <pearu.peterson@gmail.com>
Created: January 2007
"""

__all__ = ['Log','Ln','Exp','Sin','Cos','Sqrt','UndefinedFunction']

from base import Symbolic, Constant, ArithmeticMethods, BooleanMethods
from symbol import Symbol
from number import ngcd
from operator import SymbolicOperator
from singleton import Singleton

class FunctionBase(ArithmeticMethods, Symbolic):

    ############################################################################
    #
    # Informational methods
    #
    
    def get_nofargs(self):
        raise NotImplementedError,'%s must defined get_nofargs() method' \
              % (self.__class__.__name__)

    def get_dummy_symbols(self):
        return tuple([Symbolic.DummySymbol('x%s' % (i+1)) for i in range(self.get_nofargs())])

    def get_expression(self):
        return self(*self.get_dummy_symbols())

    def __call__(self, *args):
        return Symbolic.Apply(self, *args)

class UndefinedFunction(FunctionBase):

    ###########################################################################
    #
    # Constructor methods
    #

    def __new__(cls, label, *derivative_indices):
        """
        UndefinedFunction('f',(i,j)) represents a (i+j)-th
        partial derivative of a function `f` with respect the 1st and
        2nd arguments.
        """
        label = Symbolic(label)
        derivative_indices = map(Symbolic, derivative_indices)
        return Symbolic.__new__(cls, label, derivative_indices)

    def init(self, label, derivative_indices):
        self.label = label
        self.derivative_indices = tuple(derivative_indices)
        return

    def astuple(self):
        return (self.__class__.__name__, self.label) +  self.derivative_indices

    ############################################################################
    #
    # Informational methods
    #

    def get_precedence(self): return 72

    def get_nofargs(self):
        return len(self.derivative_indices)

    ###########################################################################
    #
    # Transformation methods
    #

    def tostr(self, level=0):

        args = self.get_dummy_symbols()
        l = []
        for i in range(self.get_nofargs()):
            di = self.derivative_indices[i]
            if isinstance(di, Symbolic.Zero):
                continue
            l.append(args[i] ** di)
        precedence = self.get_precedence()
        if l:
            r = '%s[%s]' % (self.label.tostr(precedence), ', '.join([s.tostr() for s in l]))
        else:
            r = self.label.tostr()
        if precedence <= level:
            return '(%s)' % r
        return r

    def expand(self):
        return self

    def derivative(self, index=1):
        assert 1<=index<=self.get_nofargs(),`index`
        i = self.derivative_indices
        return self.__class__(self.label, i[:index-1]+(i[index-1]+1,)+i[index:])

    def antiderivative(self, index=1):
        assert 1<=index<=self.get_nofargs(),`index`
        i = self.derivative_indices
        return self.__class__(self.label, i[:index-1]+(i[index-1]-1,)+i[index:])

#
# End of UndefinedFunction class
#
################################################################################


class DefinedFunction(FunctionBase):

    pass

#
# End of DefinedFunction class
#
################################################################################


class SingletonDefinedFunction(DefinedFunction, Singleton):

    def get_precedence(self): return 1

    def tostr(self, level=0):
        return self.__class__.__name__.lower()

    def __call__(self, *args):
        return Symbolic.Apply(self, *args)

#
# End of SingletonDefinedFunction class
#
################################################################################

class Lambda(DefinedFunction):
    """ Represents anonymous functions.
    
        Lambda(arg_1, .., arg_n, <expression with arg_i>)
        Lambda(<expression>), arguments are found as free_symbols.
    """

    ###########################################################################
    #
    # Constructor methods
    #

    def __new__(cls, *args):
        if len(args)==1:
            d = Symbolic_namespace = {}
            expr = Symbolic(args[0])
            dymmy_args = d.keys()
        else:
            dummy_args = []
            for a in args[:-1]:
                if isinstance(a, Symbolic):
                    dummy_args.append(a)
                elif ',' in a:
                    dummy_args += map(Symbolic.Symbol,a.split(','))
                else:
                    dummy_args.append(Symbolic.Symbol(a))
            d = Symbolic_namespace = {}
            for a in dummy_args:
                d[a.label] = a
            expr = Symbolic(args[-1])
        lst = []
        for a in dummy_args:
            if isinstance(a, Symbolic.DummySymbol):
                lst.append(a)
                continue
            dummy_a = Symbolic.DummySymbol(a)
            expr = expr.substitute(a, dummy_a)
            lst.append(dummy_a)
        dummy_args = lst
        obj = Symbolic.__new__(cls, dummy_args, expr)
        return obj

    def init(self, args, expr):
        self.args = tuple(args)
        self.expr = expr
        return

    def astuple(self):
        return (self.__class__.__name__,) + self.args + (self.expr,)

    ############################################################################
    #
    # Informational methods
    #

    def get_precedence(self): return 1
    def get_nofargs(self): return len(self.args)
    def get_dummy_symbols(self): return self.args
    def get_expression(self): return self.expr

    ###########################################################################
    #
    # Transformation methods
    #

    def tostr(self, level=0):
        precedence = self.get_precedence()
        r = 'lambda %s: %s' % (', '.join([a.tostr() for a in self.args]),
                               self.expr.tostr(precedence))
        if precedence <= level:
            return '(%s)' % r
        return r

    ############################################################################
    #
    # Functional methods
    #

    def __call__(self, *args):
        if len(args) != len(self.args):
            raise ValueError,'%s object expected %s arguments but got %s' \
                  % (len(self.args), len(args))
        args = map(Symbolic, args)
        expr = self.expr
        for (dummy_arg, arg) in zip(self.args, args):
            expr = expr.substitute(dummy_arg, arg)
        return expr

    def derivative(self, arg_index):
        assert isinstance(arg_index, int),`arg_index`
        if not (1<= arg_index <= len(self.args)):
            raise ValueError,'.derivative() argument must be in interval [1, %s] but got %r' \
                  (len(self.args), arg_index)
        return self.__class__(*(self.args + (self.expr.diff(self.args[arg_index-1]),)))

    def antiderivative(self, arg_index):
        assert isinstance(arg_index, int),`arg_index`
        if not (1<= arg_index <= len(self.args)):
            raise ValueError,'.antiderivative() argument must be in interval [1, %s] but got %r' \
                  (len(self.args), arg_index)
        return self.__class__(*(self.args + (self.expr.integrate(self.args[arg_index-1]),)))

#
# End of Lambda class
#
################################################################################

class Ln(SingletonDefinedFunction):

    def get_nofargs(self): return 1
    

    def __call__(self, *args):
        """
        ln(E**n) -> n
        ln(-m) -> ln(m) + Pi * I 
        ln(p) -> n * ln(m), where p=m**n
        """
        if len(args)!=1:
            raise TypeError,'ln() takes exactly one argument (%s given)' % (len(args))
        x = Symbolic(args[0])
        if isinstance(x, Symbolic.Exp1):
            return Symbolic.One()
        if isinstance(x, Symbolic.NegativeOne):
            return Symbolic.Pi() * Symbolic.ImaginaryUnit()
        if isinstance(x, Symbolic.Power):
            if isinstance(x.base, Symbolic.Exp1) \
               and isinstance(x.exponent, Symbolic.Number):
                return x.exponent
        if isinstance(x, Symbolic.Number) and x.is_negative():
            return Symbolic.Pi() * Symbolic.ImaginaryUnit() + self(-x)
        if isinstance(x, Symbolic.Integer):
            factors = x.flags.factors
            ce = ngcd(*factors.values())
            if ce != 1:
                n = 1
                for b,e in factors.items():
                    n *= b ** (e/ce)
                return ce * self(n)
        return Symbolic.Apply(self, x)
        return SymbolicOperator.__call__(self, x)

    def derivative(self, index=1):
        assert index==1,`index`
        x = self.get_dummy_symbols()[0]
        return Lambda(x, x**Symbolic.NegativeOne())

    def antiderivative(self, index=1):
        assert index==1,`index`
        x = self.get_dummy_symbols()[0]
        print x,Lambda(x, x*Ln()(x)-x)('y')
        return Lambda(x, x*Ln()(x)-x)

class Log(SingletonDefinedFunction):

    label = 'log'

    def get_nofargs(self): return 1

    def __call__(self, *args):
        """
        ln(E**n) -> n
        """
        if len(args) not in [1,2]:
            raise TypeError,'log() takes one or two arguments (%s given)' % (len(args))
        x = Symbolic(args[0])
        if len(args)==2: base=args[1]
        else: base = 'E'
        ln = Ln()
        if base=='E': return ln(x)
        return ln(x)/ln(base)


class Exp(SingletonDefinedFunction):

    def get_nofargs(self): return 1

    def derivative(self, index=1):
        assert index==1,`index`
        return self

    def antiderivative(self, index=1):
        assert index==1,`index`
        return self

class Sin(SingletonDefinedFunction):


    def get_nofargs(self): return 1

    def derivative(self, index=1):
        assert index==1,`index`
        return Cos()

    def __call__(self, *args):
        """
        sin(-x) -> -sin(x)
        """
        if len(args)!=1:
            raise TypeError,'sin() takes exactly one argument (%s given)' % (len(args))
        x = Symbolic(args[0])
        if isinstance(x, Symbolic.Number) and x.is_negative():
            return -self(-x)
        if isinstance(x, Symbolic.Mul) and x.coeff.is_negative():
            return -self(-x)
        return Symbolic.Apply(self, x)
        return super(self.__class__, self).__call__(x)        


class Cos(SingletonDefinedFunction):

    def get_nofargs(self): return 1

    def __call__(self, *args):
        """
        cos(-x) -> cos(x)
        """
        if len(args)!=1:
            raise TypeError,'cos() takes exactly one argument (%s given)' % (len(args))
        x = Symbolic(args[0])
        if isinstance(x, Symbolic.Number) and x.is_negative():
            return self(-x)
        if isinstance(x, Symbolic.Mul) and x.coeff<0:
            return self(-x)
        return Symbolic.Apply(self, x)
        return super(self.__class__, self).__call__(x)        

    def derivative(self, index=1):
        assert index==1,`index`
        x = self.get_dummy_symbols()[0]
        return Lambda(x,-Sin()(x))

class Sqrt(SingletonDefinedFunction):

    label = 'sqrt'

    def __call__(self, *args):
        """
        sqrt(n*x) -> sqrt(n) * sqrt(x) where n>0
        """
        if len(args)!=1:
            raise TypeError,'cos() takes exactly one argument (%s given)' % (len(args))
        x = Symbolic(args[0])
        if isinstance(x, Symbolic.Number):
            if isinstance(x, Symbolic.NegativeOne):
                return Symbolic.ImaginaryUnit()
            if x.is_negative():
                return Symbolic.ImaginaryUnit() * self(-x)
        if isinstance(x, Symbolic.Mul) and not isinstance(x.coeff, Symbolic.One) and x.coeff.is_positive():
            return self(x.coeff) * self(Symbolic.Mul(*x.seq))
        return Symbolic.Apply(self, x)


    def derivative(self, index=1):
        assert index==1,`index`
        x = self.get_dummy_symbols()[0]
        return Lambda(x,Symbolic.Half()/self(x))

    def antiderivative(self, index=1):
        assert index==1,`index`
        return lambda x: Symbolic.Rational(2,3)*x*Sqrt()(x)


Symbolic.singleton_classes['ln'] = Ln
Symbolic.Ln = Ln
Symbolic.singleton_classes['log'] = Log
Symbolic.Log = Log
Symbolic.singleton_classes['exp'] = Exp
Symbolic.Exp = Exp
Symbolic.singleton_classes['sin'] = Sin
Symbolic.Sin = Sin
Symbolic.singleton_classes['cos'] = Cos
Symbolic.Cos = Cos
Symbolic.singleton_classes['sqrt'] = Sqrt
Symbolic.Sqrt = Sqrt

Symbolic.FunctionBase = FunctionBase
Symbolic.UndefinedFunction = UndefinedFunction
Symbolic.DefinedFunction = DefinedFunction
Symbolic.SingletonDefinedFunction = SingletonDefinedFunction
Symbolic.Lambda = Lambda

#EOF

