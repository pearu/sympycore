

from ...core import Basic
from .setfunction import SetFunction
from .symbols import Empty, Universal

__all__ = ['Union', 'Intersection', 'Minus', 'Complementary']

class Union(SetFunction):
    """ Union of sets.
    """
    # signature is initialized in __init__.py

    @classmethod
    def canonize(cls, sets):
        if len(sets)==0: return Empty
        if len(sets)==1: return sets[0]
        new_sets = set()
        flag = False
        for s in sets:
            if s.is_Union:
                new_sets = new_sets.union(s.args)
                flag = True
            elif s.is_empty:
                flag = True
            else:
                n = len(new_sets)
                new_sets.add(s)
                if n==len(new_sets):
                    flag = True
        for s in new_sets:
            for s1 in new_sets:
                if s is s1: continue
                if s.is_subset_of(s1):
                    new_sets.remove(s)
                    return cls(*new_sets)
                if s.is_BasicRange:
                    s2 = s.try_union(s1)
                    if s2 is not None:
                        new_sets.remove(s)
                        new_sets.remove(s1)
                        new_sets.add(s2)
                        return cls(*new_sets)
        if flag:
            return cls(*new_sets)
        if len(sets)==2:
            s1,s2 = list(sets)
            if s1.is_Complementary and s1.set==s2:
                return s1.superset
            elif s2.is_Complementary and s2.set==s1:
                return s2.superset
        sets.sort(Basic.compare)
        return

    def try_contains(self, other):
        l = []
        for set in self.args:
            r = set.contains(other)
            if isinstance(r, bool):
                if r:
                    return True
            else:
                l.append(set)
        if not l:
            return False
        if len(l)<len(self.args):
            return Element(other, Union(*l))

    @property
    def superset(self):
        return self

    @property
    def domain(self):
        return Union(*[s.domain for s in self.args])

class Intersection(SetFunction):
    """ Intersection of sets.
    """
    # signature is initialized in __init__.py
    
    @classmethod
    def canonize(cls, sets):
        if len(sets)==0: return ~Empty
        if len(sets)==1: return sets[0]
        new_sets = set()
        flag = False
        for s in sets:
            if s.is_Intersection:
                new_sets = new_sets.union(s.args)
                flag = True
            elif s.is_empty:
                return s
            else:
                n = len(new_sets)
                new_sets.add(s)
                if n==len(new_sets):
                    flag = True
        for s in new_sets:
            for s1 in new_sets:
                if s is s1: continue
                if s.is_subset_of(s1):
                    new_sets.remove(s1)
                    return cls(*new_sets)
                if s.is_BasicRange:
                    s2 = s.try_intersection(s1)
                    if s2 is not None:
                        new_sets.remove(s)
                        new_sets.remove(s1)
                        new_sets.add(s2)
                        return cls(*new_sets)
        if flag:
            return cls(*new_sets)
        if len(sets)==2:
            s1,s2 = list(sets)
            if s1.is_Complementary and s1.set==s2:
                return Empty
            if s2.is_Complementary and s2.set==s1:
                return Empty
        sets.sort(Basic.compare)
        return      

    @property
    def superset(self):
        return self

    @property
    def domain(self):
        return Union(*[s.domain for s in self.args])


class Minus(SetFunction):
    """ Set minus.
    """
    # signature is initialized in __init__.py
    
    @classmethod
    def canonize(cls, (lhs, rhs)):
        if rhs.is_subset_of(lhs) and rhs.superset==lhs:
            return Complementary(rhs, lhs)
        if rhs.is_subset_of(lhs) is False:
            return lhs
        return lhs.try_minus(rhs)

class Complementary(SetFunction):
    """ Complementary set of a set S within F.

    x in Complementary(S, F) <=> x in F & x not in S
    x in F & x not in Complementary(S, F) <=> x in S
    """
    # signature is initialized in __init__.py

    @property
    def domain(self):
        return self[1].domain

    @property
    def superset(self):
        return self[1]

    @property
    def set(self):
        return self[0]
    def __new__(cls, set, superset=None):
        if superset is None:
            superset = set.superset
        return SetFunction.__new__(cls, set, superset)
    
    @classmethod
    def canonize(cls, (set, superset)):
        if set==superset:
            return Empty
        if superset.is_Field and set.superset!=superset:
            return Union(Complementary(set, set.superset), Complementary(set.superset, superset))
        return set.try_complementary(superset)
    def try_complementary(self, superset):
        if self.superset==superset:
            return self.set
        if superset.is_subset_of(self.superset) and self.set.is_subset_of(superset):
            return self.set
    def try_contains(self, other):
        set = self.args[0]
        field = self.superset
        r = field.contains(other)
        if isinstance(r, bool):
            if r:
                r = set.contains(other)
                if isinstance(r, bool):
                    r = not r
            if isinstance(r, bool):
                return r
    def is_subset_of(self, other):
        set = self.args[0]
        if set.is_subset_of(other):
            return True
        if set==other:
            return False
    def try_infimum(self):
        return Basic.Min(self.superset)
    def try_supremum(self):
        return Basic.Max(self.superset)    

