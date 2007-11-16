
from ...core.basic import Basic, Composite, sympify, classes, sympify_types1
from ...core.utils import UniversalMethod
#from ...core.methods import BasicImmutableMeths
from .basic import BasicSet

__all__ = ['Set']

class Set(BasicSet, Composite, frozenset):
    """ A set object with elements.
    """

    def __new__(cls, *args):
        if not args: return Empty
        args = map(sympify,args)
        obj = frozenset.__new__(cls, args)
        obj.args_sorted = None
        obj._hashvalue = None
        #set.update(obj, args)
        return obj

    def __init__(self, *args, **kws):
        # avoid calling default set.__init__.
        pass

    def __eq__(self, other):
        if isinstance(other, sympify_types1):
            other = sympify(other)
        if not isinstance(other, self.__class__):
            return False
        return frozenset.__eq__(self, other)

    def compare(self, other):
        c = cmp(self.count_ops(symbolic=False), self.count_ops(symbolic=False))
        if c:
            return c
        c = cmp(len(self), len(other))
        if c:
            return c
        return cmp(id(self), id(other))

    def __hash__(self):
        if self._hashvalue is None:
            self._hashvalue = hash(tuple(self))
        return self._hashvalue

    @property
    def domain(self):
        return self
    @property
    def superset(self):
        return self
    
    def try_element(self, other):
        return frozenset.__contains__(self, other)

    def try_union(self, other):
        if other.is_Set:
            return Set(*set(self).union(other))
    def try_intersection(self, other):
        if other.is_Set:
            return Set(*set(self).intersection(other))
    def try_difference(self, other):
        if other.is_Set:
            return Set(*set(self).difference(other))

    # method to be (re)moved
    def try_supremum(self):
        r = classes.Max(*self)
    def try_infimum(self):
        return classes.Min(*self)


