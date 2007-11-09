
from ...core import Basic
from ...core.function import FunctionSignature
from ...logic.sets import SetFunction, set_classes, Union, Set, Empty
from .basic import ArithmeticSetFunction

__all__ = ['RangeOO', 'RangeOC', 'RangeCO', 'RangeCC', 'Range']

from ...core.assume_utils import is_equal as eq
from ..assume_utils import is_less as lt
from ..assume_utils import is_less_equal as le
from ..assume_utils import is_greater as gt
from ..assume_utils import is_greater_equal as ge
from ...logic.sets.assume_utils import is_element_of_set as es
from ...logic.sets.assume_utils import is_subset_of_set as ss

class BasicRange(ArithmeticSetFunction):
    """ Base class for range functions.
    """
    signature = FunctionSignature((Basic, Basic, set_classes),set_classes)
    
    @property
    def a(self):
        return self[0]
    @property
    def b(self):
        return self[1]
    @property
    def superset(self):
        return self[2]
    @property
    def domain(self):
        return self[2].domain
    
    @classmethod
    def canonize(cls, (a,b,set)):
        if lt(b, a):
            return Empty
        if eq(a,b):
            if cls is RangeCC:
                r = es(a, set)
                if isinstance(r, bool):
                    if r: return Set(a)
                    return Empty
                return
            return Empty
        if lt(a, b):
            if set.is_BasicRange:
                sa, sb, superset = set.args
                new_a, new_b = a, b
                n = cls.__name__
                b1,b2 = n[-2]=='C', n[-1]=='C'
                n = set.__class__.__name__
                c1,c2 = n[-2]=='C', n[-1]=='C'
                if eq(sa, a):
                    b1 = b1 and c1
                elif lt(a, sa):
                    new_a = sa
                    b1 = c1
                elif lt(sa, a):
                    pass
                else:
                    return
                if eq(b, sb):
                    b2 = b2 and c2
                elif lt(sb, b):
                    new_b = sb
                    b2 = c2
                elif lt(b, sb):
                    pass
                else:
                    return
                if new_a==-Basic.oo:
                    b1 = False
                if new_b==Basic.oo:
                    b2 = False
                new_cls = {(False,False):RangeOO,
                           (False,True):RangeOC,
                           (True,False):RangeCO,
                           (True,True):RangeCC}[(b1,b2)]
                return new_cls(new_a, new_b, superset)
        if cls.__name__[-2]=='C':
            if a==-Basic.oo:
                if cls.__name__[-1]=='C':
                    if b==Basic.oo:
                        return RangeOO(a,b,set)
                    return RangeOC(a,b,set)
                else:
                    return RangeOO(a,b,set)
            elif b==Basic.oo:
                if cls.__name__[-1]=='C':
                    return RangeCO(a,b,set)
        elif cls.__name__[-1]=='C':
            if b==Basic.oo:
                return RangeOO(a,b,set)

    def try_element(self, other):
        a,b,superset = self.args
        if lt(other,a) or lt(b,other):
            return False
        isboundary = False
        if self.a==other:
            isboundary = True
            if self.__class__.__name__[-2]=='O': return False
        elif self.b==other:
            isboundary = True
            if self.__class__.__name__[-1]=='O': return False
        if isboundary or (lt(a,other) and lt(other, b)):
            r = es(other, superset)
            if isinstance(r,bool):
                return r
            if superset.domain.is_RealSet:
                # Element(x,Range(x-1,x+1,Reals)) -> True
                return True
            # Element(x,Range(x-1,x+1,Integers)) -> None
            return
    def try_shifted(self, shift):
        return self.__class__(self.a+shift, self.b+shift, self.superset)
    def try_intersection(self, other):
        if not other.is_BasicRange:
            return
        r = self.__class__(self.a, self.b, other)
        if r.is_BasicRange and r.superset==other:
            return
        return r
    def try_subset(self, other):
        if other.is_BasicRange:
            r = ss(other.domain, self.domain)
            if not isinstance(r, bool):
                return
            if not r: return False
            a,b,s1 = other.args
            c,d,s2 = self.args
            if self.is_RangeOO:
                if other.is_RangeOO:
                    # (a,b) is subset of (c,d)
                    cf = (le,le,le,le,lt,lt)
                elif other.is_RangeOC:
                    # (a,b] is subset of (c,d)
                    cf = (le,lt,le,le,lt,le)
                elif other.is_RangeCO:
                    # [a,b) is subset of (c,d)
                    cf = (lt,le,le,le,le,lt)
                elif other.is_RangeCC:
                    # [a,b] is subset of (c,d)
                    cf = (lt,lt,le,le,le,le)
                else:
                    return
            elif self.is_RangeOC:
                if other.is_RangeOO:
                    # (a,b) is subset of (c,d]
                    cf = (le,le,le,lt,lt,lt)
                elif other.is_RangeOC:
                    # (a,b] is subset of (c,d]
                    cf = (le,le,le,lt,lt,lt)
                elif other.is_RangeCO:
                    # [a,b) is subset of (c,d]
                    cf = (lt,le,le,lt,le,lt)
                elif other.is_RangeCC:
                    # [a,b] is subset of (c,d]
                    cf = (lt,le,le,lt,le,lt)
                else:                
                    return
            elif self.is_RangeCO:
                if other.is_RangeOO:
                    # (a,b) is subset of [c,d)
                    cf = (le,le,le,le,lt,lt)
                elif other.is_RangeOC:
                    # (a,b] is subset of [c,d)
                    cf = (le,lt,lt,le,lt,le)
                elif other.is_RangeCO:
                    # [a,b) is subset of [c,d)
                    cf = (le,le,lt,le,lt,lt)
                elif other.is_RangeCC:
                    # [a,b] is subset of [c,d)
                    cf = (le,lt,lt,le,lt,le)
                else:
                    return
            elif self.is_RangeCC:
                if other.is_RangeOO:
                    # (a,b) is subset of [c,d]
                    cf = (le,le,le,le,lt,lt)
                elif other.is_RangeOC:
                    # (a,b] is subset of [c,d]
                    cf = (le,le,lt,lt,lt,lt)
                elif other.is_RangeCO:
                    # [a,b) is subset of [c,d]
                    cf = (le,le,lt,lt,lt,lt)
                elif other.is_RangeCC:
                    # [a,b] is subset of [c,d]
                    cf = (le,le,lt,lt,lt,lt)
                else:
                    return
            else:
                return
            if cf[0](c,a) and cf[1](b,d):
                return True
            if cf[2](b,c) or cf[3](d,a) or cf[4](a,c) or cf[5](d,b):
                return False
        return Basic.BasicSet.try_subset(self, other)

class RangeOO(BasicRange):
    """ An open range (a,b) of a set S."""

    def try_supremum(self):
        if self.domain.is_IntegerSet:
            return self.b-1
        return self.b
    def try_infimum(self):
        if self.domain.is_IntegerSet:
            return self.a+1
        return self.a
    def try_positive(self):
        return self.__class__(0, self.b, self.superset)
    def try_negative(self):
        return self.__class__(self.a, 0, self.superset)
    def try_union(self, other):
        if not other.is_BasicRange:
            return
        a,b,d1 = self[:]
        c,d,d2 = other[:]
        if not d1==d2:
            return
        superset = d1
        if eq(b, c):
            if other.is_RangeOO or other.is_RangeOC:
                # (a,b) U (b,d), (a,b) U (b,d]
                return
            if other.is_RangeCO:
                # (a,b) U [b,d)
                return RangeOO(a, d, superset)
            if other.is_RangeCC:
                # (a,b) U [b,d]
                return RangeOC(a, d, superset)
        if le(a, c):
            # code below assumes a<=c for simplicity
            if other.is_RangeOO:
                # (a,b) U (c,d)
                if lt(c, b):
                    if le(d, b): return self
                    if lt(b, d): return RangeOO(a, d, superset)
                return
            if other.is_RangeOC:
                # (a,b) U (c,d]
                if lt(c, b):
                    if lt(d, b): return self
                    if le(b, d): return RangeOC(a, d, superset)
                return
            if other.is_RangeCO:
                # (a,b) U [c,d)
                if eq(a, c):
                    if le(b, d): return other
                    if lt(d, b): return RangeCO(a, b, superset)
                    return
                if le(c, b):
                    if le(d, b): return self
                    if lt(b, d): return RangeOO(a, d, superset)
                return
            if other.is_RangeCC:
                # (a,b) U [c,d]
                if eq(a,c):
                    if le(b, d): return other
                    if lt(d, b): return RangeCC(a, b, superset)
                    return
                if le(c, b):
                    if lt(d, b): return self
                    if le(b, d): return RangeOC(a, d, superset)
                    return
            return
    def try_difference(self, other):
        if not other.is_BasicRange:
            return
        a,b,d1 = self[:]
        c,d,d2 = other[:]
        if not d1==d2:
            return
        superset = d1
        # (a,b) \ (c,d)
        if le(b,c) or le(d,a):
            # (a,b<=c,d), (c,d<=a,b)
            return self
        if eq(a, c):
            if le(b,d): return Empty
            if lt(d,b):
                # (a=c,d<b)
                if other.is_RangeOO or other.is_RangeCO:
                    return RangeCO(d,b,superset)
                return RangeOO(d,b,superset)
        if lt(a,c):
            if le(b,d):
                # (a<c,b<=d)
                if other.is_RangeOO or other.is_RangeOC:
                    return RangeOC(a,c,superset)
                return RangeOO(a,c,superset)
            if lt(d,b):
                # (a<c,d<b)
                if other.is_RangeOO:
                    return Union(RangeOC(a,c,superset), RangeCO(d,b,superset))
                if other.is_RangeOC:
                    return Union(RangeOC(a,c,superset), RangeOO(d,b,superset))
                if other.is_RangeCO:
                    return Union(RangeOO(a,c,superset), RangeCO(d,b,superset))
                if other.is_RangeCC:
                    return Union(RangeOO(a,c,superset), RangeOO(d,b,superset))
        if lt(c,a):
            # (c,a,d,b), (c,a,b,d)
            if le(b,d):
                # (c<a,b<=d)
                return Empty
            if lt(d,b):
                # (c<a,d<b)
                if other.is_RangeOO or other.is_RangeCO:
                    return RangeCO(d,b,superset)
                return RangeOO(d,b,superset)
    def try_complementary(self, superset):
        if self.superset==superset.domain:
            return Union(RangeCC(Basic.Min(superset), self.a, superset),
                         RangeCC(self.b, Basic.Max(superset), superset),
                         )

class RangeOC(BasicRange):
    """ An semi-open range (a,b] of a set S."""

    def try_supremum(self):
        return self.b
    def try_infimum(self):
        if self.domain.is_IntegerSet:
            return self.a+1
        return self.a
    def try_positive(self):
        return self.__class__(0, self.b, self.superset)
    def try_negative(self):
        return RangeOO(self.a, 0, self.superset)
    def try_union(self, other):
        if not other.is_BasicRange:
            return
        a,b,d1 = self[:]
        c,d,d2 = other[:]
        if not d1==d2:
            return
        superset = d1
        if eq(b, c):
            if other.is_RangeOO or other.is_RangeCO:
                # (a,b] U (b,d), (a,b] U [b,d)
                return RangeOO(a, d, superset)
            if other.is_RangeOC or other.is_RangeCC:
                # (a,b] U (b,d], (a,b] U [b,d]
                return RangeOC(a, d, superset)
        if le(a, c):
            # code below assumes a<=c for simplicity
            if other.is_RangeOO:
                # (a,b] U (c,d)
                if lt(c, b):
                    if le(d, b): return self
                    if lt(b, d): return RangeOO(a, d, superset)
                return
            if other.is_RangeOC:
                # (a,b] U (c,d]
                if le(c, b):
                    if le(d, b): return self
                    if lt(b, d): return RangeOC(a, d, superset)
                return
            if other.is_RangeCO:
                # (a,b] U [c,d)
                if eq(a, c):
                    if lt(b, d): return other
                    if le(d, b): return RangeCC(a, b, superset)
                    return
                if le(c, b):
                    if le(d, b): return self
                    if lt(b, d): return RangeOO(a, d, superset)
                return
            if other.is_RangeCC:
                # (a,b] U [c,d]
                if eq(a,c):
                    if le(b, d): return other
                    if lt(d, b): return self
                    return
                if le(c, b):
                    if le(d, b): return self
                    if lt(b, d): return RangeOC(a, d, superset)
                    return
            return
    def try_difference(self, other):
        if not other.is_BasicRange:
            return
        a,b,d1 = self[:]
        c,d,d2 = other[:]
        if not d1==d2:
            return
        superset = d1
        # (a,b] \ (c,d)
        if lt(b,c) or le(d,a):
            # (a,b<=c,d), (c,d<=a,b)
            return self
        if eq(b,c):
            return RangeOO(a,b,superset)
        if eq(a, c):
            if eq(b,d):
                if other.is_RangeOO or other.is_RangeCO:
                    return Set(b)
                return Empty
            if lt(b,d): return Empty
            if lt(d,b):
                # (a=c,d<b)
                if other.is_RangeOO or other.is_RangeCO:
                    return RangeCC(d,b,superset)
                return RangeOC(d,b,superset)
        if lt(a,c):
            if eq(b,d):
                if other.is_RangeOO:
                    return Union(RangeOC(a,c,superset),Set(b))
                if other.is_RangeCO:
                    return Union(RangeOO(a,c,superset),Set(b))
                if other.is_RangeOC:
                    return RangeOC(a,c,superset)
                if other.is_RangeCC:
                    return RangeOO(a,c,superset)
                return
            if lt(b,d):
                # (a<c,b<=d)
                if other.is_RangeOO or other.is_RangeOC:
                    return RangeOC(a,c,superset)
                return RangeOO(a,c,superset)
            if lt(d,b):
                # (a<c,d<b)
                if other.is_RangeOO:
                    return Union(RangeOC(a,c,superset), RangeCC(d,b,superset))
                if other.is_RangeOC:
                    return Union(RangeOC(a,c,superset), RangeOC(d,b,superset))
                if other.is_RangeCO:
                    return Union(RangeOO(a,c,superset), RangeCC(d,b,superset))
                if other.is_RangeCC:
                    return Union(RangeOO(a,c,superset), RangeOC(d,b,superset))
        if lt(c,a):
            # (c,a,d,b), (c,a,b,d)
            if eq(b,d):
                # (c<a,b=d)
                if other.is_RangeOO or other.is_RangeCO:
                    return Set(b)
                return Empty
            if lt(b,d):
                # (c<a,b<d)
                return Empty
            if lt(d,b):
                # (c<a,d<b)
                if other.is_RangeOO or other.is_RangeCO:
                    return RangeCC(d,b,superset)
                return RangeOC(d,b,superset)
    def try_complementary(self, superset):
        if self.superset==superset.domain:
            return Union(RangeCC(Basic.Min(superset), self.a, superset),
                         RangeOC(self.b, Basic.Max(superset), superset),
                         )

class RangeCO(BasicRange):
    """ An semi-open range [a,b) of a set S."""

    def try_supremum(self):
        if self.domain.is_IntegerSet:
            return self.b-1
        return self.b
    def try_infimum(self):
        return self.a
    def try_positive(self):
        return RangeOO(0, self.b, self.superset)
    def try_negative(self):
        return self.__class__(self.a, 0, self.superset)
    def try_union(self, other):
        if not other.is_BasicRange:
            return
        a,b,d1 = self[:]
        c,d,d2 = other[:]
        if not d1==d2:
            return
        superset = d1
        if eq(b, c):
            if other.is_RangeOO or other.is_RangeOC:
                # [a,b) U (b,d), [a,b) U (b,d]
                return
            if other.is_RangeCO:
                # [a,b) U [b,d)
                return RangeCO(a, d, superset)
            if other.is_RangeCC:
                # [a,b) U [b,d]
                return RangeCC(a, d, superset)
        if le(a, c):
            # code below assumes a<=c for simplicity
            if other.is_RangeOO:
                # [a,b) U (c,d)
                if lt(c, b):
                    if le(d, b): return self
                    if lt(b, d): return RangeCO(a, d, superset)
                return
            if other.is_RangeOC:
                # [a,b) U (c,d]
                if lt(c, b):
                    if lt(d, b): return self
                    if le(b, d): return RangeCC(a, d, superset)
                return
            if other.is_RangeCO:
                # [a,b) U [c,d)
                if le(c, b):
                    if le(d, b): return self
                    if lt(b, d): return RangeCO(a, d, superset)
                return
            if other.is_RangeCC:
                # [a,b) U [c,d]
                if le(c, b):
                    if lt(d, b): return self
                    if le(b, d): return RangeCC(a, d, superset)
                    return
            return
    def try_difference(self, other):
        if not other.is_BasicRange:
            return
        a,b,d1 = self[:]
        c,d,d2 = other[:]
        if not d1==d2:
            return
        superset = d1
        # [a,b) \ (c,d)
        if eq(d,a):
            if other.is_RangeOO or other.is_RangeCO:
                return RangeCO(a,b,superset)
            if other.is_RangeOC or other.is_RangeCC:
                return RangeOO(a,b,superset)
            return
        if le(b,c) or lt(d,a):
            # (a,b<=c,d), (c,d<=a,b)
            return self
        if eq(a, c):
            if eq(b,d):
                if other.is_RangeOO or other.is_RangeOC:
                    return Set(a)
                return Empty
            if lt(b,d):
                if other.is_RangeOO or other.is_RangeOC:
                    return Set(a)
                return Empty
            if lt(d,b):
                # (a=c,d<b)
                if other.is_RangeOO:
                    return Union(Set(a),RangeCO(d,b,superset))
                if other.is_RangeOC:
                    return Union(Set(a),RangeOO(d,b,superset))
                if other.is_RangeCO:
                    return RangeCO(d,b,superset)
                if other.is_RangeCC:
                    return RangeOO(d,b,superset)
        if lt(a,c):
            if le(b,d):
                # (a<c,b<=d)
                if other.is_RangeOO or other.is_RangeOC:
                    return RangeCC(a,c,superset)
                return RangeCO(a,c,superset)
            if lt(d,b):
                # (a<c,d<b)
                if other.is_RangeOO:
                    return Union(RangeCC(a,c,superset), RangeCO(d,b,superset))
                if other.is_RangeOC:
                    return Union(RangeCC(a,c,superset), RangeOO(d,b,superset))
                if other.is_RangeCO:
                    return Union(RangeCO(a,c,superset), RangeCO(d,b,superset))
                if other.is_RangeCC:
                    return Union(RangeCO(a,c,superset), RangeOO(d,b,superset))
        if lt(c,a):
            # (c,a,d,b), (c,a,b,d)
            if le(b,d):
                # (c<a,b<=d)
                return Empty
            if lt(d,b):
                # (c<a,d<b)
                if other.is_RangeOO or other.is_RangeCO:
                    return RangeCO(d,b,superset)
                if other.is_RangeOC or other.is_RangeCC:
                    return RangeOO(d,b,superset)
                return
    def try_complementary(self, superset):
        if self.superset==superset.domain:
            return Union(RangeCO(Basic.Min(superset), self.a, superset),
                         RangeCC(self.b, Basic.Max(superset), superset),
                         )

class RangeCC(BasicRange):
    """ An closed range [a,b] of a set S."""

    def try_supremum(self):
        return self.b
    def try_infimum(self):
        return self.a
    def try_positive(self):
        return RangeOC(0, self.b, self.superset)
    def try_negative(self):
        return RangeCO(self.a, 0, self.superset)
    def try_union(self, other):
        if not other.is_BasicRange:
            return
        a,b,d1 = self[:]
        c,d,d2 = other[:]
        if not d1==d2:
            return
        superset = d1
        if eq(b, c):
            if other.is_RangeOO or other.is_RangeCO:
                # [a,b] U (b,d), [a,b] U [b,d)
                return RangeCO(a, d, superset)
            if other.is_RangeCC or other.is_RangeOC:
                # [a,b] U [b,d], [a,b] U (b,d]
                return RangeCC(a, d, superset)
        if le(a, c):
            # code below assumes a<=c for simplicity
            if other.is_RangeOO:
                # [a,b] U (c,d)
                if le(c, b):
                    if le(d, b): return self
                    if lt(b, d): return RangeCO(a, d, superset)
                return
            if other.is_RangeOC:
                # [a,b] U (c,d]
                if le(c, b):
                    if le(d, b): return self
                    if lt(b, d): return RangeCC(a, d, superset)
                return
            if other.is_RangeCO:
                # [a,b] U [c,d)
                if le(c, b):
                    if le(d, b): return self
                    if lt(b, d): return RangeCO(a, d, superset)
                return
            if other.is_RangeCC:
                # [a,b] U [c,d]
                if le(c, b):
                    if le(d, b): return self
                    if lt(b, d): return RangeCC(a, d, superset)
                    return
            return
    def try_difference(self, other):
        if not other.is_BasicRange:
            return
        a,b,d1 = self[:]
        c,d,d2 = other[:]
        if not d1==d2:
            return
        superset = d1
        # [a,b] \ (c,d)
        if eq(d,a):
            if other.is_RangeOO or other.is_RangeCO:
                return RangeCC(a,b,superset)
            if other.is_RangeOC or other.is_RangeCC:
                return RangeOC(a,b,superset)
            return
        if eq(b,c):
            if other.is_RangeOO or other.is_RangeOC:
                return self
            if other.is_RangeCO or other.is_RangeCC:
                return RangeCO(a,b,superset)
            return
        if lt(b,c) or lt(d,a):
            # (a,b<=c,d), (c,d<=a,b)
            return self
        if eq(a, c):
            if eq(b,d):
                if other.is_RangeOO:
                    return Set(a,b)
                if other.is_RangeOC:
                    return Set(a)
                if other.is_RangeCO:
                    return Set(b)
                if other.is_RangeCC:
                    return Empty
                return
            if lt(b,d):
                if other.is_RangeOO or other.is_RangeOC:
                    return Set(a)
                return Empty
            if lt(d,b):
                # (a=c,d<b)
                if other.is_RangeOO:
                    return Union(Set(a),RangeCC(d,b,superset))
                if other.is_RangeOC:
                    return Union(Set(a),RangeOC(d,b,superset))
                if other.is_RangeCO:
                    return RangeCC(d,b,superset)
                if other.is_RangeCC:
                    return RangeOC(d,b,superset)
        if lt(a,c):
            if eq(b,d):
                if other.is_RangeOO:
                    return Union(RangeCC(a,c,superset),Set(b))
                if other.is_RangeOC:
                    return RangeCC(a,c,superset)
                if other.is_RangeCO:
                    return Union(RangeCO(a,c,superset),Set(b))
                if other.is_RangeCC:
                    return RangeCO(a,c,superset)
                return
            if lt(b,d):
                # (a<c,b<d)
                if other.is_RangeOO or other.is_RangeOC:
                    return RangeCC(a,c,superset)
                return RangeCO(a,c,superset)
            if lt(d,b):
                # (a<c,d<b)
                if other.is_RangeOO:
                    return Union(RangeCC(a,c,superset), RangeCC(d,b,superset))
                if other.is_RangeOC:
                    return Union(RangeCC(a,c,superset), RangeOC(d,b,superset))
                if other.is_RangeCO:
                    return Union(RangeCO(a,c,superset), RangeCC(d,b,superset))
                if other.is_RangeCC:
                    return Union(RangeCO(a,c,superset), RangeOC(d,b,superset))
        if lt(c,a):
            # (c,a,d,b), (c,a,b,d)
            if eq(b,d):
                if other.is_RangeOO or other.is_RangeCO:
                    return Set(b)
                return Empty
            if lt(b,d):
                # (c<a,b<=d)
                return Empty
            if lt(d,b):
                # (c<a,d<b)
                if other.is_RangeOO or other.is_RangeCO:
                    return RangeCC(d,b,superset)
                if other.is_RangeOC or other.is_RangeCC:
                    return RangeOC(d,b,superset)
                return
    def try_complementary(self, superset):
        if self.superset==superset.domain:
            return Union(RangeCO(Basic.Min(superset), self.a, superset),
                         RangeOC(self.b, Basic.Max(superset), superset),
                         )

class Range(RangeOO):
    """ An open range (a,b) of a set S (default=Reals).
    """
    def __new__(cls, a, b, set=None):
        if set is None:
            set = Basic.RealSet()
        return RangeOO(a, b, set)

