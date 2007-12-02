
from types import ClassType

from ..core import Basic, Atom, BasicType, BasicWild, classes, objects
from ..core.function import (BasicFunctionType, BasicFunction,
                             FunctionSignature, BasicLambda,
                             Callable)
from ..core.utils import UniversalMethod
from .methods import ArithmeticMethods
from .basic import BasicArithmetic

__all__ = ['FunctionType', 'Function', 'Lambda', 'FunctionSymbol',
           'WildFunctionType', 'ArithmeticFunction']

class FunctionType(BasicArithmetic, BasicFunctionType):

    pass

class Function(BasicArithmetic, BasicFunction):

    __metaclass__ = FunctionType

    def try_derivative(self, s):
        i = 0
        l = []
        r = objects.zero
        args = self.args
        for a in args:
            i += 1
            da = a.diff(s)
            if da.is_zero:
                continue
            df = self.func.fdiff(i)
            l.append(df(*args) * da)
        return classes.Add(*l)

    @UniversalMethod
    def fdiff(obj, index=1):
        if isinstance(obj, BasicType):
            return FunctionType('%s_%s' % (obj.__name__, index), Function,
                                dict(signature=obj.signature), is_global=False)
        return obj._fdiff(index)

    def _fdiff(self, index=1):
        # handles: sin(cos).fdiff() -> sin'(cos) * cos' -> cos(cos) * sin
        i = 0
        l = []
        for a in self.args:
            i += 1
            df = self.func.fdiff(i)(*self.args)
            da = a.fdiff(index)
            l.append(df * da)
        return classes.Add(*l)


class Lambda(BasicArithmetic, BasicLambda):

    pass

class WildFunctionType(BasicWild, FunctionType):
    # Todo: derive WildFunctionType from DummyFunctionType.
    def __new__(typ, name=None, bases=None, attrdict=None, is_global=None, predicate=None):
        if name is None:
            name = 'WF'
        func = FunctionType.__new__(typ, name, bases, attrdict, is_global)
        if predicate is not None:
            func.predicate = staticmethod(predicate)
        return func


class ArithmeticFunction(Function):
    """ Base class for Add and Mul classes.
    
    Important notes:
    - Add and Mul implement their own __new__ methods.
    - Add and Mul do not implement canonize() method but are
      subclasses of Function. Canonization is carried out
      by the TermCoeffDict and BaseExpDict classes, respectively.
    - Instances of Add and Mul are created in .as_Basic()
      methods of TermCoeffDict and BaseExpDict, respectively.
    - One should not subclass from Add and Mul classes (does this still holds?).
    - Add and Mul instances have the following attributes:
       * ._dict_content - holds TermCoeffDict or BaseExpDict instance
       * .args - equals to _dict_content.args_flattened
       * .args_sorted - use .get_args_sorted() for initializing
       * .args_frozenset - use .get_args_frozenset() for initializing
       * BaseExpDict instances have additional attribute .coeff such
         that <BaseExpDict instance>[coeff] == 1
         and coeff.is_Number == True
    """

    ordered_arguments = False
    
    signature = FunctionSignature([BasicArithmetic],(BasicArithmetic,))

    def __eq__(self, other):
        if self.__class__ is other.__class__:
            return dict.__eq__(self._dict_content, other._dict_content)
        if isinstance(other, Basic):
            return False
        if isinstance(other, str):
            return self==sympify(other)
        return False

    def count_ops(self, symbolic=True):
        n = len(self.args)
        if symbolic:
            counter = (n-1) * self.func
        else:
            counter = n-1
        for a in self.args:
            counter += a.count_ops(symbolic=symbolic)
        return counter
