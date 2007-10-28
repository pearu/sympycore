
from .utils import memoizer_immutable_args
from .basic import Atom, Basic, sympify

__all__ = ['BasicSymbol', 'BasicDummySymbol','BasicWildSymbol']

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
            if other.is_BasicDummySymbol: return False
            if not isinstance(other, self.__class__): return False
        return str.__eq__(self, other)            

    __hash__ = str.__hash__

    def as_dummy(self):
        return BasicDummySymbol(self.name)

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

class BasicWildSymbol(BasicDummySymbol):
    """
    Wild() matches any expression but another Wild().
    """

    def __new__(cls, name=None, exclude=None):
        if name is None:
            name = 'W%s' % (BasicSymbol._dummy_count+1)
        obj = BasicDummySymbol.__new__(cls, name)
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
