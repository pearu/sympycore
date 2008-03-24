""" Collecting field opertions.
"""
# Author: Pearu Peterson
# Created: March 2008

from ..utils import TERMS, FACTORS, NUMBER
from ..arithmetic.numbers import numbertypes_set

__all__ = ['multiply', 'negate']

# FACTORS < TERMS < NUMBER < rest
_swap_args_set1 = frozenset([TERMS, FACTORS, NUMBER])
_swap_args_set = frozenset([(TERMS, FACTORS), (NUMBER, FACTORS), (NUMBER, TERMS)])

def negate(self):
    head1, data1 = self.pair
    if head1 is NUMBER:
        return type(self)(NUMBER, -data1)
    if head1 is TERMS:
        r = type(self)(TERMS, dict([(t,-c) for t,c in data1.iteritems()]))
        return r.canonize_TERMS() if len(data1)==1 else r
    return type(self)(TERMS, {self:-1})

def multiply(self, other):
    head1, data1 = self.pair
    t = type(other)
    cls = type(self)
    if t is not cls:
        if t in self.coefftypes_set:
            if head1 is NUMBER:
                return cls(NUMBER, data1 * other)
            if other == 1:
                return self
            if not other:
                return self.zero
            if head1 is FACTORS:
                return cls(TERMS, {self: other})
            if head1 is TERMS:
                if len(data1)==1:
                    t, c = data1.items()[0]
                    c = c * other
                    return t if c==1 else cls(TERMS, {t:c})
                return cls(TERMS, dict([(t, c*other) for t,c in data1.iteritems()]))
            return cls(TERMS, {self: other})        
        other = self.convert(other, False)
        if other is NotImplemented:
            return other
    head2, data2 = other.pair
    if not (head1 in _swap_args_set1) or (head1, head2) in _swap_args_set:
        head1, head2, data1, data2, self, other = head2, head1, data2, data1, other, self
    if head1 is FACTORS:
        if head2 is FACTORS:
            d = data1.copy()
            result = cls(FACTORS, d)
            num = result._add_dict3(data2)
            if len(d)<=1:
                result = result.canonize_FACTORS()
            if num is None or num==1:
                return result
            if result==self.one:
                return cls(NUMBER, num)
            return cls(TERMS, {result:num})
        elif head2 is TERMS:
            if len(data2)==1:
                t, c = data2.items()[0]
                t *= self
                if t==self.one:
                    return cls(NUMBER, c)
                return cls(TERMS, {t: c})
        elif head2 is NUMBER:
            if data2 == 1:
                return self
            if not data2:
                return other
            return cls(TERMS, {self: data2})
        d = data1.copy()
        result = cls(FACTORS, d)
        result._add_item(other, 1)
        return result.canonize_FACTORS() if len(d)<=1 else result
    elif head1 is TERMS:
        if len(data1)==1:
            t, c = data1.items()[0]
            if head2 is NUMBER:
                if data2 == 1:
                    return self
                if not data2:
                    return other                
                c = c * data2
                return t if c==1 else cls(TERMS, {t:c})
            if head2 is TERMS:
                if len(data2)==1:
                    t2, c2 = data2.items()[0]
                    t12 = t * t2
                    c12 = c * c2
                    if c12==1:
                        return t12
                    if t12==self.one:
                        return cls(NUMBER, c12)
                    return cls(TERMS, {t12: c12})
            return cls(TERMS, {t * other: c})
        if head2 is NUMBER:
            if data2 == 1:
                return self
            if not data2:
                return other                
            return cls(TERMS, dict([(t, c*data2) for t,c in data1.iteritems()]))
        if head2 is TERMS:
            if len(data2)==1:
                t2, c2 = data2.items()[0]
                t12 = self*t2
                if t12==self.one:
                    return cls(NUMBER, c2)
                return cls(TERMS, {t12: c2})
            if data1==data2:
                return cls(FACTORS, {self:2})
        return cls(FACTORS, {self:1, other:1})
    elif head1 is NUMBER:
        if data1 == 1:
            return other
        if not data1:
            return self
        if head2 is NUMBER:
            return cls(NUMBER, data1 * data2)
        return cls(TERMS, {other: data1})
    else:
        if self==other:
            return cls(FACTORS, {self:2})
        return cls(FACTORS, {self:1, other:1})
