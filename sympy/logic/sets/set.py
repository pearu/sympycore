
from ...core.basic import Composite, sympify
from ...core.methods import ImmutableSetMeths
from .basic import BasicSet

__all__ = ['Set']

class Set(ImmutableSetMeths, BasicSet, Composite, set):
    """ A set object with elements.
    """

    def __new__(cls, *args):
        if not args: return Empty
        obj = set.__new__(cls)
        args = map(sympify,args)
        set.update(obj, args)
        return obj

    def __init__(self, *args, **kws):
        # avoid calling default set.__init__.
        pass
    
    def try_contains(self, other):
        return set.__contains__(self, other)
    def try_supremum(self):
        r = Basic.Max(*self)
    def try_infimum(self):
        return Basic.Min(*self)

    @property
    def domain(self):
        return self
    @property
    def superset(self):
        return self

