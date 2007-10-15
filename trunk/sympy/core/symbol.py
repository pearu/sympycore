
from utils import memoizer_immutable_args, memoizer_Symbol_new
from basic import Atom, Basic, sympify
from methods import ArithMeths

class BasicSymbol(Atom, str):

    _dummy_count = 0
    is_dummy = False

    def __new__(cls, name, dummy=False, **options):
        # when changing the Symbol signature then change memoizer_Symbol_new
        # accordingly    
        assert isinstance(name, str), `name`
        if dummy:
            return str.__new__(cls, name).as_dummy()
        return str.__new__(cls, name)

    @property
    def name(self): return str.__str__(self)

    def torepr(self):
        return '%s(%r)' % (self.__class__.__name__, self.name)

    def tostr(self, level=0):
        return self.name

    def __eq__(self, other):
        if isinstance(other, Basic):
            if other.is_Dummy: return False
        return str.__eq__(self, other)            

    __hash__ = str.__hash__

class BasicDummySymbol(BasicSymbol):

    def __new__(cls, name):
        BasicSymbol._dummy_count += 1
        obj = str.__new__(cls, name)
        obj.dummy_index = BasicSymbol._dummy_count        
        return obj    

    def torepr(self):
        return '%s(%r)' % (self.__class__.__name__, self.name)

    def tostr(self, level=0):
        return '_' + self.name

    def __eq__(self, other):
        return self is other


class Symbol(ArithMeths, BasicSymbol):

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


class Wild(Dummy):
    """
    Wild() matches any expression but another Wild().
    """

    def __new__(cls, name=None, exclude=None):
        if name is None:
            name = 'W%s' % (Symbol._dummy_count+1)
        obj = Dummy.__new__(cls, name)
        if exclude is None:
            obj.exclude = None
        else:
            obj.exclude = [Basic.sympify(x) for x in exclude]
        return obj

    def matches(pattern, expr, repl_dict={}, evaluate=False):
        for p,v in repl_dict.items():
            if p==pattern:
                if v==expr: return repl_dict
                return None
        if pattern.exclude:
            for x in pattern.exclude:
                if x in expr:
                    return None
        repl_dict = repl_dict.copy()
        repl_dict[pattern] = expr
        return repl_dict

    def tostr(self, level=0):
        return self.name + '_'
