
from ..core import Basic
from ..core.function import BasicFunctionType, BasicFunction, FunctionSignature, BasicLambda
from .methods import ArithmeticMethods

__all__ = ['FunctionClass', 'Function', 'Lambda']

class FunctionType(ArithmeticMethods, BasicFunctionType):

    pass

class Function(ArithmeticMethods, BasicFunction):

    __metaclass__ = FunctionType

    def __new__(cls, *args, **options):
        if cls.__name__.endswith('Function'):
            if cls is Function and len(args)==1:
                # Default function signature is of SingleValuedFunction
                # that provides basic arithmetic methods.
                cls = UndefinedFunction
            return cls.__metaclass__(cls, *args)
        return BasicFunction.__new__(cls, *args, **options)

class UndefinedFunction(Function):

    signature = FunctionSignature(None, (Basic,))

    def fdiff(cls, index=1):
        return UndefinedFunction('%s_%s' % (cls.__name__, index), cls.signature)


class Lambda(BasicLambda, FunctionType):
    pass
