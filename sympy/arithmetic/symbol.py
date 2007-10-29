
from ..core import Basic
from ..core.symbol import BasicSymbol, BasicDummySymbol, BasicWildSymbol
from .basic import BasicArithmetic

__all__ = ['Symbol', 'Dummy', 'Wild']

class Symbol(BasicArithmetic, BasicSymbol):

    """ Represents a symbol.

    Symbol('x', dummy=True) returns a unique Symbol instance.
    """

    def __call__(self, *args):
        signature = Basic.FunctionSignature((Basic,)*len(args), (Basic,))
        return Basic.FunctionType(str(self), attrdict=dict(signature=signature))(*args)

    def as_dummy(self):
        return Dummy(self.name)

    def try_derivative(self, s):
        if self==s:
            return Basic.one
        return Basic.zero

class Dummy(BasicDummySymbol, Symbol):
    """ Dummy Symbol.
    """

class Wild(BasicWildSymbol, Symbol):
    """
    Wild() matches any expression but another Wild().
    """
