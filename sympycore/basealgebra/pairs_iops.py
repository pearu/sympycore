"""
This file is generated by the src/mk_pairs_iops.py script.
See http://sympycore.googlecode.com/ for more information.

DO NOT CHANGE THIS FILE DIRECTLY!!!
"""

from ..arithmetic.numbers import Complex, Float, FractionTuple, try_power
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

def return_factors(cls, pairs, new=object.__new__):
    if not pairs:
        return cls.one
    elif len(pairs)==1:
        t, c = pairs.items()[0]
        if c==1:
            return t
        if t==cls.one:
            return t
    #RETURN_NEW(HEAD=FACTORS; DATA=pairs)
    #NEWINSTANCE(OBJ=_tmp16; HEAD=FACTORS; DATA=pairs)
    _tmp16 = new(cls)
    _tmp16.head = FACTORS
    _tmp16.data = pairs
    return _tmp16

def inplace_add(cls, obj, pairs, pairs_get, one):
    tobj = type(obj)
    if tobj is cls:
        head = obj.head
        if head is NUMBER:
            value = obj.data
            if value:
                #ADD_TERM_VALUE_DICT(DICT=pairs; DICT_GET=pairs_get; TERM=one; VALUE=value; SIGN=+; USIGN=)
                _tmp30 = pairs_get(one)
                if _tmp30 is None:
                    pairs[one] =  value
                else:
                    _tmp30 = _tmp30 + value
                    if _tmp30:
                        pairs[one] = _tmp30
                    else:
                        del pairs[one]
        elif head is TERMS:
            for t,c in obj.data.iteritems():
                #ADD_TERM_VALUE_DICT(DICT=pairs; DICT_GET=pairs_get; TERM=t; VALUE=c; SIGN=+; USIGN=)
                _tmp37 = pairs_get(t)
                if _tmp37 is None:
                    pairs[t] =  c
                else:
                    _tmp37 = _tmp37 + c
                    if _tmp37:
                        pairs[t] = _tmp37
                    else:
                        del pairs[t]
        else:
            #ADD_TERM_VALUE_DICT(DICT=pairs; DICT_GET=pairs_get; TERM=obj; VALUE=1; SIGN=+; USIGN=)
            _tmp44 = pairs_get(obj)
            if _tmp44 is None:
                pairs[obj] =  1
            else:
                _tmp44 = _tmp44 + 1
                if _tmp44:
                    pairs[obj] = _tmp44
                else:
                    del pairs[obj]
    #ELIF_CHECK_NUMBER(T=tobj)
    elif tobj is int or tobj is long or tobj is FractionTuple or tobj is float or tobj is Float or tobj is Complex or tobj is complex:
        if obj:
            #ADD_TERM_VALUE_DICT(DICT=pairs; DICT_GET=pairs_get; TERM=one; VALUE=obj; SIGN=+; USIGN=)
            _tmp58 = pairs_get(one)
            if _tmp58 is None:
                pairs[one] =  obj
            else:
                _tmp58 = _tmp58 + obj
                if _tmp58:
                    pairs[one] = _tmp58
                else:
                    del pairs[one]
    else:
        inplace_add(cls, cls.convert(obj), pairs, pairs_get, one)

def inplace_add2(cls, obj, coeff, pairs, pairs_get, one):
    if not coeff:
        return
    tobj = type(obj)
    if tobj is cls:
        head = obj.head
        if head is NUMBER:
            value = coeff * obj.data
            if value:
                #ADD_TERM_VALUE_DICT(DICT=pairs; DICT_GET=pairs_get; TERM=one; VALUE=value; SIGN=+; USIGN=)
                _tmp65 = pairs_get(one)
                if _tmp65 is None:
                    pairs[one] =  value
                else:
                    _tmp65 = _tmp65 + value
                    if _tmp65:
                        pairs[one] = _tmp65
                    else:
                        del pairs[one]
        elif head is TERMS:
            for t,c in obj.data.iteritems():
                #ADD_TERM_VALUE_DICT(DICT=pairs; DICT_GET=pairs_get; TERM=t; VALUE=coeff*c; SIGN=+; USIGN=)
                _tmp72 = pairs_get(t)
                if _tmp72 is None:
                    pairs[t] =  coeff*c
                else:
                    _tmp72 = _tmp72 + coeff*c
                    if _tmp72:
                        pairs[t] = _tmp72
                    else:
                        del pairs[t]
        else:
            #ADD_TERM_VALUE_DICT(DICT=pairs; DICT_GET=pairs_get; TERM=obj; VALUE=coeff; SIGN=+; USIGN=)
            _tmp79 = pairs_get(obj)
            if _tmp79 is None:
                pairs[obj] =  coeff
            else:
                _tmp79 = _tmp79 + coeff
                if _tmp79:
                    pairs[obj] = _tmp79
                else:
                    del pairs[obj]
    #ELIF_CHECK_NUMBER(T=tobj)
    elif tobj is int or tobj is long or tobj is FractionTuple or tobj is float or tobj is Float or tobj is Complex or tobj is complex:
        value = coeff * obj
        if value:
            #ADD_TERM_VALUE_DICT(DICT=pairs; DICT_GET=pairs_get; TERM=one; VALUE=value; SIGN=+; USIGN=)
            _tmp93 = pairs_get(one)
            if _tmp93 is None:
                pairs[one] =  value
            else:
                _tmp93 = _tmp93 + value
                if _tmp93:
                    pairs[one] = _tmp93
                else:
                    del pairs[one]
    else:
        inplace_add2(cls, cls.convert(obj), coeff, pairs, pairs_get, one)

def inplace_sub(cls, obj, pairs, pairs_get, one):
    tobj = type(obj)
    if tobj is cls:
        head = obj.head
        if head is NUMBER:
            value = obj.data
            if value:
                #ADD_TERM_VALUE_DICT(DICT=pairs; DICT_GET=pairs_get; TERM=one; VALUE=value; SIGN=-; USIGN=-)
                _tmp100 = pairs_get(one)
                if _tmp100 is None:
                    pairs[one] = - value
                else:
                    _tmp100 = _tmp100 - value
                    if _tmp100:
                        pairs[one] = _tmp100
                    else:
                        del pairs[one]
        elif HEAD is TERMS:
            for t,c in obj.data.iteritems():
                #ADD_TERM_VALUE_DICT(DICT=pairs; DICT_GET=pairs_get; TERM=t; VALUE=c; SIGN=-; USIGN=-)
                _tmp107 = pairs_get(t)
                if _tmp107 is None:
                    pairs[t] = - c
                else:
                    _tmp107 = _tmp107 - c
                    if _tmp107:
                        pairs[t] = _tmp107
                    else:
                        del pairs[t]
        else:
            #ADD_TERM_VALUE_DICT(DICT=pairs; DICT_GET=pairs_get; TERM=obj; VALUE=1; SIGN=-; USIGN=-)
            _tmp114 = pairs_get(obj)
            if _tmp114 is None:
                pairs[obj] = - 1
            else:
                _tmp114 = _tmp114 - 1
                if _tmp114:
                    pairs[obj] = _tmp114
                else:
                    del pairs[obj]
    #ELIF_CHECK_NUMBER(T=tobj)
    elif tobj is int or tobj is long or tobj is FractionTuple or tobj is float or tobj is Float or tobj is Complex or tobj is complex:
        if obj:
            #ADD_TERM_VALUE_DICT(DICT=pairs; DICT_GET=pairs_get; TERM=one; VALUE=obj; SIGN=-; USIGN=-)
            _tmp128 = pairs_get(one)
            if _tmp128 is None:
                pairs[one] = - obj
            else:
                _tmp128 = _tmp128 - obj
                if _tmp128:
                    pairs[one] = _tmp128
                else:
                    del pairs[one]
    else:
        inplace_add(cls, cls.convert(obj), pairs, pairs_get, one)

def inplace_mul(cls, obj, pairs, pairs_get, try_power=try_power, NUMBER=NUMBER):
    tobj = type(obj)
    if tobj is cls:
        head = obj.head
        if head is NUMBER:
            return obj.data
        elif head is TERMS:
            data = obj.data
            if len(data)==1:
                t, number = data.items()[0]
                #MUL_FACTOR_VALUE_DICT(DICT=pairs; DICT_GET=pairs_get; FACTOR=t; VALUE=1; SIGN=+; USIGN=; NUMBER=number)
                _tmp135 = pairs_get(t)
                if _tmp135 is None:
                    pairs[t] =  1
                else:
                    _tmp135 = _tmp135 + 1
                    if type(_tmp135) is cls and _tmp135.head is NUMBER:
                        _tmp135 = _tmp135.data
                    if _tmp135:
                        if t.head is NUMBER:
                            del pairs[t]
                            z, sym = try_power(t.data, _tmp135)
                            if sym:
                                for t1, c1 in sym:
                                    #NEWINSTANCE(OBJ=tt; HEAD=NUMBER; DATA=t1)
                                    tt = new(cls)
                                    tt.head = NUMBER
                                    tt.data = t1
                                    #ADD_TERM_VALUE_DICT(DICT=pairs; DICT_GET=pairs_get; TERM=tt; VALUE=c1; SIGN=+; USIGN=)
                                    _tmp149 = pairs_get(tt)
                                    if _tmp149 is None:
                                        pairs[tt] =  c1
                                    else:
                                        _tmp149 = _tmp149 + c1
                                        if _tmp149:
                                            pairs[tt] = _tmp149
                                        else:
                                            del pairs[tt]
                            number = number * z
                        else:
                            pairs[t] = _tmp135
                    else:
                        del pairs[t]
                return number
            number = 1
            #MUL_FACTOR_VALUE_DICT(DICT=pairs; DICT_GET=pairs_get; FACTOR=obj; VALUE=1; SIGN=+; USIGN=; NUMBER=number)
            _tmp156 = pairs_get(obj)
            if _tmp156 is None:
                pairs[obj] =  1
            else:
                _tmp156 = _tmp156 + 1
                if type(_tmp156) is cls and _tmp156.head is NUMBER:
                    _tmp156 = _tmp156.data
                if _tmp156:
                    if obj.head is NUMBER:
                        del pairs[obj]
                        z, sym = try_power(obj.data, _tmp156)
                        if sym:
                            for t1, c1 in sym:
                                #NEWINSTANCE(OBJ=tt; HEAD=NUMBER; DATA=t1)
                                tt = new(cls)
                                tt.head = NUMBER
                                tt.data = t1
                                #ADD_TERM_VALUE_DICT(DICT=pairs; DICT_GET=pairs_get; TERM=tt; VALUE=c1; SIGN=+; USIGN=)
                                _tmp170 = pairs_get(tt)
                                if _tmp170 is None:
                                    pairs[tt] =  c1
                                else:
                                    _tmp170 = _tmp170 + c1
                                    if _tmp170:
                                        pairs[tt] = _tmp170
                                    else:
                                        del pairs[tt]
                        number = number * z
                    else:
                        pairs[obj] = _tmp156
                else:
                    del pairs[obj]
            return number
        elif head is FACTORS:
            number = 1
            for t, c in obj.data.iteritems():
                #MUL_FACTOR_VALUE_DICT(DICT=pairs; DICT_GET=pairs_get; FACTOR=t; VALUE=c; SIGN=+; USIGN=; NUMBER=number)
                _tmp177 = pairs_get(t)
                if _tmp177 is None:
                    pairs[t] =  c
                else:
                    _tmp177 = _tmp177 + c
                    if type(_tmp177) is cls and _tmp177.head is NUMBER:
                        _tmp177 = _tmp177.data
                    if _tmp177:
                        if t.head is NUMBER:
                            del pairs[t]
                            z, sym = try_power(t.data, _tmp177)
                            if sym:
                                for t1, c1 in sym:
                                    #NEWINSTANCE(OBJ=tt; HEAD=NUMBER; DATA=t1)
                                    tt = new(cls)
                                    tt.head = NUMBER
                                    tt.data = t1
                                    #ADD_TERM_VALUE_DICT(DICT=pairs; DICT_GET=pairs_get; TERM=tt; VALUE=c1; SIGN=+; USIGN=)
                                    _tmp191 = pairs_get(tt)
                                    if _tmp191 is None:
                                        pairs[tt] =  c1
                                    else:
                                        _tmp191 = _tmp191 + c1
                                        if _tmp191:
                                            pairs[tt] = _tmp191
                                        else:
                                            del pairs[tt]
                            number = number * z
                        else:
                            pairs[t] = _tmp177
                    else:
                        del pairs[t]
            return number
        else:
            number = 1
            #MUL_FACTOR_VALUE_DICT(DICT=pairs; DICT_GET=pairs_get; FACTOR=obj; VALUE=1; SIGN=+; USIGN=; NUMBER=number)
            _tmp198 = pairs_get(obj)
            if _tmp198 is None:
                pairs[obj] =  1
            else:
                _tmp198 = _tmp198 + 1
                if type(_tmp198) is cls and _tmp198.head is NUMBER:
                    _tmp198 = _tmp198.data
                if _tmp198:
                    if obj.head is NUMBER:
                        del pairs[obj]
                        z, sym = try_power(obj.data, _tmp198)
                        if sym:
                            for t1, c1 in sym:
                                #NEWINSTANCE(OBJ=tt; HEAD=NUMBER; DATA=t1)
                                tt = new(cls)
                                tt.head = NUMBER
                                tt.data = t1
                                #ADD_TERM_VALUE_DICT(DICT=pairs; DICT_GET=pairs_get; TERM=tt; VALUE=c1; SIGN=+; USIGN=)
                                _tmp212 = pairs_get(tt)
                                if _tmp212 is None:
                                    pairs[tt] =  c1
                                else:
                                    _tmp212 = _tmp212 + c1
                                    if _tmp212:
                                        pairs[tt] = _tmp212
                                    else:
                                        del pairs[tt]
                        number = number * z
                    else:
                        pairs[obj] = _tmp198
                else:
                    del pairs[obj]
            return number
    #ELIF_CHECK_NUMBER(T=tobj)
    elif tobj is int or tobj is long or tobj is FractionTuple or tobj is float or tobj is Float or tobj is Complex or tobj is complex:
        return obj
    else:
        return inplace_mul(cls, cls.convert(obj), pairs, pairs_get)

def inplace_mul2(cls, obj, exp, pairs, pairs_get, try_power=try_power, NUMBER=NUMBER):
    if not exp:
        return 1
    tobj = type(obj)
    if tobj is cls:
        head = obj.head
        if head is NUMBER:
            return obj.data ** exp
        elif head is TERMS:
            data = obj.data
            if len(data)==1:
                t, number = data.items()[0]
                #MUL_FACTOR_VALUE_DICT(DICT=pairs; DICT_GET=pairs_get; FACTOR=t; VALUE=exp; SIGN=+; USIGN=; NUMBER=number)
                _tmp226 = pairs_get(t)
                if _tmp226 is None:
                    pairs[t] =  exp
                else:
                    _tmp226 = _tmp226 + exp
                    if type(_tmp226) is cls and _tmp226.head is NUMBER:
                        _tmp226 = _tmp226.data
                    if _tmp226:
                        if t.head is NUMBER:
                            del pairs[t]
                            z, sym = try_power(t.data, _tmp226)
                            if sym:
                                for t1, c1 in sym:
                                    #NEWINSTANCE(OBJ=tt; HEAD=NUMBER; DATA=t1)
                                    tt = new(cls)
                                    tt.head = NUMBER
                                    tt.data = t1
                                    #ADD_TERM_VALUE_DICT(DICT=pairs; DICT_GET=pairs_get; TERM=tt; VALUE=c1; SIGN=+; USIGN=)
                                    _tmp240 = pairs_get(tt)
                                    if _tmp240 is None:
                                        pairs[tt] =  c1
                                    else:
                                        _tmp240 = _tmp240 + c1
                                        if _tmp240:
                                            pairs[tt] = _tmp240
                                        else:
                                            del pairs[tt]
                            number = number * z
                        else:
                            pairs[t] = _tmp226
                    else:
                        del pairs[t]
                return number
            number = 1
            #MUL_FACTOR_VALUE_DICT(DICT=pairs; DICT_GET=pairs_get; FACTOR=obj; VALUE=exp; SIGN=+; USIGN=; NUMBER=number)
            _tmp247 = pairs_get(obj)
            if _tmp247 is None:
                pairs[obj] =  exp
            else:
                _tmp247 = _tmp247 + exp
                if type(_tmp247) is cls and _tmp247.head is NUMBER:
                    _tmp247 = _tmp247.data
                if _tmp247:
                    if obj.head is NUMBER:
                        del pairs[obj]
                        z, sym = try_power(obj.data, _tmp247)
                        if sym:
                            for t1, c1 in sym:
                                #NEWINSTANCE(OBJ=tt; HEAD=NUMBER; DATA=t1)
                                tt = new(cls)
                                tt.head = NUMBER
                                tt.data = t1
                                #ADD_TERM_VALUE_DICT(DICT=pairs; DICT_GET=pairs_get; TERM=tt; VALUE=c1; SIGN=+; USIGN=)
                                _tmp261 = pairs_get(tt)
                                if _tmp261 is None:
                                    pairs[tt] =  c1
                                else:
                                    _tmp261 = _tmp261 + c1
                                    if _tmp261:
                                        pairs[tt] = _tmp261
                                    else:
                                        del pairs[tt]
                        number = number * z
                    else:
                        pairs[obj] = _tmp247
                else:
                    del pairs[obj]
            return number
        elif head is FACTORS:
            number = 1
            for t, c in obj.data.iteritems():
                #MUL_FACTOR_VALUE_DICT(DICT=pairs; DICT_GET=pairs_get; FACTOR=t; VALUE=c*exp; SIGN=+; USIGN=; NUMBER=number)
                _tmp268 = pairs_get(t)
                if _tmp268 is None:
                    pairs[t] =  c*exp
                else:
                    _tmp268 = _tmp268 + c*exp
                    if type(_tmp268) is cls and _tmp268.head is NUMBER:
                        _tmp268 = _tmp268.data
                    if _tmp268:
                        if t.head is NUMBER:
                            del pairs[t]
                            z, sym = try_power(t.data, _tmp268)
                            if sym:
                                for t1, c1 in sym:
                                    #NEWINSTANCE(OBJ=tt; HEAD=NUMBER; DATA=t1)
                                    tt = new(cls)
                                    tt.head = NUMBER
                                    tt.data = t1
                                    #ADD_TERM_VALUE_DICT(DICT=pairs; DICT_GET=pairs_get; TERM=tt; VALUE=c1; SIGN=+; USIGN=)
                                    _tmp282 = pairs_get(tt)
                                    if _tmp282 is None:
                                        pairs[tt] =  c1
                                    else:
                                        _tmp282 = _tmp282 + c1
                                        if _tmp282:
                                            pairs[tt] = _tmp282
                                        else:
                                            del pairs[tt]
                            number = number * z
                        else:
                            pairs[t] = _tmp268
                    else:
                        del pairs[t]
            return number
        else:
            number = 1
            #MUL_FACTOR_VALUE_DICT(DICT=pairs; DICT_GET=pairs_get; FACTOR=obj; VALUE=exp; SIGN=+; USIGN=; NUMBER=number)
            _tmp289 = pairs_get(obj)
            if _tmp289 is None:
                pairs[obj] =  exp
            else:
                _tmp289 = _tmp289 + exp
                if type(_tmp289) is cls and _tmp289.head is NUMBER:
                    _tmp289 = _tmp289.data
                if _tmp289:
                    if obj.head is NUMBER:
                        del pairs[obj]
                        z, sym = try_power(obj.data, _tmp289)
                        if sym:
                            for t1, c1 in sym:
                                #NEWINSTANCE(OBJ=tt; HEAD=NUMBER; DATA=t1)
                                tt = new(cls)
                                tt.head = NUMBER
                                tt.data = t1
                                #ADD_TERM_VALUE_DICT(DICT=pairs; DICT_GET=pairs_get; TERM=tt; VALUE=c1; SIGN=+; USIGN=)
                                _tmp303 = pairs_get(tt)
                                if _tmp303 is None:
                                    pairs[tt] =  c1
                                else:
                                    _tmp303 = _tmp303 + c1
                                    if _tmp303:
                                        pairs[tt] = _tmp303
                                    else:
                                        del pairs[tt]
                        number = number * z
                    else:
                        pairs[obj] = _tmp289
                else:
                    del pairs[obj]
            return number
    #ELIF_CHECK_NUMBER(T=tobj)
    elif tobj is int or tobj is long or tobj is FractionTuple or tobj is float or tobj is Float or tobj is Complex or tobj is complex:
        return obj ** exp
    else:
        return inplace_mul2(cls, cls.convert(obj), exp, pairs, pairs_get)

    
