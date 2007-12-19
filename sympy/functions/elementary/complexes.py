
from ...core import Basic, FunctionSignature, classes, objects
from ...arithmetic import Function

__all__ = ['Abs', 'Arg', 'Re', 'Im']


class Abs(Function):
    signature = FunctionSignature([(Basic,)], (Basic,))

    @classmethod
    def canonize(cls, (arg,)):
        if isinstance(arg, classes.Number):
            return abs(arg)
        if isinstance(arg, classes.NaN) or isinstance(arg, classes.Infinity) or arg.is_positive:
            return arg
        term, coeff = arg.as_term_coeff()
        if not coeff.is_one:
            return cls(coeff) * cls(term)

class Arg(Function):
    """ The principal value of the argument of a complex-valued expression.
    
    -Pi < Arg(x) <= Pi
    x == Abs(x) * Exp(Arg(x)*I)
    if x>=0 then Arg(x)=0, if x<0 then Arg(x)=Pi
    """

    signature = FunctionSignature([(Basic,)], (Basic,))

    @classmethod
    def canonize(cls, (arg,)):
        if isinstance(arg, classes.Number):
            if arg < 0:
                return objects.pi
            return objects.zero
        return

class Re(Function):

    signature = FunctionSignature([(Basic,)], (Basic,))

    @classmethod
    def canonize(cls, (arg,)):
        if isinstance(arg, classes.Number):
            return arg
        return

class Im(Function):

    signature = FunctionSignature([(Basic,)], (Basic,))

    @classmethod
    def canonize(cls, (arg,)):
        if isinstance(arg, classes.Number):
            return objects.zero
        return
