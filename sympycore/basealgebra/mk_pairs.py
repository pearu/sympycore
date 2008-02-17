#!/usr/bin/env python
#
# Created by Pearu Peterson in Febuary 2008
#

import os

def preprocess(source, tmp_cache=[1]):
    result = []
    for line in source.splitlines():
        if line.lstrip().startswith('@'):
            prefix, rest = line.split('@',1)
            i = rest.index('(')
            name = rest[:i]
            tmp_cache[0] += 1
            d = {'TMP':'_tmp%s' % (tmp_cache[0])}
            for arg in rest.strip()[i+1:-1].split(';'):
                key, value = arg.split('=',1)
                d[key.strip()] = value.strip()
            try:
                templ = eval(name, globals(), {})
            except NameError:
                templ = '@' + rest
            else:
                if '@' in templ:
                    templ = preprocess(templ)
            result.append(prefix + '#' + rest)
            try:
                templ_d = templ % d
            except KeyError, msg:
                print 'KeyError: %s (while processing %r)' % (msg, line.lstrip())
                print d, `templ`
                continue
            for l in templ_d.splitlines():
                result.append(prefix + l)
        else:
            result.append(line)
    return '\n'.join(result)

# FILE INFORMATION

cwd = os.path.abspath(os.path.dirname(__file__))
pairs_ops_py = os.path.join(cwd,'pairs_ops.py')
template = '''\
"""
This file is generated by the sympycore/basealgebra/mk_pairs.py script.
DO NOT CHANGE THIS FILE DIRECTLY!!!
"""

from ..utils import NUMBER, SYMBOL, TERMS, FACTORS, RedirectOperation
from ..arithmetic.numbers import ExtendedNumber, normalized_fraction, FractionTuple

def div(a, b, inttypes = (int, long)):
    if isinstance(b, inttypes):
        if isinstance(a, inttypes):
            if not b:
                if not a:
                    return ExtendedNumber.get_undefined()
                return ExtendedNumber.get_zoo()
            return normalized_fraction(a, b)
        if not b:
            if isinstance(a, ExtendedNumber):
                return a / b
            return ExtendedNumber.get_zoo()
        if b == 1:
            return a
        return FractionTuple((1,b)) * a
    return a / b

'''

#======================================
# General macros
#======================================

NEWINSTANCE = '''\
%(OBJ)s = new(cls)
%(OBJ)s.head = %(HEAD)s
%(OBJ)s.data = %(DATA)s
'''
RETURN_NEW = '''\
@NEWINSTANCE(OBJ=obj; HEAD=%(HEAD)s; DATA=%(DATA)s)
return obj
'''

ADD_TERM_VALUE_DICT='''\
b = %(DICT_GET)s(%(TERM)s)
if b is None:
    %(DICT)s[%(TERM)s] = %(VALUE)s
else:
    c = b + %(VALUE)s
    try:
        if c:
            %(DICT)s[%(TERM)s] = c
        else:
            del %(DICT)s[%(TERM)s]
    except RedirectOperation:
        %(DICT)s[%(TERM)s] = c
'''

MUL_FACTOR_VALUE_DICT='''\
b = %(DICT_GET)s(%(FACTOR)s)
if b is None:
    %(DICT)s[%(FACTOR)s] = %(VALUE)s
else:
    %(TMP)s = b + %(VALUE)s
    try:
        if %(TMP)s:
            if %(FACTOR)s.head is NUMBER:
                r = %(FACTOR)s ** %(TMP)s
                if r.head is NUMBER:
                    %(NUMBER)s *= r
                    del %(DICT)s[%(FACTOR)s]
                else:
                    %(DICT)s[%(FACTOR)s] = %(TMP)s
            else:
                %(DICT)s[%(FACTOR)s] = %(TMP)s
        else:
            del %(DICT)s[%(FACTOR)s]
    except RedirectOperation:
        %(DICT)s[%(FACTOR)s] = %(TMP)s
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
       return t * %(NUMBER)s
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
@ADD_TERM_VALUE_DICT(TERM=one; VALUE=%(VALUE)s; DICT=%(DICT)s; DICT_GET=%(DICT)s.get)
'''

NEG_DICT_VALUES = '''\
%(DICT_OUT)s = dict([(t, -c) for t,c in %(DICT_IN)s.iteritems()])
'''

#======================================
# NEG macros
#======================================

NEG_NUMBER = '@RETURN_NEW(HEAD=NUMBER; DATA=-%(OP)s.data)\n'
NEG_SYMBOL = '@RETURN_NEW(HEAD=TERMS; DATA={%(OP)s: -1})\n'
NEG_TERMS = '''\
op_pairs = %(OP)s.data
if len(op_pairs)==1:
    t, c = op_pairs.items()[0]
    c = -c
    if c==1:
        return t
    @RETURN_NEW(HEAD=TERMS; DATA={t:c})
@NEG_DICT_VALUES(DICT_IN=%(OP)s.data; DICT_OUT=pairs)
@RETURN_NEW(HEAD=TERMS; DATA=pairs)
'''
NEG_FACTORS = '@NEG_SYMBOL(OP=%(OP)s)\n'

#======================================
# ADD macros
#======================================

ADD_VALUE_NUMBER='@RETURN_NEW(HEAD=NUMBER; DATA=%(VALUE)s + %(RHS)s.data)\n'
ADD_NUMBER_VALUE='@RETURN_NEW(HEAD=NUMBER; DATA=%(LHS)s.data + %(VALUE)s)\n'
ADD_NUMBER_NUMBER = '@ADD_VALUE_NUMBER(VALUE=%(LHS)s.data; RHS=%(RHS)s)\n'
ADD_VALUE_SYMBOL = '''\
%(TMP)s = %(VALUE)s
try:
    if not %(TMP)s:
        return %(RHS)s
except RedirectOperation:
    pass
@RETURN_NEW(HEAD=TERMS; DATA={cls.one: %(TMP)s, %(RHS)s: 1})
'''
ADD_SYMBOL_VALUE = '@ADD_VALUE_SYMBOL(VALUE=%(VALUE)s; RHS=%(LHS)s)\n'
ADD_NUMBER_SYMBOL = '@ADD_VALUE_SYMBOL(VALUE=%(LHS)s.data; RHS=%(RHS)s)\n'
ADD_SYMBOL_NUMBER = '@ADD_SYMBOL_VALUE(VALUE=%(RHS)s.data; LHS=%(LHS)s)\n'
ADD_SYMBOL_SYMBOL = '''\
if %(LHS)s == %(RHS)s:
    pairs = {%(LHS)s: 2}
else:
    pairs = {%(LHS)s: 1, %(RHS)s: 1}
@RETURN_NEW(HEAD=TERMS; DATA=pairs)
'''
ADD_VALUE_TERMS = '''\
%(TMP)s = %(VALUE)s
try:
    if not %(TMP)s:
        return %(RHS)s
except RedirectOperation:
    pass
pairs = dict(%(RHS)s.data)
one = cls.one
@ADD_VALUE_DICT(DICT=pairs; VALUE=%(TMP)s)
@RETURN_NEW(HEAD=TERMS; DATA=pairs)
'''
ADD_TERMS_VALUE = '@ADD_VALUE_TERMS(VALUE=%(VALUE)s; RHS=%(LHS)s)\n'
ADD_NUMBER_TERMS = '@ADD_VALUE_TERMS(VALUE=%(LHS)s.data; RHS=%(RHS)s)\n'
ADD_TERMS_NUMBER = '@ADD_TERMS_VALUE(VALUE=%(RHS)s.data; LHS=%(LHS)s)\n'

ADD_TERMS_SYMBOL = '''\
pairs = dict(%(LHS)s.data)
@ADD_TERM_VALUE_DICT(TERM=%(RHS)s; VALUE=1; DICT=pairs; DICT_GET=pairs.get)
@CANONIZE_TERMS_DICT(DICT=pairs)
@RETURN_NEW(HEAD=TERMS; DATA=pairs)
'''
ADD_SYMBOL_TERMS = '@ADD_TERMS_SYMBOL(LHS=%(RHS)s; RHS=%(LHS)s)\n'
ADD_TERMS_TERMS = '''\
pairs = dict(%(LHS)s.data)
pairs_get = pairs.get
for t,c in %(RHS)s.data.iteritems():
    @ADD_TERM_VALUE_DICT(TERM=t; VALUE=c; DICT=pairs; DICT_GET=pairs_get)
@CANONIZE_TERMS_DICT(DICT=pairs)
@RETURN_NEW(HEAD=TERMS; DATA=pairs)
'''

#======================================
# SUB macros
#======================================

SUB_VALUE_NUMBER='@RETURN_NEW(HEAD=NUMBER; DATA=%(VALUE)s - %(RHS)s.data)\n'
SUB_NUMBER_VALUE='@RETURN_NEW(HEAD=NUMBER; DATA=%(LHS)s.data - %(VALUE)s)\n'
SUB_NUMBER_NUMBER = '@SUB_VALUE_NUMBER(VALUE=%(LHS)s.data; RHS=%(RHS)s)\n'
SUB_VALUE_SYMBOL = '''\
%(TMP)s = %(VALUE)s
try:
    if not %(TMP)s:
        @RETURN_NEW(HEAD=TERMS; DATA={%(RHS)s: -1})
except RedirectOperation:
    pass
@RETURN_NEW(HEAD=TERMS; DATA={cls.one: %(TMP)s, %(RHS)s: -1})
'''
SUB_SYMBOL_VALUE = '@ADD_SYMBOL_VALUE(OBJ=obj; LHS=%(LHS)s; VALUE=-%(VALUE)s)\n'
SUB_NUMBER_SYMBOL = '@SUB_VALUE_SYMBOL(VALUE=%(LHS)s.data; RHS=%(RHS)s)\n'
SUB_SYMBOL_NUMBER = '@SUB_SYMBOL_VALUE(VALUE=%(RHS)s.data; LHS=%(LHS)s)\n'
SUB_SYMBOL_SYMBOL = '''\
if %(LHS)s == %(RHS)s:
    return cls.zero
@RETURN_NEW(HEAD=TERMS; DATA={%(LHS)s: 1, %(RHS)s: -1})
'''
SUB_VALUE_TERMS = '''\
%(TMP)s = %(VALUE)s
try:
    if not %(TMP)s:
        @NEG_TERMS(OP=%(RHS)s)
except RedirectOperation:
    pass
@NEG_DICT_VALUES(DICT_IN=%(RHS)s.data; DICT_OUT=pairs)
one = cls.one
@ADD_VALUE_DICT(DICT=pairs; VALUE=%(TMP)s)
@RETURN_NEW(HEAD=TERMS; DATA=pairs)
'''
SUB_TERMS_VALUE = '@ADD_VALUE_TERMS(VALUE=-%(VALUE)s; RHS=%(LHS)s)\n'
SUB_NUMBER_TERMS = '@SUB_VALUE_TERMS(VALUE=%(LHS)s.data; RHS=%(RHS)s)\n'
SUB_TERMS_NUMBER = '@SUB_TERMS_VALUE(VALUE=%(RHS)s.data; LHS=%(LHS)s)\n'
SUB_TERMS_SYMBOL = '''\
pairs = dict(%(LHS)s.data)
@ADD_TERM_VALUE_DICT(TERM=%(RHS)s; VALUE=-1; DICT=pairs; DICT_GET=pairs.get)
@CANONIZE_TERMS_DICT(DICT=pairs)
@RETURN_NEW(HEAD=TERMS; DATA=pairs)
'''
SUB_SYMBOL_TERMS = '''\
@NEG_DICT_VALUES(DICT_IN=%(RHS)s.data; DICT_OUT=pairs)
@ADD_TERM_VALUE_DICT(TERM=%(LHS)s; VALUE=1; DICT=pairs; DICT_GET=pairs.get)
@CANONIZE_TERMS_DICT(DICT=pairs)
@RETURN_NEW(HEAD=TERMS; DATA=pairs)
'''
SUB_TERMS_TERMS = '''\
pairs = dict(%(LHS)s.data)
pairs_get = pairs.get
for t,c in %(RHS)s.data.iteritems():
    @ADD_TERM_VALUE_DICT(TERM=t; VALUE=-c; DICT=pairs; DICT_GET=pairs_get)
@CANONIZE_TERMS_DICT(DICT=pairs)
@RETURN_NEW(HEAD=TERMS; DATA=pairs)
'''

#======================================
# MUL macros
#======================================

MUL_ZERO_OP = '''\
try:
    if not %(VALUE)s:
        if %(OP)s.has_active():
            @RETURN_NEW(HEAD=TERMS; DATA={%(OP)s: 0})
        else:
            return cls.zero
except RedirectOperation:
    @RETURN_NEW(HEAD=TERMS; DATA={%(OP)s: %(VALUE)s})
'''

MUL_VALUE_NUMBER='@RETURN_NEW(HEAD=NUMBER; DATA=%(VALUE)s * %(RHS)s.data)\n'
MUL_NUMBER_VALUE='@RETURN_NEW(HEAD=NUMBER; DATA=%(LHS)s.data * %(VALUE)s)\n'
MUL_NUMBER_NUMBER = '@MUL_VALUE_NUMBER(VALUE=%(LHS)s.data; RHS=%(RHS)s)\n'
MUL_VALUE_SYMBOL = '''\
%(TMP)s = %(VALUE)s
@MUL_ZERO_OP(VALUE=%(TMP)s; OP=%(RHS)s)
if %(TMP)s==1:
    return %(RHS)s
@RETURN_NEW(HEAD=TERMS; DATA={%(RHS)s: %(TMP)s})
'''
MUL_SYMBOL_VALUE = '@MUL_VALUE_SYMBOL(VALUE=%(VALUE)s; RHS=%(LHS)s)\n'
MUL_NUMBER_SYMBOL = '@MUL_VALUE_SYMBOL(VALUE=%(LHS)s.data; RHS=%(RHS)s)\n'
MUL_SYMBOL_NUMBER = '@MUL_SYMBOL_VALUE(VALUE=%(RHS)s.data; LHS=%(LHS)s)\n'
MUL_NUMBER_FACTORS = '@MUL_SYMBOL_VALUE(VALUE=%(LHS)s.data; LHS=%(RHS)s)\n'
MUL_VALUE_FACTORS = '@MUL_SYMBOL_VALUE(VALUE=%(VALUE)s; LHS=%(RHS)s)\n'
MUL_FACTORS_NUMBER = '@MUL_SYMBOL_VALUE(VALUE=%(RHS)s.data; LHS=%(LHS)s)\n'
MUL_FACTORS_VALUE = '@MUL_SYMBOL_VALUE(VALUE=%(VALUE)s; LHS=%(LHS)s)\n'
MUL_SYMBOL_SYMBOL = '''\
if %(LHS)s == %(RHS)s:
    pairs = {%(LHS)s: 2}
else:
    pairs = {%(LHS)s: 1, %(RHS)s: 1}
@RETURN_NEW(HEAD=FACTORS; DATA=pairs)
'''
MUL_VALUE_TERMS = '''\
%(TMP)s = %(VALUE)s
@MUL_ZERO_OP(VALUE=%(TMP)s; OP=%(RHS)s)
pairs = %(RHS)s.data
if len(pairs)==1:
    t, c = pairs.items()[0]
    c = %(TMP)s * c
    if c==1:
        return t
    @RETURN_NEW(HEAD=TERMS; DATA={t: c})
if %(TMP)s==1:
    return %(RHS)s
pairs = {}
for t,c in %(RHS)s.data.iteritems():
    c = %(TMP)s * c
    try:
        if c or t.has_active():
            pairs[t] = c
    except RedirectOperation:
        pairs[t] = c
@CANONIZE_TERMS_DICT(DICT=pairs)
@RETURN_NEW(HEAD=TERMS; DATA=pairs)
'''
MUL_TERMS_VALUE='@MUL_VALUE_TERMS(VALUE=%(VALUE)s; RHS=%(LHS)s)\n'
MUL_NUMBER_TERMS = '@MUL_VALUE_TERMS(VALUE=%(LHS)s.data; RHS=%(RHS)s)\n'
MUL_TERMS_NUMBER = '@MUL_TERMS_VALUE(VALUE=%(RHS)s.data; LHS=%(LHS)s)\n'
MUL_TERMS_SYMBOL = '''\
pairs = %(LHS)s.data
if len(pairs)==1:
    t,c = pairs.items()[0]
    t = t * %(RHS)s
    if t==cls.one:
        return cls.convert(c)
    @RETURN_NEW(HEAD=TERMS; DATA={t: c})
@RETURN_NEW(HEAD=FACTORS; DATA={%(LHS)s: 1, %(RHS)s: 1})
'''
MUL_SYMBOL_TERMS = '@MUL_TERMS_SYMBOL(LHS=%(RHS)s; RHS=%(LHS)s)\n'
MUL_TERMS_TERMS = '''\
lpairs = %(LHS)s.data
rpairs = %(RHS)s.data
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
    t = t1 * %(RHS)s
    @RETURN_NEW(HEAD=TERMS; DATA={t: c1})
elif len(rpairs)==1:
    t1,c1 = rpairs.items()[0]
    t = t1 * %(LHS)s
    @RETURN_NEW(HEAD=TERMS; DATA={t: c1})
if %(LHS)s==%(RHS)s:
    pairs = {%(LHS)s: 2}
else:
    pairs = {%(LHS)s: 1, %(RHS)s: 1}
@RETURN_NEW(HEAD=FACTORS; DATA=pairs)
'''
MUL_DICT_SYMBOL = '''\
@ADD_TERM_VALUE_DICT(TERM=%(RHS)s; VALUE=1; DICT=%(DICT)s; DICT_GET=%(DICT)s.get)
@CANONIZE_FACTORS_DICT1(DICT=%(DICT)s)
@RETURN_NEW(HEAD=FACTORS; DATA=%(DICT)s)
'''
MUL_FACTORS_SYMBOL = '''\
pairs = dict(%(LHS)s.data)
@MUL_DICT_SYMBOL(DICT=pairs; RHS=%(RHS)s)
'''
MUL_SYMBOL_FACTORS = '@MUL_FACTORS_SYMBOL(LHS=%(RHS)s; RHS=%(LHS)s)\n'
MUL_FACTORS_TERMS = '''\
rpairs = %(RHS)s.data
if len(rpairs)==1:
    t1,c1 = rpairs.items()[0]
    t = t1 * %(LHS)s
    @RETURN_NEW(HEAD=TERMS; DATA={t: c1})
@MUL_FACTORS_SYMBOL(LHS=%(LHS)s; RHS=%(RHS)s)
'''
MUL_TERMS_FACTORS = '@MUL_FACTORS_TERMS(LHS=%(RHS)s; RHS=%(LHS)s)\n'
MUL_FACTORS_FACTORS = '''\
pairs = dict(%(LHS)s.data)
pairs_get = pairs.get
number = 1
for t,c in %(RHS)s.data.iteritems():
    @MUL_FACTOR_VALUE_DICT(FACTOR=t; VALUE=c; DICT=pairs; DICT_GET=pairs_get; NUMBER=number)
@CANONIZE_FACTORS_DICT(DICT=pairs; NUMBER=number)
if number is 1:
    @RETURN_NEW(HEAD=FACTORS; DATA=pairs)
@NEWINSTANCE(OBJ=obj; HEAD=FACTORS; DATA=pairs)
return obj * number
'''

#======================================
# DIV macros
#======================================

DIV_VALUE_NUMBER='@RETURN_NEW(HEAD=NUMBER; DATA=div(%(VALUE)s, %(RHS)s.data))\n'
DIV_NUMBER_VALUE='@RETURN_NEW(HEAD=NUMBER; DATA=div(%(LHS)s.data, %(VALUE)s))\n'
DIV_NUMBER_NUMBER = '@DIV_VALUE_NUMBER(VALUE=%(LHS)s.data; RHS=%(RHS)s)\n'
DIV_VALUE_SYMBOL = '''\
%(TMP)s = %(VALUE)s
try:
    if not %(TMP)s:
        return cls.zero
except RedirectOperation:
    pass
@NEWINSTANCE(OBJ=obj2; HEAD=FACTORS; DATA={%(RHS)s: -1})
if %(TMP)s==1:
    return obj2
@RETURN_NEW(HEAD=TERMS; DATA={obj2: %(TMP)s})
'''
DIV_SYMBOL_VALUE = '@MUL_VALUE_SYMBOL(VALUE=div(1, %(VALUE)s); RHS=%(LHS)s)\n'
DIV_NUMBER_SYMBOL = '@DIV_VALUE_SYMBOL(VALUE=%(LHS)s.data; RHS=%(RHS)s)\n'
DIV_SYMBOL_NUMBER = '@DIV_SYMBOL_VALUE(VALUE=%(RHS)s.data; LHS=%(LHS)s)\n'
DIV_TERMS_VALUE = '@MUL_TERMS_VALUE(LHS=%(LHS)s; VALUE=div(1,%(VALUE)s))\n'

DIV_VALUE_TERMS = '''\
@MUL_ZERO_OP(VALUE=%(VALUE)s; OP=%(RHS)s)
pairs = %(RHS)s.data
if len(pairs)==1:
    t, c = pairs.items()[0]
    c = div(%(VALUE)s, c)
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

DIV_FACTORS_VALUE = '@MUL_FACTORS_VALUE(LHS=%(LHS)s; VALUE=div(1,%(VALUE)s))\n'
DIV_VALUE_FACTORS = '''
pairs = %(RHS)s.data
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
DIV_NUMBER_TERMS = '@DIV_VALUE_TERMS(VALUE=%(LHS)s.data; RHS=%(RHS)s)\n'
DIV_TERMS_NUMBER = '@DIV_TERMS_VALUE(VALUE=%(RHS)s.data; LHS=%(LHS)s)\n'
DIV_NUMBER_FACTORS = '@DIV_VALUE_FACTORS(VALUE=%(LHS)s.data; RHS=%(RHS)s)\n'
DIV_FACTORS_NUMBER = '@DIV_FACTORS_VALUE(VALUE=%(RHS)s.data; LHS=%(LHS)s)\n'
DIV_SYMBOL_SYMBOL = '''\
if %(LHS)s == %(RHS)s:
    return cls.one
@RETURN_NEW(HEAD=FACTORS; DATA={%(LHS)s: 1, %(RHS)s: -1})
'''
DIV_TERMS_SYMBOL = '''
pairs = %(LHS)s.data
if len(pairs)==1:
    t, c = pairs.items()[0]
    if t==%(RHS)s:
        return cls.convert(c)
    @NEWINSTANCE(OBJ=%(TMP)s; HEAD=FACTORS; DATA={t:1, %(RHS)s: -1})
    @RETURN_NEW(HEAD=TERMS; DATA={%(TMP)s: c})
@RETURN_NEW(HEAD=FACTORS; DATA={%(LHS)s: 1, %(RHS)s: -1})
'''
DIV_TERMS_TERMS = '''
if %(LHS)s==%(RHS)s:
    return cls.one
lpairs = %(LHS)s.data
rpairs = %(RHS)s.data
if len(lpairs)==1:
    t1, c1 = lpairs.items()[0]
    if len(rpairs)==1:
        t2, c2 = rpairs.items()[0]
        c = div(c1, c2)
        if t2==t1:
            return cls.convert(c)
        if c==1:
            @RETURN_NEW(HEAD=FACTORS; DATA={t1:1, t2:-1})
        @NEWINSTANCE(OBJ=%(TMP)s; HEAD=FACTORS; DATA={t1:1, t2:-1})
    else:
        @NEWINSTANCE(OBJ=%(TMP)s; HEAD=FACTORS; DATA={t1:1, %(RHS)s:-1})
    @RETURN_NEW(HEAD=TERMS; DATA={%(TMP)s:c})
elif len(rpairs)==1:
    t2, c2 = rpairs.items()[0]
    c = div(1, c2)
    if t2==%(LHS)s:
        return cls.convert(c)
    %(TMP)s = %(LHS)s / t2
    @RETURN_NEW(HEAD=TERMS; DATA={%(TMP)s:c})
@RETURN_NEW(HEAD=FACTORS; DATA={%(LHS)s:1, %(RHS)s:-1})
'''
DIV_SYMBOL_TERMS = '''\
pairs = %(RHS)s.data
if len(pairs)==1:
    t,c = pairs.items()[0]
    if %(LHS)s==t:
        return cls.convert(div(1, c))
    @NEWINSTANCE(OBJ=%(TMP)s; HEAD=FACTORS; DATA={%(LHS)s:1, t:-1})
    @RETURN_NEW(HEAD=TERMS; DATA={%(TMP)s: div(1, c)})
@RETURN_NEW(HEAD=FACTORS; DATA={%(LHS)s:1, %(RHS)s:-1})
'''
DIV_SYMBOL_FACTORS = '''\
pairs = %(RHS)s.data
if len(pairs)==1:
    t, c = pairs.items()[0]
    if t==%(LHS)s:
        c = 1 - c
        try:
            if not c:
                return cls.one
        except RedirectOperation:
            pass
        if c==1:
            return t
        else:
            @RETURN_NEW(HEAD=FACTORS; DATA={t: c})
    @RETURN_NEW(HEAD=FACTORS; DATA={t: -c, %(LHS)s: 1})
@NEG_DICT_VALUES(DICT_IN=%(RHS)s.data; DICT_OUT=pairs)
@MUL_DICT_SYMBOL(DICT=pairs; RHS=%(LHS)s)
'''
DIV_TERMS_FACTORS = '''\
lpairs = %(LHS)s.data
if len(lpairs)==1:
    t, c = lpairs.items()[0]
    t = t / %(RHS)s
    if t==cls.one:
        return cls.convert(c)
    head = t.head
    if head is NUMBER:
        @RETURN_NEW(HEAD=NUMBER; DATA=t.data * c)
    elif head is TERMS:
        @MUL_TERMS_VALUE(LHS=t; VALUE=c)
    else:
        @MUL_SYMBOL_VALUE(LHS=t; VALUE=c)
@DIV_SYMBOL_FACTORS(LHS=%(LHS)s; RHS=%(RHS)s)
'''
DIV_DICT_SYMBOL = '''\
@ADD_TERM_VALUE_DICT(TERM=%(RHS)s; VALUE=-1; DICT=%(DICT)s; DICT_GET=%(DICT)s.get)
@CANONIZE_FACTORS_DICT1(DICT=%(DICT)s)
@RETURN_NEW(HEAD=FACTORS; DATA=%(DICT)s)
'''
DIV_FACTORS_SYMBOL = '''\
pairs = dict(%(LHS)s.data)
@DIV_DICT_SYMBOL(RHS=%(RHS)s; DICT=pairs)
'''
DIV_FACTORS_TERMS = '''\
rpairs = %(RHS)s.data
if len(rpairs)==1:
    t, c = rpairs.items()[0]
    t = %(LHS)s / t
    c = div(1, c)
    if t==cls.one:
        return cls.convert(c)
    head = t.head
    if head is NUMBER:
        @RETURN_NEW(HEAD=NUMBER; DATA=t.data * c)
    elif head is TERMS:
        @MUL_TERMS_VALUE(LHS=t; VALUE=c)
    else:
        @MUL_SYMBOL_VALUE(LHS=t; VALUE=c)
@DIV_FACTORS_SYMBOL(LHS=%(LHS)s; RHS=%(RHS)s)
'''
DIV_FACTORS_FACTORS = '''\
pairs = dict(%(LHS)s.data)
pairs_get = pairs.get
number = 1
for t,c in %(RHS)s.data.iteritems():
    @MUL_FACTOR_VALUE_DICT(FACTOR=t; VALUE=-c; DICT=pairs; DICT_GET=pairs_get; NUMBER=number)
@CANONIZE_FACTORS_DICT(DICT=pairs; NUMBER=number)
if number==1:
    @RETURN_NEW(HEAD=FACTORS; DATA=pairs)
@NEWINSTANCE(OBJ=%(TMP)s; HEAD=FACTORS; DATA=pairs)
@RETURN_NEW(HEAD=TERMS; DATA={%(TMP)s: number})
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
            lapp(tab*2 + '@%%(OP)s_%s_%s(LHS=self; RHS=other)' % (h1, h2))
    return prefix + ('\n'+prefix).join(lines)

OP3_TEMPLATE = '''
def %(op)s_method(self, other, NUMBER=NUMBER, TERMS=TERMS, FACTORS=FACTORS, new=object.__new__):
    cls = self.__class__
    lhead = self.head
    if type(other) is not cls:
        if isinstance(other, cls.coefftypes):
            if lhead is NUMBER:
                @%(OP)s_NUMBER_VALUE(VALUE=other; LHS=self)
            elif lhead is TERMS:
                @%(OP)s_TERMS_VALUE(VALUE=other; LHS=self)
            else:
                @%(OP)s_SYMBOL_VALUE(VALUE=other; LHS=self)
        other = cls.convert(other, False)
        if other is NotImplemented:
            return other
    rhead = other.head
''' + generate_if_blocks(['NUMBER', 'TERMS', 'SYMBOL'], prefix=' '*4)

OP4_TEMPLATE = '''
def %(op)s_method(self, other, NUMBER=NUMBER, TERMS=TERMS, FACTORS=FACTORS, new=object.__new__):
    cls = self.__class__
    lhead = self.head
    if type(other) is not cls:
        if isinstance(other, cls.coefftypes):
            if lhead is NUMBER:
                @%(OP)s_NUMBER_VALUE(VALUE=other; LHS=self)
            elif lhead is TERMS:
                @%(OP)s_TERMS_VALUE(VALUE=other; LHS=self)
            elif lhead is FACTORS:
                @%(OP)s_FACTORS_VALUE(VALUE=other; LHS=self)
            else:
                @%(OP)s_SYMBOL_VALUE(VALUE=other; LHS=self)
        other = cls.convert(other, False)
        if other is NotImplemented:
            return other
    rhead = other.head
''' + generate_if_blocks(['NUMBER', 'TERMS', 'FACTORS', 'SYMBOL'], prefix=' '*4)


def main():
    f = open(pairs_ops_py, 'w')
    print >> f, template
    print >> f, preprocess('''

def neg_method(self, NUMBER=NUMBER, TERMS=TERMS, new=object.__new__):
    cls = self.__class__
    lhead = self.head
    if lhead is NUMBER:
        @NEG_NUMBER(OP=self)
    elif lhead is TERMS:
        @NEG_TERMS(OP=self)
    else:
        @NEG_SYMBOL(OP=self)

def rsub_method(self, other, NUMBER=NUMBER, TERMS=TERMS, FACTORS=FACTORS, new=object.__new__):
    cls = self.__class__
    lhead = self.head
    if isinstance(other, cls.coefftypes):
        if lhead is NUMBER:
            @SUB_VALUE_NUMBER(VALUE=other; RHS=self)
        elif lhead is TERMS:
            @SUB_VALUE_TERMS(VALUE=other; RHS=self)
        else:
            @SUB_VALUE_SYMBOL(VALUE=other; RHS=self)
    other = cls.convert(other, False)
    if other is NotImplemented:
        return other
    return other - self

def rdiv_method(self, other, NUMBER=NUMBER, TERMS=TERMS, FACTORS=FACTORS, new=object.__new__):
    cls = self.__class__
    lhead = self.head
    if isinstance(other, cls.coefftypes):
        if lhead is NUMBER:
            @DIV_VALUE_NUMBER(VALUE=other; RHS=self)
        elif lhead is TERMS:
            @DIV_VALUE_TERMS(VALUE=other; RHS=self)
        elif lhead is FACTORS:
            @DIV_VALUE_FACTORS(VALUE=other; RHS=self)
        else:
            @DIV_VALUE_SYMBOL(VALUE=other; RHS=self)
    other = cls.convert(other, False)
    if other is NotImplemented:
        return other
    return other / self
''')


    print >> f, preprocess(OP3_TEMPLATE % (dict(op='add', OP='ADD')))
    print >> f, preprocess(OP3_TEMPLATE % (dict(op='sub', OP='SUB')))
    print >> f, preprocess(OP4_TEMPLATE % (dict(op='mul', OP='MUL')))
    print >> f, preprocess(OP4_TEMPLATE % (dict(op='div', OP='DIV')))

    f.close()


if __name__=='__main__':
    main()
