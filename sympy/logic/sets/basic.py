from ...core import Basic, sympify

es = Basic.is_element_of_set

class BasicSet(Basic):
    """ Defines generic methods for set classes.
    """
    @property
    def superset(self):
        """ Return container set.
        """
        raise NotImplementedError('%s.superset property' % (self.__class__.__name__))

    @property
    def domain(self):
        """ Return one of the predefined sets that includes self.
        """
        assert isinstance(self, Basic.SetSymbol),`self`
        return self

    def try_contains(self, other):
        """ Check if other is an element of self.
        If the result is undefined, return None.
        """
        return

    def try_includes(self, other):
        """ Check if other is a subset of self.
        If the result is undefined, return None.
        """
        if other==self:
            return True
        if other.is_Set:
            flag = False
            for e in other:
                r = es(e, self)
                if isinstance(r, bool):
                    if not r: return False
                else:
                    flag = True
            if flag:
                return
            return True
        return

    def contains(self, other):
        """ Convenience method to construct Element(other, self) instance.
        """
        return Basic.Element(sympify(other), self)

    def includes(self, other):
        """ Convenience method to construct Subset(other, self) instance.
        """
        return Basic.Subset(sympify(other), self)

    def is_subset_of(self, other):
        """ Check if self is a subset of other.
        """
        return

    def try_complementary(self, superset):
        """ Return a complementary set of self in the container field
        (as returned by the superset property).
        """
        return
    def try_positive(self):
        return
    def try_negative(self):
        return
    def try_shifted(self, shift):
        return
    def try_divisible(self, divisor):
        return
    def try_minus(self, other):
        return
    def try_union(self, other):
        return
    def try_intersection(self, other):
        return

    def __invert__(self):
        """ Convinience method to construct a complementary set.
        """
        return Complementary(self, self.superset)
