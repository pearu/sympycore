""" Provides the implementation of CollectingField.expand method.
"""

__all__ = ['expand']

__docformat__ = "restructuredtext"

from ..core import Expr
from ..arithmetic.number_theory import multinomial_coefficients
from ..utils import NUMBER, TERMS, FACTORS
from .pairs_iops import inplace_add2, return_terms, return_factors
from .pairs_ops import expand_mul_method

def expand(self):
    """ Return self as expanded expression.

    Integers powers and products of sums are expanded.
    """
    head = self.head
    if head is TERMS:
        return expand_TERMS(type(self), self, self.one)
    if head is FACTORS:
        return expand_FACTORS(type(self), self, self.one)
    return self

def expand_TERMS(cls, self, one):
    data = self.data
    d = {}
    d_get = d.get
    for t, c in data.iteritems():
        h = t.head
        if h is TERMS:
            t = expand_TERMS(cls, t, one)
        elif h is FACTORS:
            t = expand_FACTORS(cls, t, one)
        inplace_add2(cls, t, c, d, d_get, one)
    return return_terms(cls, d)

def expand_FACTORS(cls, self, one):
    ed = None
    for t, c in self.data.iteritems():
        h = t.head
        tc = type(c)
        if not (h is TERMS and (tc is int or tc is long) and c > 0):
            if c is not 1:
                t = t**c
            if ed is None:
                ed = {t: 1}
            else:
                d = {}
                for t2, c2 in ed.iteritems():
                    d[expand_mul_method(cls, t, t2)] = c2
                ed = d
            continue
        if h is TERMS:
            t = expand_TERMS(cls, t, one)
            h = t.head
        elif h is FACTORS:
            t = expand_FACTORS(cls, t, one)
            h = t.head
        assert h is TERMS,`t`
        if c > 1:
            terms = t.data.items()
            mdata = multinomial_coefficients(len(terms), c)
            d = {}
            t = cls(TERMS, d)
            for exps, n in mdata.iteritems():
                d1 = {}
                t1 = cls(FACTORS, d1)
                t1_add_item = t1._add_item
                t1_add_dict = t1._add_dict
                t1_add_dict2 = t1._add_dict2
                for i,e in enumerate(exps):
                    if not e:
                        continue
                    t2, c2 = terms[i]
                    h2, d2 = t2.pair
                    if h2 is NUMBER:
                        assert d2==1,`t2`
                    elif h2 is FACTORS:
                        t1_add_dict(d2) if e is 1 else t1_add_dict2(d2, e)
                    else:
                        t1_add_item(t2, e)
                    if c2 is not 1:
                        n *= c2 if e is 1 else c2**e
                l1 = len(d1)
                if l1==0:
                    t1 = one
                elif l1==1:
                    t2, c2 = d1.items()[0]
                    if c2==1 or t2==one:
                        t1 = t2
                t._add_item(t1, n)
            if len(d)<=1:
                t = return_terms(cls, d)
        h, data = t.pair
        if ed is None:
            if h is TERMS:
                ed = data.copy()
            elif h is NUMBER:
                ed = {one: data}
            else:
                ed = {t: 1}
        elif h is TERMS:
            if len(data) > len(ed):
                iter1 = data.iteritems
                iter2 = ed.iteritems
                dict1,dict2 = data,ed
            else:
                iter2 = data.iteritems
                iter1 = ed.iteritems
                dict1,dict2 = ed,data
            d = {}
            tmp = cls(TERMS, d)
            add_item = tmp._add_item
            for t1, c1 in iter1():
                head1, data1 = t1.pair
                if head1 is FACTORS:
                    for t2, c2 in iter2():
                        head2, data2 = t2.pair
                        if head2 is FACTORS:
                            d12 = data1.copy()
                            t12 = cls(FACTORS, d12)
                            num = t12._add_dict3(data2)
                            if len(d12)<=1:
                                if not d12:
                                    t12 = one
                                else:
                                    tt, cc = d12.items()[0]
                                    if cc==1:
                                        t12 = tt
                                    elif tt==one:
                                        t12 = tt
                            if num is None or num is 1:
                                add_item(t12, c1*c2)
                            else:
                                add_item(t12, num*c1*c2)
                        elif head2 is NUMBER:
                            # data2 must be 1
                            add_item(t1, c1*c2)
                        else:
                            t12 = expand_mul_method(cls, t1, t2)
                            add_item(t12, c1*c2)
                elif head1 is NUMBER:
                    # data1 must be 1
                    tmp._add_dict2(dict2, c1)
                else:
                    for t2, c2 in iter2():
                        head2, data2 = t2.pair
                        t12 = expand_mul_method(cls, t1, t2)
                        add_item(t12, c1*c2)
            ed = d
        elif h is NUMBER:
            b = ed.get(one)
            if b is None:
                ed[one] = data
            else:
                c1 = b + data
                if c1:
                    ed[one] = c1
                else:
                    del ed[one]
        else:
            d = {}
            for t2, c2 in ed.iteritems():
                d[expand_mul_method(cls, t, t2)] = c2
            ed = d
    if ed is None:
        return cls.one
    result = return_terms(cls, ed)
    return result

    
