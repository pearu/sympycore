""" Provides the implementation of CollectingField.expand method.
"""

__all__ = ['expand']

__docformat__ = "restructuredtext"

from ..core import Expr
from ..arithmetic.number_theory import multinomial_coefficients
from ..utils import NUMBER, TERMS
from ..heads import BASE_EXP_DICT as FACTORS
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
    result = cls(TERMS, d)
    d_get = d.get
    for t, c in data.iteritems():
        h = t.head
        if h is TERMS:
            t = expand_TERMS(cls, t, one)
        elif h is FACTORS:
            t = expand_FACTORS(cls, t, one)
        inplace_add2(cls, t, c, d, d_get, one)
    return result.canonize_TERMS()

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
            t = cls(TERMS, {})
            t_add_item = t._add_item
            for exps, n in mdata.iteritems():
                t1 = cls(FACTORS, {})
                t1_add_item = t1._add_item
                t1_add_dict = t1._add_dict
                t1_add_dict2 = t1._add_dict2
                for i,e in enumerate(exps):
                    if e:
                        t2, c2 = terms[i]
                        h2, d2 = t2.pair
                        if h2 is NUMBER:
                            assert d2==1,`t2`
                        elif h2 is FACTORS:
                            if e is 1:
                                t1_add_dict(d2)
                            else:
                                t1_add_dict2(d2, e)
                        else:
                            t1_add_item(t2, e)
                        if c2 is not 1:
                            n *= c2 if e is 1 else c2**e
                t1 = t1.canonize_FACTORS()
                t_add_item(t1, n)
            t = t.canonize_TERMS()
        h, data = t.pair
        if ed is None:
            if h is TERMS:
                ed = data.copy()
            elif h is NUMBER:
                ed = {one: data}
            else:
                ed = {t: 1}
        elif h is TERMS:
            if len(data) < len(ed):
                iter1 = data.iteritems
                iter2 = ed.iteritems
                dict2 = ed
            else:
                iter2 = data.iteritems
                iter1 = ed.iteritems
                dict2 = data
            d = {}
            tmp = cls(TERMS, d)
            add_item = tmp._add_item
            add_dict2 = tmp._add_dict2
            for t1, c1 in iter1():
                head1, data1 = t1.pair
                if head1 is FACTORS:
                    data1_copy = data1.copy
                    for t2, c2 in iter2():
                        c12 = c1*c2
                        head2, data2 = t2.pair
                        if head2 is FACTORS:
                            t12 = cls(FACTORS, data1_copy())
                            num = t12._add_dict3(data2)
                            if num is not None:
                                c12 *= num
                            t12 = t12.canonize_FACTORS()
                        elif head2 is NUMBER:
                            # data2 must be 1
                            t12 = t1
                        else:
                            t12 = cls(FACTORS, data1_copy())
                            t12._add_item(t2, 1)
                            t12 = t12.canonize_FACTORS()
                        add_item(t12, c12)
                elif head1 is NUMBER:
                    # data1 must be 1
                    add_dict2(dict2, c1)
                else:
                    for t2, c2 in iter2():
                        head2, data2 = t2.pair
                        if head2 is FACTORS:
                            t12 = cls(FACTORS, data2.copy())
                            t12._add_item(t1, 1)
                            t12 = t12.canonize_FACTORS()
                        elif head2 is NUMBER:
                            # data2 must be 1
                            t12 = t1
                        else:
                            if t1==t2:
                                t12 = cls(FACTORS, {t1:2})
                            else:
                                t12 = cls(FACTORS, {t1:1, t2:1})
                        add_item(t12, c1 * c2)
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
        return one
    return cls(TERMS, ed).canonize_TERMS()
