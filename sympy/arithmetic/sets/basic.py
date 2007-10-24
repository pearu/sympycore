
from ...core import Basic
from ...logic.sets import BasicSet, SetSymbol, SetFunction

class ArithmeticBasicSet(BasicSet):
    
    def __pos__(self):
        """ Convenience method to construct a subset of only positive quantities.
        """
        return Basic.Positive(self)
    def __neg__(self):
        """ Convenience method to construct a subset of only negative quantities.
        """
        return Basic.Negative(self)
    def __add__(self, other):
        """ Convinience method to construct a shifted set by other.
        """
        return Basic.Shifted(self, other)
    __radd__ = __add__
    def __sub__(self, other):
        return Basic.Shifted(self, -other)
    def __rsub__(self, other):
        return Basic.Shifted(-self, other)
    
    def __mul__(self, other):
        """ Convinience method to construct a set that elements divide by other.
        """
        return Basic.Divisible(self, other)
    __rmul__ = __mul__

    def try_supremum(self):
        """ Return supremum of a set.
        """
        return
    def try_infimum(self):
        """ Return infimum of a set.
        """
        return
    @property
    def is_unbounded_left(self):
        m = Basic.Min(self)
        if m.is_Number: return False
        if m==-Basic.oo: return True
        return

    @property
    def is_unbounded_right(self):
        m = Basic.Max(self)
        if m.is_Number: return False
        if m==Basic.oo: return True
        return

class ArithmeticSetSymbol(ArithmeticBasicSet, SetSymbol):

    pass

class ArithmeticSetFunction(ArithmeticBasicSet, SetFunction):

    pass
