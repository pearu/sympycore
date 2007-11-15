
from ...core.basic import Basic, Composite, sympify, classes
from ...core.methods import BasicImmutableMeths
from .basic import BasicSet

__all__ = ['Set']

class Set(BasicImmutableMeths, BasicSet, Composite, frozenset):
    """ A set object with elements.
    """

    def __new__(cls, *args):
        if not args: return Empty
        args = map(sympify,args)
        obj = frozenset.__new__(cls, args)
        #set.update(obj, args)
        return obj

    def __init__(self, *args, **kws):
        # avoid calling default set.__init__.
        pass

    def as_list(self):
        r = list(self)
        r.sort(Basic.static_compare)
        return r

    def compare(self, other):
        if self is other: return 0
        c = cmp(self.__class__, other.__class__)
        if c: return c
        c = cmp(len(self), len(other))
        if c: return c
        return cmp(self.as_list(), other.as_list())

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return frozenset.__eq__(self, other)
        if isinstance(self, (Basic,bool)):
            return False
        return self==sympify(other)

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


