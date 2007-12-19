from ..core import Basic, BasicType, classes, objects, sympify
from ..core.function import (BasicFunctionType, BasicFunction,
                             FunctionSignature, BasicLambda,
                             Callable)
from .basic import BasicArithmetic

__all__ = ['OperatorType', 'Operator']

class OperatorType(BasicArithmetic, BasicFunctionType):
    """ Metaclass for Operator class.
    """

class Operator(BasicArithmetic, BasicFunction):
    """ Base class for operators that can be used in arithmetic
    operations as operants.

    Operator differs from Function by the fact that Operator values
    are unevaluated functions.

    The default constructor takes 2-tuple arguments of Basic objects
    or Basic objects that are mapped to Tuple(<obj>,1):
    
      Operator(x, (y, 2)) -> Operator((x, 1), (y, 2))

    If two 2-tuple arguments have equal first element then
    the second elements are added:

      Operator(x, (x, 3)) -> Operator((x,4))

    The above behavior is appropiate for differential and integral
    operators:

      FD(1, 2, (1, 3)) -> FD((1,4),(2,1))  - 5-th order partial
        differentation operator 4 times with respect to first
        argument and 1 time with respect to the second argument.
        
      D(x, y, (x, 3)) - D((x,4), (y,1)) - 5-th order partial
        differentation operator 4 times with respect x
        and 1 time with respect to y.

    """
    __metaclass__ = OperatorType

    def __new__(cls, *args, **options):
        if not options.get('is_canonical', False):
            args = map(sympify, args)
            l = []
            d = {}
            # assuming that the order of applying operators
            # with respect to different variables is insignificant:
            for a in args:
                if isinstance(a, classes.Tuple):
                    i = a[0]
                    r = a[1:]
                else:
                    i = a
                    r = ()
                if i not in d:
                    l.append(i)
                    d[i] = cls.compose_arg_tuples(r)
                else:
                    d[i] = cls.compose_arg_tuples(d[i], r)
            args = [classes.Tuple(*((i,)+d[i])) for i in l]
        return BasicFunction.__new__(cls, *args, **options)

    @staticmethod
    def compose_arg_tuples(r1, r2=None):
        """ Method used to parse Operator arguments.

        The method mth=Operator.compose_arg_tuples is called
        in the following situations:
        Operator(x) -> Operator(z) where z=(x,)+mth(())
        """
        if r2 is None:
            return (r1,)
        return r1 + (r2,)
