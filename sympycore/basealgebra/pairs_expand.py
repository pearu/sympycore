
from ..arithmetic.numbers import Complex, Float, FractionTuple, try_power
from ..arithmetic.number_theory import multinomial_coefficients
from ..utils import SYMBOL, NUMBER, TERMS, FACTORS
from .pairs_iops import inplace_add2, inplace_add, return_terms, inplace_mul2, return_factors, inplace_mul

def newinstance(cls, head, data, new = object.__new__):
    o = new(cls)
    o.head = head
    o.data = data
    return o

def expand(self):
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
                d_get = d.get
                for t2, c2 in ed.iteritems():
                    inplace_add2(cls, t * t2, c2, d, d_get, one)
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
                for (t1, c1), e in zip(terms, exps):
                    num = inplace_mul2(cls, t1, e, d1, d1_get)
                    n = n * num * c1**e
                t1 = return_factors(cls, d1)
                inplace_add2(cls, t1, n, d, d_get, one)
            t = return_terms(cls, d)
            h = t.head
        if ed is None:
            if h is TERMS:
                ed = dict(t.data)
            elif h is NUMBER:
                ed = {one: t.data}
            else:
                ed = {t: 1}
        elif h is TERMS:
            d = {}
            d_get = d.get
            for t1, c1 in t.data.iteritems():
                for t2, c2 in ed.iteritems():
                    inplace_add2(cls, t1*t2, c1*c2, d, d_get, one)
            ed = d
        elif h is NUMBER:
            b = ed.get(one)
            if b is None:
                ed[one] = t.data
            else:
                c1 = b + t.data
                if c1:
                    ed[one] = c1
                else:
                    del ed[one]
        else:
            d = {}
            d_get = d.get
            for t2, c2 in ed.iteritems():
                d[t * t2] = c2
                #inplace_add2(cls, t * t2, c2, d, d_get, one)
            ed = d
    if ed is None:
        return cls.one
    return return_terms(cls, ed)

    
