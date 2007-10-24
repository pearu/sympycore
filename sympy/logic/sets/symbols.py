
from ...core import Basic
from ...core.utils import singleton
from ...core.symbol import BasicSymbol
from .basic import BasicSet

__all__ = ['SetSymbol', 'UniversalSet', 'EmptySet',
           'Empty', 'Universal']

class SetSymbol(BasicSet, BasicSymbol):
    """ Set symbol.
    """
class UniversalSet(SetSymbol):
    """ A set of all sets.
    """
    is_empty = False
    @singleton
    def __new__(cls):
        return str.__new__(cls, 'UNIVERSALSET')
    @property
    def superset(self):
        return self
    @property
    def domain(self):
        return self
    def is_subset_of(self, other):
        return self==other
    def try_contains(self, other):
        return True
    def try_complementary(self, superset):
        return Empty
    def try_shifted(self, shift):
        return self
    def try_positive(self):
        return Positive(Reals)
    def try_negative(self):
        return Negative(Reals)


class EmptySet(SetSymbol):
    is_empty = True
    @singleton
    def __new__(cls):
        return str.__new__(cls, 'EMPTYSET')
    def try_contains(self, other): return False
    def is_subset_of(self, other):
        return True
    @property
    def superset(self):
        return Universal
    @property
    def domain(self):
        return self
    def try_complementary(self, superset):
        return superset
    def try_shifted(self, shift):
        return self
    def try_positive(self):
        return self
    def try_negative(self):
        return self

Basic.is_empty = None

Empty = EmptySet()
Universal = UniversalSet()
