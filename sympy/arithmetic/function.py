
from types import ClassType

from ..core import Basic, Atom, BasicType, BasicWild, classes, objects
from ..core.function import (BasicFunctionType, BasicFunction,
                             FunctionSignature, BasicLambda,
                             Callable)
from ..core.utils import UniversalMethod
from .methods import ArithmeticMethods
from .basic import BasicArithmetic

__all__ = ['FunctionType', 'Function', 'Lambda', 'FunctionSymbol', 'WildFunctionType']

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
