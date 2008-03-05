#!/usr/bin/env python
#
# Created by Pearu Peterson in Febuary 2008
#

import os

from macros import preprocess
cwd = os.path.abspath(os.path.dirname(__file__))
targetfile_py = os.path.join(cwd,'..','sympycore','basealgebra','pairs_ops.py')

template = '''\
"""Generated low-level arithmetic methods for CommutativeRingWithPairs.

This file is generated by the src/mk_pairs_ops.py script.
See http://sympycore.googlecode.com/ for more information.

DO NOT CHANGE THIS FILE DIRECTLY!!!
"""

from ..core import Expr
from ..utils import NUMBER, SYMBOL, TERMS, FACTORS
from ..arithmetic.numbers import (normalized_fraction,
  FractionTuple, try_power, numbertypes)
from ..arithmetic.infinity import Infinity

#new = Expr.__new__

def div(a, b, cls):
    tb = type(b)
    if tb is int or tb is long:
        ta = type(a)
        if ta is int or tb is long:
            if not b:
                if not a:
                    return cls.undefined
                return cls.zoo
            return normalized_fraction(a, b)
        if not b:
            return a * cls.zoo
        if b == 1:
            return a
        return a * FractionTuple((1,b))
    return a / b

'''

#======================================
# General macros
#======================================

RETURN_NEW2 = '''\
%(TMP)s = %(DATA)s
if isinstance(%(TMP)s, Infinity):
    return %(TMP)s
@RETURN_NEW(HEAD=%(HEAD)s; DATA=%(TMP)s)
'''

CANONIZE_TERMS_DICT = '''\
if not %(DICT)s:
    return cls.zero
if len(%(DICT)s)==1:
   t, c = %(DICT)s.items()[0]
   if c==1:
       return t
   if t==cls.one:
       return cls.convert(c)
'''

CANONIZE_FACTORS_DICT = '''\
if not %(DICT)s:
    if %(NUMBER)s is 1:
        return cls.one
    return %(NUMBER)s
if len(%(DICT)s)==1:
   t, c = %(DICT)s.items()[0]
   if c==1:
       if %(NUMBER)s==1:
           return t
       @RETURN_NEW(HEAD=TERMS; DATA={t: %(NUMBER)s})
   if t==cls.one:
       return %(NUMBER)s
'''

CANONIZE_FACTORS_DICT1 = '''\
if not %(DICT)s:
    return cls.one
if len(%(DICT)s)==1:
   t, c = %(DICT)s.items()[0]
   if c==1:
       return t
   if t==cls.one:
       return t
'''

ADD_VALUE_DICT='''\
@ADD_TERM_VALUE_DICT(TERM=cls.one; VALUE=%(VALUE)s; DICT=%(DICT)s; DICT_GET=%(DICT)s.get; SIGN=+; USIGN=)
'''

NEG_DICT_VALUES = '''\
%(DICT_OUT)s = dict([(t, -c) for t,c in %(DICT_IN)s.iteritems()])
'''
MUL_DICT_VALUES = '''\
%(DICT_OUT)s = dict([(t, c*%(OP)s) for t,c in %(DICT_IN)s.iteritems()])
'''

#======================================
# NEG macros
#======================================

NEG_NUMBER = '@RETURN_NEW(HEAD=NUMBER; DATA=-%(OPDATA)s)\n'
NEG_SYMBOL = '@RETURN_NEW(HEAD=TERMS; DATA={%(OP)s: -1})\n'
NEG_TERMS = '''\
op_pairs = %(OPDATA)s
if len(op_pairs)==1:
    t, c = op_pairs.items()[0]
    c = -c
    if c==1:
        return t
    @RETURN_NEW(HEAD=TERMS; DATA={t:c})
@NEG_DICT_VALUES(DICT_IN=%(OPDATA)s; DICT_OUT=pairs)
@RETURN_NEW(HEAD=TERMS; DATA=pairs)
'''
NEG_FACTORS = '@NEG_SYMBOL(OP=%(OP)s; OPDATA=%(OPDATA)s)\n'

#======================================
# ADD macros
#======================================

ADD_VALUE_NUMBER='@RETURN_NEW(HEAD=NUMBER; DATA=%(VALUE)s + %(RHSDATA)s)\n'
ADD_NUMBER_VALUE='@RETURN_NEW(HEAD=NUMBER; DATA=%(LHSDATA)s + %(VALUE)s)\n'
ADD_NUMBER_NUMBER = '@ADD_VALUE_NUMBER(VALUE=%(LHSDATA)s; RHS=%(RHS)s; RHSDATA=%(RHSDATA)s)\n'
ADD_VALUE_SYMBOL = '''\
%(TMP)s = %(VALUE)s
if not %(TMP)s:
    return %(RHS)s
@RETURN_NEW(HEAD=TERMS; DATA={cls.one: %(TMP)s, %(RHS)s: 1})
'''
ADD_SYMBOL_VALUE = '@ADD_VALUE_SYMBOL(VALUE=%(VALUE)s; RHS=%(LHS)s; RHSDATA=%(LHSDATA)s)\n'
ADD_NUMBER_SYMBOL = '@ADD_VALUE_SYMBOL(VALUE=%(LHSDATA)s; RHS=%(RHS)s; RHSDATA=%(RHSDATA)s)\n'
ADD_SYMBOL_NUMBER = '@ADD_SYMBOL_VALUE(VALUE=%(RHSDATA)s; LHS=%(LHS)s; LHSDATA=%(LHSDATA)s)\n'
ADD_SYMBOL_SYMBOL = '''\
if %(LHS)s == %(RHS)s:
    pairs = {%(LHS)s: 2}
else:
    pairs = {%(LHS)s: 1, %(RHS)s: 1}
@RETURN_NEW(HEAD=TERMS; DATA=pairs)
'''
ADD_VALUE_TERMS = '''\
%(TMP)s = %(VALUE)s
if not %(TMP)s:
    return %(RHS)s
pairs = dict(%(RHSDATA)s)
@ADD_VALUE_DICT(DICT=pairs; VALUE=%(TMP)s)
@RETURN_NEW(HEAD=TERMS; DATA=pairs)
'''
ADD_TERMS_VALUE = '@ADD_VALUE_TERMS(VALUE=%(VALUE)s; RHS=%(LHS)s; RHSDATA=%(LHSDATA)s)\n'
ADD_NUMBER_TERMS = '@ADD_VALUE_TERMS(VALUE=%(LHSDATA)s; RHS=%(RHS)s; RHSDATA=%(RHSDATA)s)\n'
ADD_TERMS_NUMBER = '@ADD_TERMS_VALUE(VALUE=%(RHSDATA)s; LHS=%(LHS)s; LHSDATA=%(LHSDATA)s)\n'

ADD_TERMS_SYMBOL = '''\
pairs = dict(%(LHSDATA)s)
@ADD_TERM_VALUE_DICT(TERM=%(RHS)s; VALUE=1; DICT=pairs; DICT_GET=pairs.get; SIGN=+; USIGN=)
@CANONIZE_TERMS_DICT(DICT=pairs)
@RETURN_NEW(HEAD=TERMS; DATA=pairs)
'''
ADD_SYMBOL_TERMS = '@ADD_TERMS_SYMBOL(LHS=%(RHS)s; LHSDATA=%(RHSDATA)s; RHS=%(LHS)s; RHSDATA=%(LHSDATA)s)\n'
ADD_TERMS_TERMS = '''\
pairs = dict(%(LHSDATA)s)
pairs_get = pairs.get
for t,c in %(RHSDATA)s.iteritems():
    @ADD_TERM_VALUE_DICT(TERM=t; VALUE=c; DICT=pairs; DICT_GET=pairs_get; SIGN=+; USIGN=)
@CANONIZE_TERMS_DICT(DICT=pairs)
@RETURN_NEW(HEAD=TERMS; DATA=pairs)
'''

#======================================
# SUB macros
#======================================

SUB_VALUE_NUMBER='@RETURN_NEW(HEAD=NUMBER; DATA=%(VALUE)s - %(RHSDATA)s)\n'
SUB_NUMBER_VALUE='@RETURN_NEW(HEAD=NUMBER; DATA=%(LHSDATA)s - %(VALUE)s)\n'
SUB_NUMBER_NUMBER = '@SUB_VALUE_NUMBER(VALUE=%(LHSDATA)s; RHS=%(RHS)s; RHSDATA=%(RHSDATA)s)\n'
SUB_VALUE_SYMBOL = '''\
%(TMP)s = %(VALUE)s
if not %(TMP)s:
    @RETURN_NEW(HEAD=TERMS; DATA={%(RHS)s: -1})
@RETURN_NEW(HEAD=TERMS; DATA={cls.one: %(TMP)s, %(RHS)s: -1})
'''
SUB_SYMBOL_VALUE = '@ADD_SYMBOL_VALUE(OBJ=obj; LHS=%(LHS)s; LHSDATA=%(LHSDATA)s; VALUE=-%(VALUE)s)\n'
SUB_NUMBER_SYMBOL = '@SUB_VALUE_SYMBOL(VALUE=%(LHSDATA)s; RHS=%(RHS)s; RHSDATA=%(RHSDATA)s)\n'
SUB_SYMBOL_NUMBER = '@SUB_SYMBOL_VALUE(VALUE=%(RHSDATA)s; LHS=%(LHS)s; LHSDATA=%(LHSDATA)s)\n'
SUB_SYMBOL_SYMBOL = '''\
if %(LHS)s == %(RHS)s:
    return cls.zero
@RETURN_NEW(HEAD=TERMS; DATA={%(LHS)s: 1, %(RHS)s: -1})
'''
SUB_VALUE_TERMS = '''\
%(TMP)s = %(VALUE)s
if not %(TMP)s:
    @NEG_TERMS(OP=%(RHS)s; OPDATA=%(RHSDATA)s)
@NEG_DICT_VALUES(DICT_IN=%(RHSDATA)s; DICT_OUT=pairs)
@ADD_VALUE_DICT(DICT=pairs; VALUE=%(TMP)s)
@RETURN_NEW(HEAD=TERMS; DATA=pairs)
'''
SUB_TERMS_VALUE = '@ADD_VALUE_TERMS(VALUE=-%(VALUE)s; RHS=%(LHS)s; RHSDATA=%(LHSDATA)s)\n'
SUB_NUMBER_TERMS = '@SUB_VALUE_TERMS(VALUE=%(LHSDATA)s; RHS=%(RHS)s; RHSDATA=%(RHSDATA)s)\n'
SUB_TERMS_NUMBER = '@SUB_TERMS_VALUE(VALUE=%(RHSDATA)s; LHS=%(LHS)s; LHSDATA=%(LHSDATA)s)\n'
SUB_TERMS_SYMBOL = '''\
pairs = dict(%(LHSDATA)s)
@ADD_TERM_VALUE_DICT(TERM=%(RHS)s; VALUE=-1; DICT=pairs; DICT_GET=pairs.get; SIGN=+; USIGN=)
@CANONIZE_TERMS_DICT(DICT=pairs)
@RETURN_NEW(HEAD=TERMS; DATA=pairs)
'''
SUB_SYMBOL_TERMS = '''\
@NEG_DICT_VALUES(DICT_IN=%(RHSDATA)s; DICT_OUT=pairs)
@ADD_TERM_VALUE_DICT(TERM=%(LHS)s; VALUE=1; DICT=pairs; DICT_GET=pairs.get; SIGN=+; USIGN=)
@CANONIZE_TERMS_DICT(DICT=pairs)
@RETURN_NEW(HEAD=TERMS; DATA=pairs)
'''
SUB_TERMS_TERMS = '''\
pairs = dict(%(LHSDATA)s)
pairs_get = pairs.get
for t,c in %(RHSDATA)s.iteritems():
    @ADD_TERM_VALUE_DICT(TERM=t; VALUE=-c; DICT=pairs; DICT_GET=pairs_get; SIGN=+; USIGN=)
@CANONIZE_TERMS_DICT(DICT=pairs)
@RETURN_NEW(HEAD=TERMS; DATA=pairs)
'''

#======================================
# MUL macros
#======================================

MUL_ZERO_OP = '''\
if not %(VALUE)s:
    return cls.zero
'''

MUL_VALUE_NUMBER='@RETURN_NEW(HEAD=NUMBER; DATA=%(VALUE)s * %(RHSDATA)s)\n'
MUL_NUMBER_VALUE='@RETURN_NEW(HEAD=NUMBER; DATA=%(LHSDATA)s * %(VALUE)s)\n'
MUL_NUMBER_NUMBER = '@MUL_VALUE_NUMBER(VALUE=%(LHSDATA)s; RHS=%(RHS)s; RHSDATA=%(RHSDATA)s)\n'
MUL_VALUE_SYMBOL = '''\
%(TMP)s = %(VALUE)s
if not %(TMP)s:
    return cls.zero
if %(TMP)s==1:
    return %(RHS)s
@RETURN_NEW(HEAD=TERMS; DATA={%(RHS)s: %(TMP)s})
'''
MUL_SYMBOL_VALUE = '@MUL_VALUE_SYMBOL(VALUE=%(VALUE)s; RHS=%(LHS)s; RHSDATA=%(LHSDATA)s)\n'
MUL_NUMBER_SYMBOL = '@MUL_VALUE_SYMBOL(VALUE=%(LHSDATA)s; RHS=%(RHS)s; RHSDATA=%(RHSDATA)s)\n'
MUL_SYMBOL_NUMBER = '@MUL_SYMBOL_VALUE(VALUE=%(RHSDATA)s; LHS=%(LHS)s; LHSDATA=%(LHSDATA)s)\n'
MUL_NUMBER_FACTORS = '@MUL_SYMBOL_VALUE(VALUE=%(LHSDATA)s; LHS=%(RHS)s; LHSDATA=%(RHSDATA)s)\n'
MUL_VALUE_FACTORS = '@MUL_SYMBOL_VALUE(VALUE=%(VALUE)s; LHS=%(RHS)s; LHSDATA=%(RHSDATA)s)\n'
MUL_FACTORS_NUMBER = '@MUL_SYMBOL_VALUE(VALUE=%(RHSDATA)s; LHS=%(LHS)s; LHSDATA=%(LHSDATA)s)\n'
MUL_FACTORS_VALUE = '@MUL_SYMBOL_VALUE(VALUE=%(VALUE)s; LHS=%(LHS)s; LHSDATA=%(LHSDATA)s)\n'
MUL_SYMBOL_SYMBOL = '''\
if %(LHS)s == %(RHS)s:
    pairs = {%(LHS)s: 2}
else:
    pairs = {%(LHS)s: 1, %(RHS)s: 1}
@RETURN_NEW(HEAD=FACTORS; DATA=pairs)
'''
MUL_VALUE_TERMS = '''\
%(TMP)s = %(VALUE)s
if not %(TMP)s:
    return cls.zero
pairs = %(RHSDATA)s
if len(pairs)==1:
    t, c = pairs.items()[0]
    c = %(TMP)s * c
    if c==1:
        return t
    @RETURN_NEW(HEAD=TERMS; DATA={t: c})
if %(TMP)s==1:
    return %(RHS)s
pairs = {}
for t,c in %(RHSDATA)s.iteritems():
    pairs[t] = %(TMP)s * c
@NEWINSTANCE(OBJ=obj; HEAD=TERMS; DATA=pairs)
coeff, terms = %(RHS)s._coeff_terms
if terms is not None:
    c = coeff * %(TMP)s
    if not c==1:
        obj._coeff_terms = (c, terms)
else:
    obj._coeff_terms = (%(TMP)s, %(RHS)s)
return obj
'''
MUL_TERMS_VALUE='@MUL_VALUE_TERMS(VALUE=%(VALUE)s; RHS=%(LHS)s; RHSDATA=%(LHSDATA)s)\n'
MUL_NUMBER_TERMS = '@MUL_VALUE_TERMS(VALUE=%(LHSDATA)s; RHS=%(RHS)s; RHSDATA=%(RHSDATA)s)\n'
MUL_TERMS_NUMBER = '@MUL_TERMS_VALUE(VALUE=%(RHSDATA)s; LHS=%(LHS)s; LHSDATA=%(LHSDATA)s)\n'
MUL_TERMS_SYMBOL = '''\
pairs = %(LHSDATA)s
if len(pairs)==1:
    t,c = pairs.items()[0]
    t = t * %(RHS)s
    if t==cls.one:
        return cls.convert(c)
    @RETURN_NEW(HEAD=TERMS; DATA={t: c})
coeff, terms = %(LHS)s._coeff_terms
if terms is not None:
    @NEWINSTANCE(OBJ=%(TMP)s; HEAD=FACTORS; DATA={terms:1, %(RHS)s:1})
    @RETURN_NEW(HEAD=TERMS; DATA={%(TMP)s:coeff})
@RETURN_NEW(HEAD=FACTORS; DATA={%(LHS)s: 1, %(RHS)s: 1})
'''
MUL_SYMBOL_TERMS = '@MUL_TERMS_SYMBOL(LHS=%(RHS)s; LHSDATA=%(RHSDATA)s; RHS=%(LHS)s; RHSDATA=%(LHSDATA)s)\n'
MUL_TERMS_TERMS = '''\
lpairs = %(LHSDATA)s
rpairs = %(RHSDATA)s
if len(lpairs)==1:
    t1,c1 = lpairs.items()[0]
    if len(rpairs)==1:
        t2,c2 = rpairs.items()[0]
        t = t1 * t2
        c = c1 * c2
        if t == cls.one:
            return cls.convert(c)
        if c==1:
            return t
        @RETURN_NEW(HEAD=TERMS; DATA={t: c})
    coeff, terms = %(RHS)s._coeff_terms
    if terms is None:
        return (t1 * %(RHS)s) * c1
    return (t1*terms) * (c1*coeff)
elif len(rpairs)==1:
    t1,c1 = rpairs.items()[0]
    coeff, terms = %(RHS)s._coeff_terms
    if terms is None:
        return (t1 * %(LHS)s) * c1
    return (t1*terms) * (c1*coeff)
lcoeff, lterms = %(LHS)s._coeff_terms
rcoeff, rterms = %(RHS)s._coeff_terms
if lterms is None:
    lterms = %(LHS)s
if rterms is None:
    rterms = %(RHS)s
if lterms==rterms:
    @NEWINSTANCE(OBJ=%(TMP)s; HEAD=FACTORS; DATA={lterms: 2})
else:
    @NEWINSTANCE(OBJ=%(TMP)s; HEAD=FACTORS; DATA={lterms: 1, rterms: 1})
c = lcoeff * rcoeff
if c==1:
    return %(TMP)s
@RETURN_NEW(HEAD=TERMS; DATA={%(TMP)s: c})
'''
MUL_DICT_SYMBOL = '''\
@ADD_TERM_VALUE_DICT(TERM=%(RHS)s; VALUE=1; DICT=%(DICT)s; DICT_GET=%(DICT)s.get; SIGN=+; USIGN=)
@CANONIZE_FACTORS_DICT1(DICT=%(DICT)s)
@RETURN_NEW(HEAD=FACTORS; DATA=%(DICT)s)
'''
MUL_FACTORS_SYMBOL = '''\
pairs = dict(%(LHSDATA)s)
@MUL_DICT_SYMBOL(DICT=pairs; RHS=%(RHS)s; RHSDATA=%(RHSDATA)s)
'''
MUL_SYMBOL_FACTORS = '@MUL_FACTORS_SYMBOL(LHS=%(RHS)s; LHSDATA=%(RHSDATA)s; RHS=%(LHS)s; RHSDATA=%(LHSDATA)s)\n'
MUL_FACTORS_TERMS = '''\
rpairs = %(RHSDATA)s
if len(rpairs)==1:
    t1,c1 = rpairs.items()[0]
    t = t1 * %(LHS)s
    @RETURN_NEW(HEAD=TERMS; DATA={t: c1})
coeff, terms = %(RHS)s._coeff_terms
if terms is None:
    @MUL_FACTORS_SYMBOL(LHS=%(LHS)s; LHSDATA=%(LHSDATA)s; RHS=%(RHS)s; RHSDATA=%(RHSDATA)s)
pairs = dict(%(LHSDATA)s)
@ADD_TERM_VALUE_DICT(TERM=terms; VALUE=1; DICT=pairs; DICT_GET=pairs.get; SIGN=+; USIGN=)
@CANONIZE_FACTORS_DICT(DICT=pairs; NUMBER=coeff)
@NEWINSTANCE(OBJ=%(TMP)s; HEAD=FACTORS; DATA=pairs)
@RETURN_NEW(HEAD=TERMS; DATA={%(TMP)s: coeff})
'''
MUL_TERMS_FACTORS = '@MUL_FACTORS_TERMS(LHS=%(RHS)s; LHSDATA=%(RHSDATA)s; RHS=%(LHS)s; RHSDATA=%(LHSDATA)s)\n'
MUL_FACTORS_FACTORS = '''\
pairs = dict(%(LHSDATA)s)
pairs_get = pairs.get
number = 1
for t,c in %(RHSDATA)s.iteritems():
    @MUL_FACTOR_VALUE_DICT(FACTOR=t; SIGN=+; USIGN=; VALUE=c; DICT=pairs; DICT_GET=pairs_get; NUMBER=number)
@CANONIZE_FACTORS_DICT(DICT=pairs; NUMBER=number)
if number == 1:
    @RETURN_NEW(HEAD=FACTORS; DATA=pairs)
@NEWINSTANCE(OBJ=obj; HEAD=FACTORS; DATA=pairs)
@RETURN_NEW(HEAD=TERMS; DATA={obj: number})
'''

#======================================
# DIV macros
#======================================

DIV_VALUE_NUMBER='@RETURN_NEW2(HEAD=NUMBER; DATA=div(%(VALUE)s, %(RHSDATA)s, cls))\n'
DIV_NUMBER_VALUE='@RETURN_NEW2(HEAD=NUMBER; DATA=div(%(LHSDATA)s, %(VALUE)s, cls))\n'
DIV_NUMBER_NUMBER = '@DIV_VALUE_NUMBER(VALUE=%(LHSDATA)s; RHS=%(RHS)s; RHSDATA=%(RHSDATA)s)\n'
DIV_VALUE_SYMBOL = '''\
%(TMP)s = %(VALUE)s
if not %(TMP)s:
    return cls.zero
@NEWINSTANCE(OBJ=obj2; HEAD=FACTORS; DATA={%(RHS)s: -1})
if %(TMP)s==1:
    return obj2
@RETURN_NEW(HEAD=TERMS; DATA={obj2: %(TMP)s})
'''
DIV_SYMBOL_VALUE = '@MUL_VALUE_SYMBOL(VALUE=div(1, %(VALUE)s, cls); RHS=%(LHS)s; RHSDATA=%(LHSDATA)s)\n'
DIV_NUMBER_SYMBOL = '@DIV_VALUE_SYMBOL(VALUE=%(LHSDATA)s; RHS=%(RHS)s; RHSDATA=%(RHSDATA)s)\n'
DIV_SYMBOL_NUMBER = '@DIV_SYMBOL_VALUE(VALUE=%(RHSDATA)s; LHS=%(LHS)s; LHSDATA=%(LHSDATA)s)\n'
DIV_TERMS_VALUE = '@MUL_TERMS_VALUE(LHS=%(LHS)s; LHSDATA=%(LHSDATA)s; VALUE=div(1,%(VALUE)s,cls))\n'

DIV_VALUE_TERMS = '''\
%(TMP)s = %(VALUE)s
if not %(TMP)s:
    return cls.zero
pairs = %(RHSDATA)s
if len(pairs)==1:
    t, c = pairs.items()[0]
    c = div(%(VALUE)s, c, cls)
    t = 1/t
    if c==1:
        return t
    if t==cls.one:
        return cls.convert(c)
    @RETURN_NEW(HEAD=TERMS; DATA={t: c})
@NEWINSTANCE(OBJ=%(TMP)s; HEAD=FACTORS; DATA={%(RHS)s: -1})
if %(VALUE)s==1:
    return %(TMP)s
@RETURN_NEW(HEAD=TERMS; DATA={%(TMP)s: %(VALUE)s})
'''

DIV_FACTORS_VALUE = '@MUL_FACTORS_VALUE(LHS=%(LHS)s; LHSDATA=%(LHSDATA)s; VALUE=div(1,%(VALUE)s,cls))\n'
DIV_VALUE_FACTORS = '''
pairs = %(RHSDATA)s
if len(pairs)==1:
    t, c = pairs.items()[0]
    c = -c
    if c==1:
        return t * %(VALUE)s
    new_pairs = {t: c}
else:
    @NEG_DICT_VALUES(DICT_IN=pairs; DICT_OUT=new_pairs)
@NEWINSTANCE(OBJ=%(TMP)s; HEAD=FACTORS; DATA=new_pairs)
if %(VALUE)s==1:
    return %(TMP)s
@RETURN_NEW(HEAD=TERMS; DATA={%(TMP)s: %(VALUE)s})
'''
DIV_NUMBER_TERMS = '@DIV_VALUE_TERMS(VALUE=%(LHSDATA)s; RHS=%(RHS)s; RHSDATA=%(RHSDATA)s)\n'
DIV_TERMS_NUMBER = '@DIV_TERMS_VALUE(VALUE=%(RHSDATA)s; LHS=%(LHS)s; LHSDATA=%(LHSDATA)s)\n'
DIV_NUMBER_FACTORS = '@DIV_VALUE_FACTORS(VALUE=%(LHSDATA)s; RHS=%(RHS)s; RHSDATA=%(RHSDATA)s)\n'
DIV_FACTORS_NUMBER = '@DIV_FACTORS_VALUE(VALUE=%(RHSDATA)s; LHS=%(LHS)s; LHSDATA=%(LHSDATA)s)\n'
DIV_SYMBOL_SYMBOL = '''\
if %(LHS)s == %(RHS)s:
    return cls.one
@RETURN_NEW(HEAD=FACTORS; DATA={%(LHS)s: 1, %(RHS)s: -1})
'''
DIV_TERMS_SYMBOL = '''
pairs = %(LHSDATA)s
if len(pairs)==1:
    t, c = pairs.items()[0]
    if t==%(RHS)s:
        return cls.convert(c)
    t = t / %(RHS)s
    @RETURN_NEW(HEAD=TERMS; DATA={t: c})
@RETURN_NEW(HEAD=FACTORS; DATA={%(LHS)s: 1, %(RHS)s: -1})
'''
DIV_TERMS_TERMS = '''
if %(LHS)s==%(RHS)s:
    return cls.one
lpairs = %(LHSDATA)s
rpairs = %(RHSDATA)s
if len(lpairs)==1:
    t1, c1 = lpairs.items()[0]
    if len(rpairs)==1:
        t2, c2 = rpairs.items()[0]
        c = div(c1, c2, cls)
        if t2==t1:
            return cls.convert(c)
        if c==1:
            @RETURN_NEW(HEAD=FACTORS; DATA={t1:1, t2:-1})
        @NEWINSTANCE(OBJ=%(TMP)s; HEAD=FACTORS; DATA={t1:1, t2:-1})
    else:
        @NEWINSTANCE(OBJ=%(TMP)s; HEAD=FACTORS; DATA={t1:1, %(RHS)s:-1})
    @RETURN_NEW(HEAD=TERMS; DATA={%(TMP)s:c1})
elif len(rpairs)==1:
    t2, c2 = rpairs.items()[0]
    c = div(1, c2, cls)
    if t2==%(LHS)s:
        return cls.convert(c)
    %(TMP)s = %(LHS)s / t2
    @RETURN_NEW(HEAD=TERMS; DATA={%(TMP)s:c})
@RETURN_NEW(HEAD=FACTORS; DATA={%(LHS)s:1, %(RHS)s:-1})
'''
DIV_SYMBOL_TERMS = '''\
pairs = %(RHSDATA)s
if len(pairs)==1:
    t,c = pairs.items()[0]
    if %(LHS)s==t:
        return cls.convert(div(1, c, cls))
    @NEWINSTANCE(OBJ=%(TMP)s; HEAD=FACTORS; DATA={%(LHS)s:1, t:-1})
    @RETURN_NEW(HEAD=TERMS; DATA={%(TMP)s: div(1, c, cls)})
@RETURN_NEW(HEAD=FACTORS; DATA={%(LHS)s:1, %(RHS)s:-1})
'''
DIV_SYMBOL_FACTORS = '''\
pairs = %(RHSDATA)s
if len(pairs)==1:
    t, c = pairs.items()[0]
    if t==%(LHS)s:
        c = 1 - c
        if not c:
            return cls.one
        if c==1:
            return t
        else:
            @RETURN_NEW(HEAD=FACTORS; DATA={t: c})
    @RETURN_NEW(HEAD=FACTORS; DATA={t: -c, %(LHS)s: 1})
@NEG_DICT_VALUES(DICT_IN=%(RHSDATA)s; DICT_OUT=pairs)
@MUL_DICT_SYMBOL(DICT=pairs; RHS=%(LHS)s; RHSDATA=%(LHSDATA)s)
'''
DIV_TERMS_FACTORS = '''\
lpairs = %(LHSDATA)s
if len(lpairs)==1:
    t, c = lpairs.items()[0]
    t = t / %(RHS)s
    if t==cls.one:
        return cls.convert(c)
    head, data = t.pair
    if head is NUMBER:
        @RETURN_NEW(HEAD=NUMBER; DATA=data * c)
    elif head is TERMS:
        @MUL_TERMS_VALUE(LHS=t; LHSDATA=data; VALUE=c)
    else:
        @MUL_SYMBOL_VALUE(LHS=t; LHSDATA=data; VALUE=c)
@DIV_SYMBOL_FACTORS(LHS=%(LHS)s; LHSDATA=%(LHSDATA)s; RHS=%(RHS)s; RHSDATA=%(RHSDATA)s)
'''
DIV_DICT_SYMBOL = '''\
@ADD_TERM_VALUE_DICT(TERM=%(RHS)s; VALUE=-1; DICT=%(DICT)s; DICT_GET=%(DICT)s.get; SIGN=+; USIGN=)
@CANONIZE_FACTORS_DICT1(DICT=%(DICT)s)
@RETURN_NEW(HEAD=FACTORS; DATA=%(DICT)s)
'''
DIV_FACTORS_SYMBOL = '''\
pairs = dict(%(LHSDATA)s)
@DIV_DICT_SYMBOL(RHS=%(RHS)s; RHSDATA=%(RHSDATA)s; DICT=pairs)
'''
DIV_FACTORS_TERMS = '''\
rpairs = %(RHSDATA)s
if len(rpairs)==1:
    t, c = rpairs.items()[0]
    t = %(LHS)s / t
    c = div(1, c, cls)
    if t==cls.one:
        return cls.convert(c)
    head, data = t.pair
    if head is NUMBER:
        @RETURN_NEW(HEAD=NUMBER; DATA=data * c)
    elif head is TERMS:
        @MUL_TERMS_VALUE(LHS=t; LHSDATA=data; VALUE=c)
    else:
        @MUL_SYMBOL_VALUE(LHS=t; LHSDATA=data; VALUE=c)
@DIV_FACTORS_SYMBOL(LHS=%(LHS)s; LHSDATA=%(LHSDATA)s; RHS=%(RHS)s; RHSDATA=%(RHSDATA)s)
'''
DIV_FACTORS_FACTORS = '''\
pairs = dict(%(LHSDATA)s)
pairs_get = pairs.get
number = 1
for t,c in %(RHSDATA)s.iteritems():
    @MUL_FACTOR_VALUE_DICT(FACTOR=t; SIGN=-; USIGN=-; VALUE=c; DICT=pairs; DICT_GET=pairs_get; NUMBER=number)
@CANONIZE_FACTORS_DICT(DICT=pairs; NUMBER=number)
if number==1:
    @RETURN_NEW(HEAD=FACTORS; DATA=pairs)
@NEWINSTANCE(OBJ=%(TMP)s; HEAD=FACTORS; DATA=pairs)
@RETURN_NEW(HEAD=TERMS; DATA={%(TMP)s: number})
'''

#======================================
# POW macros
#======================================

POW_NUMBER_INT = '''\
if %(VALUE)s < 0:
    @RETURN_NEW(HEAD=NUMBER; DATA=div(1, (%(LHSDATA)s)**(-%(VALUE)s), cls))
@RETURN_NEW(HEAD=NUMBER; DATA=(%(LHSDATA)s)**(%(VALUE)s))
'''
POW_TERMS_INT = '''\
pairs = %(LHSDATA)s
if len(pairs)==1:
    t,c = pairs.items()[0]
    if %(VALUE)s < 0:
        c = div(1, c**(-%(VALUE)s), cls)
    else:
        c = c ** (%(VALUE)s)
    t = t**(%(VALUE)s)
    if c==1:
        return t
    @RETURN_NEW(HEAD=TERMS; DATA={t:c})
@RETURN_NEW(HEAD=FACTORS; DATA={%(LHS)s: %(VALUE)s})
'''
POW_FACTORS_INT = '''\
@MUL_DICT_VALUES(DICT_IN=%(LHSDATA)s; DICT_OUT=pairs; OP=%(VALUE)s)
if len(pairs)==1:
    t, c = pairs.items()[0]
    if c==1:
        return t
@RETURN_NEW(HEAD=FACTORS; DATA=pairs)
'''
POW_SYMBOL_INT = '''\
@RETURN_NEW(HEAD=FACTORS; DATA={%(LHS)s: %(VALUE)s})
'''

POW_NUMBER_VALUE = '''\
z, sym = try_power(%(LHSDATA)s, %(VALUE)s)
if not sym:
    @RETURN_NEW(HEAD=NUMBER; DATA=z)
factors = {}
for t,c in sym:
    factors[cls.convert(t)] = c
@NEWINSTANCE(OBJ=%(TMP)s; HEAD=FACTORS; DATA=factors)
if z==1:
    return %(TMP)s
@RETURN_NEW(HEAD=TERMS; DATA={%(TMP)s: z})
'''

POW_TERMS_FRAC = '''\
pairs = %(LHSDATA)s
if len(pairs)==1:
    t, c = pairs.items()[0]
    if isinstance(c, numbertypes) and not c==-1:
        if c < 0:
            z, sym = try_power(-c, %(VALUE)s)
            factors = {-t: %(VALUE)s}
        else:
            z, sym = try_power(c, %(VALUE)s)
            factors = {t: %(VALUE)s}
        for t,c in sym:
            factors[cls.convert(t)] = c
        @NEWINSTANCE(OBJ=%(TMP)s; HEAD=FACTORS; DATA=factors)
        if z==1:
            return %(TMP)s
        @RETURN_NEW(HEAD=TERMS; DATA={%(TMP)s: z})
@RETURN_NEW(HEAD=FACTORS; DATA={%(LHS)s: %(VALUE)s})
'''

POW_SYMBOL_FRAC = '''\
@RETURN_NEW(HEAD=FACTORS; DATA={%(LHS)s: %(VALUE)s})
'''

POW_FACTORS_SYMBOL = '''\
pairs = %(LHSDATA)s
if len(pairs)==1:
    t, c = pairs.items()[0]
    tc = type(c)
    if tc is int or tc is long:
        @RETURN_NEW(HEAD=FACTORS; DATA={t: %(RHS)s * c})
@RETURN_NEW(HEAD=FACTORS; DATA={%(LHS)s: %(RHS)s})
'''

def generate_if_blocks(heads, prefix='', tab=' '*4):
    lines = []
    lapp = lines.append
    for h1 in heads:
        if h1==heads[-1]:
            lapp('else:')
        elif h1==heads[0]:
            lapp('if lhead is %s:' % (h1))
        else:
            lapp('elif lhead is %s:' % (h1))
        for h2 in heads:
            if h2==heads[-1]:
                lapp(tab+'else:')
            elif h2==heads[0]:
                lapp(tab+'if rhead is %s:' % (h2))
            else:
                lapp(tab+'elif rhead is %s:' % (h2))
            lapp(tab*2 + '@%%(OP)s_%s_%s(LHS=self; LHSDATA=ldata; RHS=other; RHSDATA=rdata)' % (h1, h2))
    return prefix + ('\n'+prefix).join(lines)

OP3_TEMPLATE = '''
def %(op)s_method(self, other, NUMBER=NUMBER, TERMS=TERMS, FACTORS=FACTORS):
    cls = type(self)
    lhead, ldata = self.pair
    if type(other) is not cls:
        if isinstance(other, cls.coefftypes):
            if lhead is NUMBER:
                @%(OP)s_NUMBER_VALUE(VALUE=other; LHS=self; LHSDATA=ldata)
            elif lhead is TERMS:
                @%(OP)s_TERMS_VALUE(VALUE=other; LHS=self; LHSDATA=ldata)
            else:
                @%(OP)s_SYMBOL_VALUE(VALUE=other; LHS=self; LHSDATA=ldata)
        other = cls.convert(other, False)
        if other is NotImplemented:
            return other
    rhead, rdata = other.pair
''' + generate_if_blocks(['NUMBER', 'TERMS', 'SYMBOL'], prefix=' '*4)

OP4_TEMPLATE = '''
def %(op)s_method(self, other, NUMBER=NUMBER, TERMS=TERMS, FACTORS=FACTORS):
    cls = type(self)
    lhead, ldata = self.pair
    if type(other) is not cls:
        if isinstance(other, cls.coefftypes):
            if lhead is NUMBER:
                @%(OP)s_NUMBER_VALUE(VALUE=other; LHS=self; LHSDATA=ldata)
            elif lhead is TERMS:
                @%(OP)s_TERMS_VALUE(VALUE=other; LHS=self; LHSDATA=ldata)
            elif lhead is FACTORS:
                @%(OP)s_FACTORS_VALUE(VALUE=other; LHS=self; LHSDATA=ldata)
            else:
                @%(OP)s_SYMBOL_VALUE(VALUE=other; LHS=self; LHSDATA=ldata)
        other = cls.convert(other, False)
        if other is NotImplemented:
            return other
    rhead, rdata = other.pair
''' + generate_if_blocks(['NUMBER', 'TERMS', 'FACTORS', 'SYMBOL'], prefix=' '*4)

def main():
    f = open(targetfile_py, 'w')
    print >> f, template
    print >> f, preprocess('''

def expand_mul_method(cls, self, other):
    lhead, ldata = self.pair
    rhead, rdata = other.pair
    if lhead is FACTORS:
        if rhead is FACTORS:
            @MUL_FACTORS_FACTORS(LHS=self; LHSDATA=ldata; RHS=other; RHSDATA=rdata)
        elif rhead is NUMBER:
            return self # other must be one
        else:
            @MUL_FACTORS_SYMBOL(LHS=self; LHSDATA=ldata; RHS=other; RHSDATA=rdata)
    elif lhead is NUMBER:
        return other # self must be one
    else:
        if rhead is FACTORS:
            @MUL_SYMBOL_FACTORS(LHS=self; LHSDATA=ldata; RHS=other; RHSDATA=rdata)
        elif rhead is NUMBER:
            return self # other must be one
        else:
            @MUL_SYMBOL_SYMBOL(LHS=self; LHSDATA=ldata; RHS=other; RHSDATA=rdata)

def neg_method(self, NUMBER=NUMBER, TERMS=TERMS):
    cls = type(self)
    lhead, ldata = self.pair
    if lhead is NUMBER:
        @NEG_NUMBER(OP=self; OPDATA=ldata)
    elif lhead is TERMS:
        @NEG_TERMS(OP=self; OPDATA=ldata)
    else:
        @NEG_SYMBOL(OP=self; OPDATA=ldata)

def rsub_method(self, other, NUMBER=NUMBER, TERMS=TERMS, FACTORS=FACTORS):
    cls = type(self)
    lhead, ldata = self.pair
    if isinstance(other, cls.coefftypes):
        if lhead is NUMBER:
            @SUB_VALUE_NUMBER(VALUE=other; RHS=self; RHSDATA=ldata)
        elif lhead is TERMS:
            @SUB_VALUE_TERMS(VALUE=other; RHS=self; RHSDATA=ldata)
        else:
            @SUB_VALUE_SYMBOL(VALUE=other; RHS=self; RHSDATA=ldata)
    other = cls.convert(other, False)
    if other is NotImplemented:
        return other
    return other - self

def rdiv_method(self, other, NUMBER=NUMBER, TERMS=TERMS, FACTORS=FACTORS):
    cls = type(self)
    lhead, ldata = self.pair
    if isinstance(other, cls.coefftypes):
        if lhead is NUMBER:
            @DIV_VALUE_NUMBER(VALUE=other; RHS=self; RHSDATA=ldata)
        elif lhead is TERMS:
            @DIV_VALUE_TERMS(VALUE=other; RHS=self; RHSDATA=ldata)
        elif lhead is FACTORS:
            @DIV_VALUE_FACTORS(VALUE=other; RHS=self; RHSDATA=ldata)
        else:
            @DIV_VALUE_SYMBOL(VALUE=other; RHS=self; RHSDATA=ldata)
    other = cls.convert(other, False)
    if other is NotImplemented:
        return other
    return other / self

def pow_method(self, other, z = None, NUMBER=NUMBER, TERMS=TERMS, FACTORS=FACTORS):
    cls = type(self)
    lhead, ldata = self.pair
    type_other = type(other)
    if type_other is cls:
        rhead, rdata = other.pair
        if rhead is NUMBER:
            other = rdata
        type_other = type(other)
    if type_other is int or type_other is long:
        if not other:
            return cls.one
        if other==1:
            return self
        if lhead is NUMBER:
            @POW_NUMBER_INT(VALUE=other; LHS=self; LHSDATA=ldata)
        elif lhead is TERMS:
            @POW_TERMS_INT(VALUE=other; LHS=self; LHSDATA=ldata)
        elif lhead is FACTORS:
            @POW_FACTORS_INT(VALUE=other; LHS=self; LHSDATA=ldata)
        else:
            @POW_SYMBOL_INT(VALUE=other; LHS=self; LHSDATA=ldata)
    if lhead is NUMBER and isinstance(other, cls.exptypes):
        @POW_NUMBER_VALUE(VALUE=other; LHS=self; LHSDATA=ldata)
    if type_other is FractionTuple:
        if lhead is TERMS:
            @POW_TERMS_FRAC(VALUE=other; LHS=self; LHSDATA=ldata)
        else:
            @POW_SYMBOL_FRAC(VALUE=other; LHS=self; LHSDATA=ldata)
    if type_other is cls or isinstance(other, cls.exptypes):
        if lhead is FACTORS:
            @POW_FACTORS_SYMBOL(LHS=self; LHSDATA=ldata; RHS=other)
        @RETURN_NEW(HEAD=FACTORS; DATA={self: other})
    return NotImplemented
''', globals())

    print >> f, preprocess(OP3_TEMPLATE % (dict(op='add', OP='ADD')), globals())
    print >> f, preprocess(OP3_TEMPLATE % (dict(op='sub', OP='SUB')), globals())
    print >> f, preprocess(OP4_TEMPLATE % (dict(op='mul', OP='MUL')), globals())
    print >> f, preprocess(OP4_TEMPLATE % (dict(op='div', OP='DIV')), globals())

    f.close()


if __name__=='__main__':
    main()
