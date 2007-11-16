
from .utils import memoizer_immutable_args, singleton
from .basic import Atom, Basic, sympify, BasicWild, sympify_types1

__all__ = ['BasicSymbol', 'BasicDummySymbol','BasicWildSymbol']

class BasicSymbol(Atom, str):
    """ Named symbol.
    """

    def __new__(cls, name):
        assert isinstance(name, str), `name`
        return str.__new__(cls, name)

    @property
    def name(self): return str.__str__(self)

    def torepr(self):
        return '%s(%r)' % (self.__class__.__name__, self.name)

    def tostr(self, level=0):
        return self.name

    def __eq__(self, other):
        if isinstance(other, sympify_types1):
            other = sympify(other)
        if not isinstance(other, self.__class__):
            return False
        return str.__eq__(self, other)

    def compare(self, other):
        return cmp(self.name, other.name)

    __hash__ = str.__hash__

    def as_dummy(self):
        return self.__class__._dummy_class(self.name)

    # disable arithmetic methods for basic symbols,
    # though they can be still used in arithmetic functions.
    def __add__(self, other):
        # this will prevent `BasicSymbol('a') + 'b'` -> `'ab'`
        return NotImplemented
    def __radd__(self, other):
        # Note that `'a' + BasicSymbol('b')` still returns `'ab'`.
        # This might be the reason why we should not derive
        # BasicSymbol from str. Need to measure the performance
        # of different approaches..
        return NotImplemented
    def __mul__(self, other):
        return NotImplemented
    def __rmul__(self, other):
        return NotImplemented
    def __mod__(self, other):
        return NotImplemented
    def __rmod__(self, other):
        return NotImplemented

#@singleton
def _get_default_dummy_name(cls):
    return ''.join([c for c in cls.__name__ if c.isupper()])

class BasicDummySymbol(BasicSymbol):
    """ Indexed dummy symbol.
    """

    _dummy_count = 0

    _get_default_dummy_name = classmethod(_get_default_dummy_name)
    
    def __new__(cls, name = None):
        BasicDummySymbol._dummy_count += 1
        if name is None:
            c = BasicDummySymbol._dummy_count
            n = cls._get_default_dummy_name() + str(c)
        else:
            n = name
        obj = str.__new__(cls, n)
        obj._name = name
        return obj

    def torepr(self):
        if self._name is None:
            return '%s()' % (self.__class__.__name__)
        return '%s(%r)' % (self.__class__.__name__, self.name)

    def tostr(self, level=0):
        return '_' + self.name

    def __eq__(self, other):
        # dymmy symbols are singletons
        return self is other

class BasicWildSymbol(BasicWild, BasicDummySymbol):
    """ Wild symbol.
    """

    def __new__(cls, name=None, predicate=None):
        obj = BasicDummySymbol.__new__(cls, name)
        if predicate is not None:
            obj.predicate = predicate
        return obj

    def tostr(self, level=0):
        return self.name + '_'


