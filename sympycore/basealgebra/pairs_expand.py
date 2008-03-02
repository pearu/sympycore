""" Provides the implementation of CommutativeAlgebraWithPairs.expand method.
"""

__all__ = ['expand']

__docformat__ = "restructuredtext"

from ..core import APair
from ..arithmetic.numbers import Complex, Float, FractionTuple, try_power
from ..arithmetic.number_theory import multinomial_coefficients
from ..utils import NUMBER, TERMS, FACTORS
from .pairs_iops import inplace_add2, return_terms, return_factors
from .pairs_ops import expand_mul_method

new = APair.__new__

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

def expand_FACTORS(cls, self, one, new = new):
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
            d = {}
            d_get = d.get
            terms = t.data.items()
            mdata = multinomial_coefficients(len(terms), c)
            for exps, n in mdata.iteritems():
                d1 = {}
                d1_get = d1.get
                for i,e in enumerate(exps):
                    if not e:
                        continue
                    t1, c1 = terms[i]
                    h1 = t1.head
                    if h1 is NUMBER:
                        assert t1.data==1,`t1`
                    elif h1 is FACTORS:
                        for t2, c2 in t1.data.iteritems():
                            b = d1_get(t2)
                            if b is None:
                                d1[t2] = e * c2
                            else:
                                b = b + e * c2
                                if b:
                                    d1[t2] = b
                                else:
                                    del d1[t2]
                    else:
                        b = d1_get(t1)
                        if b is None:
                            d1[t1] = e
                        else:
                            b = b + e
                            if b:
                                d1[t1] = b
                            else:
                                del d1[t1]
                    if c1 is not 1:
                        if e is 1:
                            n = n * c1
                        else:
                            n = n * c1**e
                if len(d1)>1:
                    t1 = new(cls, FACTORS, d1)
                else:
                    t1 = return_factors(cls, d1)
                b = d_get(t1)
                if b is None:
                    d[t1] = n
                else:
                    n = n + b
                    if n:
                        d[t1] = n
                    else:
                        del d[t1]
            if len(d)>1:
                t = new(cls, TERMS, d)
            else:
                t = return_terms(cls, d)
            h = t.head
        data = t.data
        if ed is None:
            if h is TERMS:
                ed = dict(data)
            elif h is NUMBER:
                ed = {one: data}
            else:
                ed = {t: 1}
        elif h is TERMS:
            d = {}
            d_get = d.get
            if len(data) > len(ed):
                iter1 = data.iteritems
                iter2 = ed.iteritems
            else:
                iter2 = data.iteritems
                iter1 = ed.iteritems
            for t1, c1 in iter1():
                for t2, c2 in iter2():
                    t = expand_mul_method(cls, t1, t2)
                    c = c1*c2
                    b = d_get(t)
                    if b is None:
                        d[t] = c
                    else:
                        c = b + c
                        if c:
                            d[t] = c
                        else:
                            del d[t]
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
            d_get = d.get
            for t2, c2 in ed.iteritems():
                d[expand_mul_method(cls, t, t2)] = c2
            ed = d
    if ed is None:
        return cls.one
    return return_terms(cls, ed)

    
