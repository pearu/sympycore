"""
This file is generated by the sympycore/basealgebra/mk_pairs_iops.py script.
DO NOT CHANGE THIS FILE DIRECTLY!!!
"""

from ..arithmetic.numbers import Complex, Float, FractionTuple
from ..utils import NUMBER, TERMS, FACTORS




def return_terms(cls, pairs, new=object.__new__):
    if not pairs:
        return cls.zero
    if len(pairs)==1:
        t, c = pairs.items()[0]
        if c==1:
            return t
        if t==cls.one:
            return cls.convert(c)
    #RETURN_NEW(HEAD=TERMS; DATA=pairs)
    #NEWINSTANCE(OBJ=_tmp2; HEAD=TERMS; DATA=pairs)
    _tmp2 = new(cls)
    _tmp2.head = TERMS
    _tmp2.data = pairs
    return _tmp2

def inplace_add(cls, obj, pairs, pairs_get, one):
    tobj = type(obj)
    if tobj is cls:
        head = obj.head
        if head is NUMBER:
            #ADD_TERM_VALUE_DICT(DICT=pairs; DICT_GET=pairs_get; TERM=one; VALUE=obj.data; SIGN=+)
            _tmp4 = pairs_get(one)
            if _tmp4 is None:
                pairs[one] = + obj.data
            else:
                _tmp4 = _tmp4 + obj.data
                if _tmp4:
                    pairs[one] = _tmp4
                else:
                    del pairs[one]
        elif head is TERMS:
            for t,c in obj.data.iteritems():
                #ADD_TERM_VALUE_DICT(DICT=pairs; DICT_GET=pairs_get; TERM=t; VALUE=c; SIGN=+)
                _tmp5 = pairs_get(t)
                if _tmp5 is None:
                    pairs[t] = + c
                else:
                    _tmp5 = _tmp5 + c
                    if _tmp5:
                        pairs[t] = _tmp5
                    else:
                        del pairs[t]
        else:
            #ADD_TERM_VALUE_DICT(DICT=pairs; DICT_GET=pairs_get; TERM=obj; VALUE=1; SIGN=+)
            _tmp6 = pairs_get(obj)
            if _tmp6 is None:
                pairs[obj] = + 1
            else:
                _tmp6 = _tmp6 + 1
                if _tmp6:
                    pairs[obj] = _tmp6
                else:
                    del pairs[obj]
    #ELIF_CHECK_NUMBER(T=tobj)
    elif tobj is int or tobj is long or tobj is FractionTuple or tobj is float or tobj is Float or tobj is Complex or tobj is complex:
        #ADD_TERM_VALUE_DICT(DICT=pairs; DICT_GET=pairs_get; TERM=one; VALUE=obj; SIGN=+)
        _tmp8 = pairs_get(one)
        if _tmp8 is None:
            pairs[one] = + obj
        else:
            _tmp8 = _tmp8 + obj
            if _tmp8:
                pairs[one] = _tmp8
            else:
                del pairs[one]
    else:
        inplace_add(cls, cls.convert(obj), pairs, pairs_get, one)


def inplace_sub(cls, obj, pairs, pairs_get, one):
    tobj = type(obj)
    if tobj is cls:
        head = obj.head
        if head is NUMBER:
            #ADD_TERM_VALUE_DICT(DICT=pairs; DICT_GET=pairs_get; TERM=one; VALUE=obj.data; SIGN=-)
            _tmp9 = pairs_get(one)
            if _tmp9 is None:
                pairs[one] = - obj.data
            else:
                _tmp9 = _tmp9 - obj.data
                if _tmp9:
                    pairs[one] = _tmp9
                else:
                    del pairs[one]
        elif HEAD is TERMS:
            for t,c in obj.data.iteritems():
                #ADD_TERM_VALUE_DICT(DICT=pairs; DICT_GET=pairs_get; TERM=t; VALUE=c; SIGN=-)
                _tmp10 = pairs_get(t)
                if _tmp10 is None:
                    pairs[t] = - c
                else:
                    _tmp10 = _tmp10 - c
                    if _tmp10:
                        pairs[t] = _tmp10
                    else:
                        del pairs[t]
        else:
            #ADD_TERM_VALUE_DICT(DICT=pairs; DICT_GET=pairs_get; TERM=obj; VALUE=1; SIGN=-)
            _tmp11 = pairs_get(obj)
            if _tmp11 is None:
                pairs[obj] = - 1
            else:
                _tmp11 = _tmp11 - 1
                if _tmp11:
                    pairs[obj] = _tmp11
                else:
                    del pairs[obj]
    #ELIF_CHECK_NUMBER(T=tobj)
    elif tobj is int or tobj is long or tobj is FractionTuple or tobj is float or tobj is Float or tobj is Complex or tobj is complex:
        #ADD_TERM_VALUE_DICT(DICT=pairs; DICT_GET=pairs_get; TERM=one; VALUE=obj; SIGN=-)
        _tmp13 = pairs_get(one)
        if _tmp13 is None:
            pairs[one] = - obj
        else:
            _tmp13 = _tmp13 - obj
            if _tmp13:
                pairs[one] = _tmp13
            else:
                del pairs[one]
    else:
        inplace_add(cls, cls.convert(obj), pairs, pairs_get, one)

    
