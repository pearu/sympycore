
from types import ClassType

from ..core import Basic, Atom
from ..core.function import (BasicFunctionType, BasicFunction,
                             FunctionSignature, BasicLambda,
                             Callable)
from .methods import ArithmeticMethods

__all__ = ['FunctionType', 'Function', 'Lambda', 'FunctionSymbol']

class FunctionType(ArithmeticMethods, BasicFunctionType):

    pass

class Function(ArithmeticMethods, BasicFunction):

    __metaclass__ = FunctionType

class Lambda(ArithmeticMethods, BasicLambda):
    pass
