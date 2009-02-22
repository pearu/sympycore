
__all__ = ['NUMBER']

import re

from .base import Head, Expr, heads_precedence, AtomicHead, Pair

from ..core import init_module
init_module.import_heads()
init_module.import_numbers()
init_module.import_lowlevel_operations()

@init_module
def _init(module):
    from ..arithmetic.numbers import try_power
    module.try_power = try_power
    
_is_number = re.compile(r'\A[-]?\d+\Z').match
_is_neg_number = re.compile(r'\A-\d+([/]\d+)?\Z').match
_is_rational = re.compile(r'\A\d+[/]\d+\Z').match

class NumberHead(AtomicHead):
    """
    NumberHead is a head for symbols, data can be any Python object.
    """

    def __repr__(self): return 'NUMBER'

    def new(self, cls, data):
        if isinstance(data, Infinity):
            return data
        return cls(NUMBER, data)

    def reevaluate(self, cls, data):
        return cls(self, data)

    def is_data_ok(self, cls, data):
        return

    def nonzero(self, cls, data):
        return data

    def to_SPARSE_POLY(self, cls, data, expr):
        return cls(data)
        
    def to_EXP_COEFF_DICT(self, cls, data, expr, variables = None):
        if variables is None:
            variables = ()
        return cls(EXP_COEFF_DICT, Pair(variables, {(0,)*len(variables):data}))

    def data_to_str_and_precedence(self, cls, data):
        if isinstance(data, complextypes):
            r, i = data.real, data.imag
            if r!=0 and i!=0:
                return str(data), heads_precedence.ADD
            if r==0:
                if i<0:
                    return str(data), heads_precedence.NEG
                return str(data), heads_precedence.NUMBER
            return self.data_to_str_and_precedence(self, cls, r)
        elif isinstance(data, rationaltypes):
            if data < 0:
                return str(data), heads_precedence.NEG
            return str(data), heads_precedence.DIV
        elif isinstance(data, realtypes):
            if data < 0:
                return str(data), heads_precedence.NEG
            return str(data), heads_precedence.NUMBER
        elif isinstance(data, Expr):
            h, d = data.pair
            return h.data_to_str_and_precedence(cls, d)
        return str(data), 0.0 # force parenthesis

    def non_commutative_mul(self, cls, lhs, rhs):
        head, data = rhs.pair
        if head is NUMBER:
            return cls(NUMBER, lhs.data * data)
        # Numbers are ring commutants:
        return rhs.head.non_commutative_mul(cls, rhs, lhs)

    def commutative_mul(self, cls, lhs, rhs):
        head, data = rhs.pair
        if head is NUMBER:
            return cls(NUMBER, lhs.data * data)
        return rhs.head.commutative_mul(cls, rhs, lhs)
    
    def term_coeff(self, cls, expr):
        if isinstance(expr, Expr):
            return cls(NUMBER, 1), expr.data
        return cls(NUMBER, 1), expr

    def neg(self, cls, expr):
        return cls(self, -expr.data)

    def add(self, cls, lhs, rhs):
        if lhs==0:
            return rhs
        h, d = rhs.pair
        if h is NUMBER:
            return cls(NUMBER, lhs.data + d)
        if h is SYMBOL:
            if lhs==0:
                return rhs
            return cls(TERM_COEFF_DICT, {cls(NUMBER,1): lhs.data, rhs:1})
        if h is ADD:
            terms = []
            for term in d:
                h1, c = term.pair
                if h1 is NUMBER:
                    c = lhs.data + c
                    if c:
                        terms.append(cls(NUMBER, c))
                else:
                    terms.append(term)
            if not terms:
                return cls(NUMBER, 0)
            if len(terms)==1:
                return terms[0]
            return cls(ADD, terms)
        if h is TERM_COEFF:
            term, coeff = d
            return cls(TERM_COEFF_DICT, {term:coeff, cls(NUMBER,1):lhs.data})
        if h is POW or h is BASE_EXP_DICT:
            return cls(TERM_COEFF_DICT, {cls(NUMBER,1):lhs.data, rhs:1})
        if h is TERM_COEFF_DICT:
            data = d.copy()
            dict_add_item(cls, data, cls(NUMBER,1), lhs.data)
            return TERM_COEFF_DICT.new(cls, data)
        raise NotImplementedError(`self, lhs.pair, rhs.pair`)

    def sub(self, cls, lhs, rhs):
        return lhs + (-rhs)

    def pow(self, cls, base, exp):
        return POW.new(cls, (base, exp))

    def expand(self, cls, expr):
        return expr

NUMBER = NumberHead()
