from ..core import Basic, Atom, BasicType, BasicWild, classes, objects
from ..core.function import (BasicFunctionType, BasicFunction,
                             FunctionSignature, BasicLambda,
                             Callable)
from .basic import BasicArithmetic

__all__ = ['D']

class OperatorType(BasicArithmetic, BasicFunctionType):
    """ Metaclass for Operator class.
    """

class Operator(BasicArithmetic, BasicFunction):
    """ Base class for operators that can be used in arithmetic
    operations as operants.

    Operator differs from Function by the fact that Operator values
    are unevaluated functions.
    """
    __metaclass__ = OperatorType


#class FDerivative(Function):
#    """ Represents derivative function of an unevaluated function.
#    """

class D(Operator):
    """

    D(index) - 1st derivative with respect to index-th argument
    D((index, n)) - n-th derivative with respect to index-th argument
    D((index1,n1), (index2,n2), ..) - partial derivatives
    """

    @classmethod
    def canonize(cls, args):
        l = []
        d = {}
        for a in args:
            if a.is_Tuple:
                i, n = a
            else:
                i = a
                n = objects.one
            if i in d:
                d[i] += n
            else:
                l.append(i)
                d[i] = n
        new_args = [classes.Tuple(i, d[i]) for i in l]
        return cls(*new_args, **dict(is_canonical=True))

    def __call__(self, func):
        f = func
        unevaluated = []
        for index, n in self:
            if index.is_Integer and n.is_Integer:
                assert n>0,`index,n`
                for i in range(n):
                    f = f.fdiff(index)
            else:
                unevaluated.append(index, n)
        if not unevaluated:
            return f
        return FDerivative(f, *unevaluated)
