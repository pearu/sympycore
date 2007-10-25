
from ..core import Basic
from ..core.symbol import BasicSymbol, BasicDummySymbol, BasicWildSymbol
from .methods import ArithmeticMethods

__all__ = ['Symbol', 'Dummy', 'Wild']

class Symbol(ArithmeticMethods, BasicSymbol):

    """ Represents a symbol.

    Symbol('x', dummy=True) returns a unique Symbol instance.
    """

    def __call__(self, *args):
        signature = Basic.FunctionSignature((Basic,)*len(args), (Basic,))
        return Basic.UndefinedFunction(self, signature)(*args)

    def as_dummy(self):
        return Dummy(self.name)

    def try_derivative(self, s):
        if self==s:
            return Basic.one
        return Basic.zero

    def fdiff(self, index=1):
        return Basic.zero

class Dummy(BasicDummySymbol, Symbol):
    """ Dummy Symbol.
    """

class Wild(BasicWildSymbol, Symbol):
    """
    Wild() matches any expression but another Wild().
    """
