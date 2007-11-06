
from .utils import memoizer_immutable_args
from .basic import Atom, Basic, sympify, BasicWild

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

    # disable arithmetic methods for basic strings
    def __add__(self, other):
        return NotImplemented
    def __radd__(self, other):
        return NotImplemented
    def __mul__(self, other):
        return NotImplemented
    def __rmul__(self, other):
        return NotImplemented
    def __mod__(self, other):
        return NotImplemented
    def __rmod__(self, other):
        return NotImplemented


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

class BasicWildSymbol(BasicWild, BasicDummySymbol):
    """
    Wild(exclude=[..]) matches any expression but another Wild instance
    and expression that has symbols from exclude list.
    Both pattern and expression must have the same metaclasses.
    """

    def __new__(cls, name=None, exclude=None, predicate=None):
        if name is None:
            name = 'W%s' % (BasicSymbol._dummy_count+1)
        obj = BasicDummySymbol.__new__(cls, name)
        if exclude is None:
            obj.exclude = None
        else:
            obj.exclude = [Basic.sympify(x) for x in exclude]
        if predicate is None:
            predicate = lambda expr: True
        obj.predicate = predicate
        return obj

    def tostr(self, level=0):
        return self.name + '_'
