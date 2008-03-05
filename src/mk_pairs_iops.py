#!/usr/bin/env python
#
# Created by Pearu Peterson in Febuary 2008
#

import os

from macros import preprocess
cwd = os.path.abspath(os.path.dirname(__file__))
targetfile_py = os.path.join(cwd,'..','sympycore','basealgebra','pairs_iops.py')

template = '''\
"""
Generated low-level arithmetic inplace functions for CommutativeRingWithPairs.

This file is generated by the src/mk_pairs_iops.py script.
See http://sympycore.googlecode.com/ for more information.

DO NOT CHANGE THIS FILE DIRECTLY!!!
"""

from ..core import Expr
from ..arithmetic.numbers import Complex, Float, FractionTuple, try_power
from ..utils import NUMBER, TERMS, FACTORS
new = Expr.__new__
'''

def main():
    f = open(targetfile_py, 'w')
    print >> f, template
    print >> f, preprocess('''

def return_terms(cls, pairs, new=new):
    if not pairs:
        return cls.zero
    if len(pairs)==1:
        t, c = pairs.items()[0]
        if c==1:
            return t
        if t==cls.one:
            return cls.convert(c)
    @RETURN_NEW(HEAD=TERMS; DATA=pairs)

def return_factors(cls, pairs, new=new):
    if not pairs:
        return cls.one
    elif len(pairs)==1:
        t, c = pairs.items()[0]
        if c==1:
            return t
        if t==cls.one:
            return t
    @RETURN_NEW(HEAD=FACTORS; DATA=pairs)

def inplace_add(cls, obj, pairs, pairs_get, one):
    tobj = type(obj)
    if tobj is cls:
        head, data = obj.pair
        if head is NUMBER:
            if data:
                @ADD_TERM_VALUE_DICT(DICT=pairs; DICT_GET=pairs_get; TERM=one; VALUE=data; SIGN=+; USIGN=)
        elif head is TERMS:
            for t,c in data.iteritems():
                @ADD_TERM_VALUE_DICT(DICT=pairs; DICT_GET=pairs_get; TERM=t; VALUE=c; SIGN=+; USIGN=)
        else:
            @ADD_TERM_VALUE_DICT(DICT=pairs; DICT_GET=pairs_get; TERM=obj; VALUE=1; SIGN=+; USIGN=)
    @ELIF_CHECK_NUMBER(T=tobj)
        if obj:
            @ADD_TERM_VALUE_DICT(DICT=pairs; DICT_GET=pairs_get; TERM=one; VALUE=obj; SIGN=+; USIGN=)
    else:
        inplace_add(cls, cls.convert(obj), pairs, pairs_get, one)

def inplace_add2(cls, obj, coeff, pairs, pairs_get, one):
    if not coeff:
        return
    tobj = type(obj)
    if tobj is cls:
        head, data = obj.pair
        if head is NUMBER:
            value = coeff * data
            if value:
                @ADD_TERM_VALUE_DICT(DICT=pairs; DICT_GET=pairs_get; TERM=one; VALUE=value; SIGN=+; USIGN=)
        elif head is TERMS:
            for t,c in data.iteritems():
                @ADD_TERM_VALUE_DICT(DICT=pairs; DICT_GET=pairs_get; TERM=t; VALUE=coeff*c; SIGN=+; USIGN=)
        else:
            @ADD_TERM_VALUE_DICT(DICT=pairs; DICT_GET=pairs_get; TERM=obj; VALUE=coeff; SIGN=+; USIGN=)
    @ELIF_CHECK_NUMBER(T=tobj)
        value = coeff * obj
        if value:
            @ADD_TERM_VALUE_DICT(DICT=pairs; DICT_GET=pairs_get; TERM=one; VALUE=value; SIGN=+; USIGN=)
    else:
        inplace_add2(cls, cls.convert(obj), coeff, pairs, pairs_get, one)

def inplace_sub(cls, obj, pairs, pairs_get, one):
    tobj = type(obj)
    if tobj is cls:
        head, data = obj.pair
        if head is NUMBER:
            value = data
            if value:
                @ADD_TERM_VALUE_DICT(DICT=pairs; DICT_GET=pairs_get; TERM=one; VALUE=value; SIGN=-; USIGN=-)
        elif head is TERMS:
            for t,c in data.iteritems():
                @ADD_TERM_VALUE_DICT(DICT=pairs; DICT_GET=pairs_get; TERM=t; VALUE=c; SIGN=-; USIGN=-)
        else:
            @ADD_TERM_VALUE_DICT(DICT=pairs; DICT_GET=pairs_get; TERM=obj; VALUE=1; SIGN=-; USIGN=-)
    @ELIF_CHECK_NUMBER(T=tobj)
        if obj:
            @ADD_TERM_VALUE_DICT(DICT=pairs; DICT_GET=pairs_get; TERM=one; VALUE=obj; SIGN=-; USIGN=-)
    else:
        inplace_add(cls, cls.convert(obj), pairs, pairs_get, one)

def inplace_mul(cls, obj, pairs, pairs_get, try_power=try_power, NUMBER=NUMBER):
    tobj = type(obj)
    if tobj is cls:
        head, data = obj.pair
        if head is NUMBER:
            return data
        elif head is TERMS:
            if len(data)==1:
                t, number = data.items()[0]
                @MUL_FACTOR_VALUE_DICT(DICT=pairs; DICT_GET=pairs_get; FACTOR=t; VALUE=1; SIGN=+; USIGN=; NUMBER=number)
                return number
            number = 1
            @MUL_FACTOR_VALUE_DICT(DICT=pairs; DICT_GET=pairs_get; FACTOR=obj; VALUE=1; SIGN=+; USIGN=; NUMBER=number)
            return number
        elif head is FACTORS:
            number = 1
            for t, c in data.iteritems():
                @MUL_FACTOR_VALUE_DICT(DICT=pairs; DICT_GET=pairs_get; FACTOR=t; VALUE=c; SIGN=+; USIGN=; NUMBER=number)
            return number
        else:
            number = 1
            @MUL_FACTOR_VALUE_DICT(DICT=pairs; DICT_GET=pairs_get; FACTOR=obj; VALUE=1; SIGN=+; USIGN=; NUMBER=number)
            return number
    @ELIF_CHECK_NUMBER(T=tobj)
        return obj
    else:
        return inplace_mul(cls, cls.convert(obj), pairs, pairs_get)

def inplace_mul2(cls, obj, exp, pairs, pairs_get, try_power=try_power, NUMBER=NUMBER):
    if not exp:
        return 1
    tobj = type(obj)
    if tobj is cls:
        head, data = obj.pair
        if head is NUMBER:
            return data ** exp
        elif head is TERMS:
            if len(data)==1:
                t, number = data.items()[0]
                number = number ** exp
                @MUL_FACTOR_VALUE_DICT(DICT=pairs; DICT_GET=pairs_get; FACTOR=t; VALUE=exp; SIGN=+; USIGN=; NUMBER=number)
                return number
            number = 1
            @MUL_FACTOR_VALUE_DICT(DICT=pairs; DICT_GET=pairs_get; FACTOR=obj; VALUE=exp; SIGN=+; USIGN=; NUMBER=number)
            return number
        elif head is FACTORS:
            number = 1
            for t, c in data.iteritems():
                @MUL_FACTOR_VALUE_DICT(DICT=pairs; DICT_GET=pairs_get; FACTOR=t; VALUE=c*exp; SIGN=+; USIGN=; NUMBER=number)
            return number
        else:
            number = 1
            @MUL_FACTOR_VALUE_DICT(DICT=pairs; DICT_GET=pairs_get; FACTOR=obj; VALUE=exp; SIGN=+; USIGN=; NUMBER=number)
            return number
    @ELIF_CHECK_NUMBER(T=tobj)
        return obj ** exp
    else:
        return inplace_mul2(cls, cls.convert(obj), exp, pairs, pairs_get)

    ''', globals())

if __name__=='__main__':
    main()
