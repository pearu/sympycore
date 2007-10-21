
from basic import Basic
from function import FunctionSignature
from sets import SetFunction, set_classes, Empty, Reals, Integers, Minus, Intersection, Union, Set

eq = Basic.is_equal
lt = Basic.is_less
le = Basic.is_less_equal
gt = Basic.is_greater
ge = Basic.is_greater_equal

class BasicRange(SetFunction):
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
    def canonize(cls, (a, b, set)):
        d = b - a
        if d.is_Number and d.is_negative:
            return Empty
        if d==-Basic.oo:
            return Empty
        if set==set.domain and a==Basic.Min(set) and b==Basic.Max(set):
            return set

    def _get_combined_class4minus(self, other):
        if other.__class__.__name__[0]=='O':
            return getattr(Basic,self.__class__.__name__[0]+'CRange')
        return getattr(Basic,self.__class__.__name__[0]+'ORange')

    def try_contains(self, other):
        r = self.superset.contains(other)
        if r is False:
            return False
        if r is not True:
            return
        if self.a.is_Number:
            if other.is_Number:
                if other < self.a:
                    return False
                if self.b.is_Number:
                    return other < self.b
                elif self.is_unbounded_right:
                    return True
        elif self.b.is_Number:
            if other.is_Number:
                if self.b < other:
                    return False
                if self.is_unbounded_left:
                    return True
    def try_shifted(self, shift):
        return self.__class__(self.a+shift, self.b+shift, self.superset)
    def try_minus(self, other):
        if other.is_BasicRange and self.superset==other.superset:
            flag = 'C' in (self.__class__.__name__[1]+other.__class__.__name__[0])
            n = self.__class__.__name__[:2]+other.__class__.__name__[:2]
            if self.a.is_Number and self.b.is_Number and other.a.is_Number and other.b.is_Number:
                if other.a <= self.a:
                    if other.b > self.b:
                        return Empty
                    if n[3]=='O':
                        clsname = 'C'+n[1]+'Range'
                    else:
                        clsname = 'O'+n[1]+'Range'
                    cls = getattr(Basic, clsname)
                    return cls(other.b, self.b, self.superset)
                if other.a < self.b:
                    if other.b >= self.b:
                        if n[2]=='O':
                            clsname = n[0]+'CRange'
                        else:
                            clsname = n[0]+'ORange'
                        cls = getattr(Basic, clsname)
                        return cls(self.a, other.a, self.superset)
                    if n[2]=='O':
                        clsname = n[0]+'CRange'
                    else:
                        clsname = n[0]+'ORange'
                    cls1 = getattr(Basic, clsname)
                    if n[3]=='O':
                        clsname = 'C'+n[1]+'Range'
                    else:
                        clsname = 'O'+n[1]+'Range'
                    cls2 = getattr(Basic, clsname)
                    return Union(cls1(self.a, other.a, self.superset), cls2(other.b, self.b, self.superset))

class OORange(BasicRange):
    """ An open range (a,b) of a set S."""

    @classmethod
    def canonize(cls, (a, b, set)):
        if a==b: return Empty
        return BasicRange.canonize((a, b, set))
    def try_contains(self, other):
        if self.a==other: return False
        if self.b==other: return False
        return super(OORange, self).try_contains(other)
    def try_supremum(self):
        if self.domain==Integers:
            return self.b-1
        return self.b
    def try_infimum(self):
        if self.domain==Integers:
            return self.a+1
        return self.a
    def try_positive(self):
        return self.__class__(0, self.b, self.superset)
    def try_negative(self):
        return self.__class__(self.a, 0, self.superset)
    def try_complementary(self, superset):
        if self.superset==superset:
            if self.is_unbounded_left:
                return CORange(self.b, Basic.Max(superset), superset)
            if self.is_unbounded_right:
                return OCRange(Basic.Min(superset),self.a, superset)
    def try_union(self, other):
        if not other.is_BasicRange:
            return
        a,b,d1 = self[:]
        c,d,d2 = other[:]
        if not d1==d2:
            return
        superset = d1
        if eq(b, c):
            if other.is_OORange or other.is_OCRange:
                # (a,b) U (b,d), (a,b) U (b,d]
                return
            if other.is_CORange:
                # (a,b) U [b,d)
                return OORange(a, d, superset)
            if other.is_CCRange:
                # (a,b) U [b,d]
                return OCRange(a, d, superset)
        if le(a, c):
            # code below assumes a<=c for simplicity
            if other.is_OORange:
                # (a,b) U (c,d)
                if lt(c, b):
                    if le(d, b): return self
                    if lt(b, d): return OORange(a, d, superset)
                return
            if other.is_OCRange:
                # (a,b) U (c,d]
                if lt(c, b):
                    if lt(d, b): return self
                    if le(b, d): return OCRange(a, d, superset)
                return
            if other.is_CORange:
                # (a,b) U [c,d)
                if eq(a, c):
                    if le(b, d): return other
                    if lt(d, b): return CORange(a, b, superset)
                    return
                if le(c, b):
                    if le(d, b): return self
                    if lt(b, d): return OORange(a, d, superset)
                return
            if other.is_CCRange:
                # (a,b) U [c,d]
                if eq(a,c):
                    if le(b, d): return other
                    if lt(d, b): return CCRange(a, b, superset)
                    return
                if le(c, b):
                    if lt(d, b): return self
                    if le(b, d): return OCRange(a, d, superset)
                    return
            return
    def try_intersection(self, other):
        if not other.is_BasicRange:
            return
        a,b,d1 = self[:]
        c,d,d2 = other[:]
        if not d1==d2:
            return
        superset = d1
        if eq(b, c):
            # (a,b) A (b,d), (a,b) A (b,d], (a,b) A [b,d), (a,b) A [b,d]
            return Empty
        if le(a, c):
            # code below assumes a<=c for simplicity
            if other.is_OORange:
                # (a,b) A (c,d)
                if le(b,c): return Empty
                if lt(c,b):
                    if le(b,d): return OORange(c,b,superset)
                    if lt(d,b): return other
                return
            if other.is_OCRange:
                # (a,b) A (c,d]
                if le(b,c): return Empty
                if lt(c,b):
                    if le(b,d): return OORange(c,b,superset)
                    if lt(d,b): return OCRange(c,d,superset)
                return
            if other.is_CORange:
                # (a,b) A [c,d)
                if lt(b,c): return Empty
                if lt(c,b):
                    if le(b,d): return CORange(c,b,superset)
                    if lt(d,b): return CORange(c,d,superset)
                return
            if other.is_CCRange:
                # (a,b) A [c,d]
                if lt(b,c): return Empty
                if lt(c,b):
                    if eq(a,c):
                        if le(b,d): return self
                        if lt(d,b): return OCRange(c,d,superset)
                    else:
                        if le(b,d): return CORange(c,b,superset)
                        if lt(d,b): return CCRange(c,d,superset)
                return

class OCRange(BasicRange):
    """ An semi-open range (a,b] of a set S."""

    @classmethod
    def canonize(cls, (a, b, set)):
        if a==b: return b
        return BasicRange.canonize((a, b, set))
    def try_contains(self, other):
        if self.a==other: return False
        if self.b==other: return self.superset.contains(other)
        return super(OCRange, self).try_contains(other)
    def try_supremum(self):
        return self.b
    def try_infimum(self):
        if self.domain==Integers:
            return self.a+1
        return self.a
    def try_positive(self):
        return self.__class__(0, self.b, self.superset)
    def try_negative(self):
        return OORange(self.a, 0, self.superset)
    def try_complementary(self, superset):
        if self.superset==superset:
            if self.is_unbounded_left:
                return OORange(self.b, Basic.Max(superset), superset)
            assert not self.is_unbounded_right,`self`
    def try_union(self, other):
        if not other.is_BasicRange:
            return
        a,b,d1 = self[:]
        c,d,d2 = other[:]
        if not d1==d2:
            return
        superset = d1
        if eq(b, c):
            if other.is_OORange or other.is_CORange:
                # (a,b] U (b,d), (a,b] U [b,d)
                return OORange(a, d, superset)
            if other.is_OCRange or other.is_CCRange:
                # (a,b] U (b,d], (a,b] U [b,d]
                return OCRange(a, d, superset)
        if le(a, c):
            # code below assumes a<=c for simplicity
            if other.is_OORange:
                # (a,b] U (c,d)
                if lt(c, b):
                    if le(d, b): return self
                    if lt(b, d): return OORange(a, d, superset)
                return
            if other.is_OCRange:
                # (a,b] U (c,d]
                if le(c, b):
                    if le(d, b): return self
                    if lt(b, d): return OCRange(a, d, superset)
                return
            if other.is_CORange:
                # (a,b] U [c,d)
                if eq(a, c):
                    if lt(b, d): return other
                    if le(d, b): return CCRange(a, b, superset)
                    return
                if le(c, b):
                    if le(d, b): return self
                    if lt(b, d): return OORange(a, d, superset)
                return
            if other.is_CCRange:
                # (a,b] U [c,d]
                if eq(a,c):
                    if le(b, d): return other
                    if lt(d, b): return self
                    return
                if le(c, b):
                    if le(d, b): return self
                    if lt(b, d): return OCRange(a, d, superset)
                    return
            return
    def try_intersection(self, other):
        if not other.is_BasicRange:
            return
        a,b,d1 = self[:]
        c,d,d2 = other[:]
        if not d1==d2:
            return
        superset = d1
        if eq(b, c):
            # (a,b] A (b,d), (a,b] A (b,d]
            if other.is_OORange or other.is_OCRange:
                return Empty
            # (a,b] A [b,d), (a,b] A [b,d]
            return Set(b)
        if le(a, c):
            # code below assumes a<=c for simplicity
            if other.is_OORange:
                # (a,b] A (c,d)
                if lt(b,c): return Empty
                if le(c,b):
                    if lt(b,d): return OCRange(c,b,superset)
                    if le(d,b): return OORange(c,d,superset)
                return
            if other.is_OCRange:
                # (a,b] A (c,d]
                if lt(b,c): return Empty
                if le(c,b):
                    if le(b,d): return OCRange(c,b,superset)
                    if lt(d,b): return other
                return
            if other.is_CORange:
                # (a,b] A [c,d)
                if lt(b,c): return Empty
                if lt(c,b):
                    if eq(a,c):
                        if lt(b,d): return self
                        if le(d,b): return OORange(c,d,superset)
                    else:
                        if lt(b,d): return CCRange(c,b,superset)
                        if le(d,b): return other
                return
            if other.is_CCRange:
                # (a,b] A [c,d]
                if lt(b,c): return Empty
                if lt(c,b):
                    if eq(a,c):
                        if le(b,d): return self
                        if lt(d,b): return OCRange(c,d,superset)
                    else:
                        if le(b,d): return CCRange(c,b,superset)
                        if lt(d,b): return other
                return

class CORange(BasicRange):
    """ An semi-open range [a,b) of a set S."""

    @classmethod
    def canonize(cls, (a, b, set)):
        if a==b: return a
        return BasicRange.canonize((a, b, set))
    def try_contains(self, other):
        if self.a==other: return self.superset.contains(other)
        if self.b==other: return False
        return super(CORange, self).try_contains(other)
    def try_supremum(self):
        if self.domain==Integers:
            return self.b-1
        return self.b
    def try_infimum(self):
        return self.a
    def try_positive(self):
        return OORange(0, self.b, self.superset)
    def try_negative(self):
        return self.__class__(self.a, 0, self.superset)
    def try_complementary(self, superset):
        if self.superset==superset:
            if self.is_unbounded_right:
                return OORange(Basic.Min(superset),self.a, superset)
            assert not self.is_unbounded_left,`self`
    def try_union(self, other):
        if not other.is_BasicRange:
            return
        a,b,d1 = self[:]
        c,d,d2 = other[:]
        if not d1==d2:
            return
        superset = d1
        if eq(b, c):
            if other.is_OORange or other.is_OCRange:
                # [a,b) U (b,d), [a,b) U (b,d]
                return
            if other.is_CORange:
                # [a,b) U [b,d)
                return CORange(a, d, superset)
            if other.is_CCRange:
                # [a,b) U [b,d]
                return CCRange(a, d, superset)
        if le(a, c):
            # code below assumes a<=c for simplicity
            if other.is_OORange:
                # [a,b) U (c,d)
                if lt(c, b):
                    if le(d, b): return self
                    if lt(b, d): return CORange(a, d, superset)
                return
            if other.is_OCRange:
                # [a,b) U (c,d]
                if lt(c, b):
                    if lt(d, b): return self
                    if le(b, d): return CCRange(a, d, superset)
                return
            if other.is_CORange:
                # [a,b) U [c,d)
                if le(c, b):
                    if le(d, b): return self
                    if lt(b, d): return CORange(a, d, superset)
                return
            if other.is_CCRange:
                # [a,b) U [c,d]
                if le(c, b):
                    if lt(d, b): return self
                    if le(b, d): return CCRange(a, d, superset)
                    return
            return
    def try_intersection(self, other):
        if not other.is_BasicRange:
            return
        a,b,d1 = self[:]
        c,d,d2 = other[:]
        if not d1==d2:
            return
        superset = d1
        if eq(b, c):
            # [a,b) A (b,d), [a,b) A (b,d], [a,b) A [b,d), [a,b) A [b,d] 
            return Empty
        if le(a, c):
            # code below assumes a<=c for simplicity
            if other.is_OORange:
                # [a,b) A (c,d)
                if le(b,c): return Empty
                if lt(c,b):
                    if le(b,d): return OORange(c,b,superset)
                    if lt(d,b): return other
                return
            if other.is_OCRange:
                # [a,b) A (c,d]
                if le(b,c): return Empty
                if lt(c,b):
                    if le(b,d): return OORange(c,b,superset)
                    if lt(d,b): return other
                return
            if other.is_CORange:
                # [a,b) A [c,d)
                if lt(b,c): return Empty
                if lt(c,b):
                    if le(b,d): return CORange(c,b,superset)
                    if lt(d,b): return other
                return
            if other.is_CCRange:
                # [a,b) A [c,d]
                if lt(b,c): return Empty
                if lt(c,b):
                    if le(b,d): return CORange(c,b,superset)
                    if lt(d,b): return other
                return

class CCRange(BasicRange):
    """ An closed range [a,b] of a set S."""

    @classmethod
    def canonize(cls, (a, b, set)):
        if a==b: return b
        return BasicRange.canonize((a, b, set))
    def try_contains(self, other):
        if self.a==other: return self.superset.contains(other)
        if self.b==other: return self.superset.contains(other)
        return super(CCRange, self).try_contains(other)
    def try_supremum(self):
        return self.b
    def try_infimum(self):
        return self.a
    def try_positive(self):
        return OCRange(0, self.b, self.superset)
    def try_negative(self):
        return CORange(self.a, 0, self.superset)
    def try_complementary(self, superset):
        if self.superset==superset:
            assert not self.is_unbounded_left,`self`
            assert not self.is_unbounded_right,`self`
    def try_union(self, other):
        if not other.is_BasicRange:
            return
        a,b,d1 = self[:]
        c,d,d2 = other[:]
        if not d1==d2:
            return
        superset = d1
        if eq(b, c):
            if other.is_OORange or other.is_CORange:
                # [a,b] U (b,d), [a,b] U [b,d)
                return CORange(a, d, superset)
            if other.is_CCRange or other.is_OCRange:
                # [a,b] U [b,d], [a,b] U (b,d]
                return CCRange(a, d, superset)
        if le(a, c):
            # code below assumes a<=c for simplicity
            if other.is_OORange:
                # [a,b] U (c,d)
                if le(c, b):
                    if le(d, b): return self
                    if lt(b, d): return CORange(a, d, superset)
                return
            if other.is_OCRange:
                # [a,b] U (c,d]
                if le(c, b):
                    if le(d, b): return self
                    if lt(b, d): return CCRange(a, d, superset)
                return
            if other.is_CORange:
                # [a,b] U [c,d)
                if le(c, b):
                    if le(d, b): return self
                    if lt(b, d): return CORange(a, d, superset)
                return
            if other.is_CCRange:
                # [a,b] U [c,d]
                if le(c, b):
                    if le(d, b): return self
                    if lt(b, d): return CCRange(a, d, superset)
                    return
            return
    def try_intersection(self, other):
        if not other.is_BasicRange:
            return
        a,b,d1 = self[:]
        c,d,d2 = other[:]
        if not d1==d2:
            return
        superset = d1
        if eq(b, c):
            # [a,b] A (b,d), [a,b] A (b,d]
            if other.is_OORange or other.is_OCRange:
                return Empty
            # [a,b] A [b,d), [a,b] A [b,d]
            return Set(b)
        if le(a, c):
            # code below assumes a<=c for simplicity
            if other.is_OORange:
                # [a,b] A (c,d)
                if lt(b,c): return Empty
                if le(c,b):
                    if lt(b,d): return OCRange(c,b,superset)
                    if le(d,b): return other
                return
            if other.is_OCRange:
                # [a,b] A (c,d]
                if lt(b,c): return Empty
                if le(c,b):
                    if le(b,d): return OCRange(c,b,superset)
                    if lt(d,b): return other
                return
            if other.is_CORange:
                # [a,b] A [c,d)
                if lt(b,c): return Empty
                if lt(c,b):
                    if le(b,d): return CCRange(c,b,superset)
                    if lt(d,b): return other
                return
            if other.is_CCRange:
                # [a,b] A [c,d]
                if lt(b,c): return Empty
                if lt(c,b):
                    if le(b,d): return CCRange(c,b,superset)
                    if lt(d,b): return other
                return

class Range(OORange):
    """ An open range (a,b) of a set S (default=Reals).
    """
    def __new__(cls, a, b, set=None):
        if set is None:
            set = Reals
        return OORange(a, b, set)

