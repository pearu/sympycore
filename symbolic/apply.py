"""
Author: Pearu Peterson <pearu.peterson@gmail.com>
Created: January 2007
"""

__all__ = ['Apply']

from base import Symbolic, SymbolicSequence
from base import RelationalMethods, FunctionalMethods, ArithmeticMethods
from types import FunctionType

class Apply(RelationalMethods, FunctionalMethods, ArithmeticMethods,
            SymbolicSequence):
    """
    Apply(<operator>, *<argument-list>, **<kw-argument-dict>)
    """
    def __new__(cls, operator, *args, **kw_args):
        args = map(Symbolic, args)
        for k,v in kw_args.items():
            args.append(Symbolic.Keyword(k,v))
        if isinstance(operator, FunctionType):
            return operator(*args)
        operator = Symbolic(operator)
        if isinstance(operator, Symbolic.Constant):
            assert len(args)==1,`args`
            return operator * args[0]
        return Symbolic.__new__(cls, operator, tuple(args))

    def astuple(self):
        return (self.__class__.__name__, self.coeff)+self.seq

    def eval_power(base, exponent):
        return

    def calc_free_symbols(self):
        r = SymbolicSequence.calc_free_symbols(self)
        if isinstance(self.coeff, Symbolic.DefinedIntegral):
            v = self.coeff.params[0]
            r.remove(v)
        return r
        
    def get_precedence(self): return 70

    def tostr(self, level=0):
        precedence = self.get_precedence()
        args = []
        for a in self.seq:
            args.append(a.tostr())
        s = '%s(%s)' % (self.coeff.tostr(precedence), ', '.join(args))
        if precedence <= level:
            return '(%s)' % (s)
        return s

    def calc_diff(self, *args):
        if not args: return self.calc_diff
        if len(args)>1: return self.calc_diff(args[0]).diff(*args[1:])
        if isinstance(self.coeff, Symbolic.FunctionBase):
            terms = []
            fargs = self.seq
            for i in range(len(fargs)):
                df = self.coeff.derivative(i+1)(*fargs)
                dg = fargs[i].diff(*args)
                terms.append(df * dg)
            return Symbolic.Add(*terms)
        raise NotImplementedError,'%s.calc_diff() needs %s support' \
              % (self.__class__.__name__,self.coeff.__class__.__name__)

    def calc_integrate(self, *args):
        if not args: return self.calc_integrate
        if len(args)>1: return self.calc_integrate(args[0]).integrate(*args[1:])
        a = args[0]
        if isinstance(a, Symbolic.Range):
            v = a.coeff
        else:
            v = a
        fargs = self.seq
        if len(fargs)==1 and v==fargs[0] and isinstance(self.coeff, Symbolic.FunctionBase):
            f = self.coeff.antiderivative(1)(*fargs)
            return f
                
        raise NotImplementedError,'%s.calc_integrate() needs %s support' \
              % (self.__class__.__name__,self.coeff.__class__.__name__)

Symbolic.Apply = Apply
