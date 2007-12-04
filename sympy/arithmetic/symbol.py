
from ..core import Basic, classes, objects
from ..core.symbol import BasicSymbol, BasicDummySymbol, BasicWildSymbol
from .basic import BasicArithmetic

__all__ = ['Symbol', 'Dummy', 'Wild']

class Symbol(BasicArithmetic, BasicSymbol):
    """ Represents a symbol.

    Symbol('x', dummy=True) returns a unique Symbol instance.
    """

    def __call__(self, *args):
        signature = classes.FunctionSignature((Basic,)*len(args), (Basic,))
        return classes.FunctionType(str(self), attrdict=dict(signature=signature))(*args)

    def try_derivative(self, s):
        if self==s:
            return objects.one
        return objects.zero

class Dummy(BasicDummySymbol, Symbol):
    """ Dummy symbol.
    """

class Wild(BasicWildSymbol, Symbol):
    """ Wild symbol.
    """

BasicArithmetic._symbol_cls = Symbol
