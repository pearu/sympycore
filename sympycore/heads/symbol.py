
__all__ = ['SYMBOL']

import re

from .base import AtomicHead, heads_precedence, Expr, heads, Pair

_is_atomic = re.compile(r'\A\w+\Z').match

def init_module(m):
    import sys
    n = sys.modules['sympycore.arithmetic.numbers']
    m.numbertypes = n.numbertypes

class SymbolHead(AtomicHead):
    """
    SymbolHead is a head for symbols, data can be any Python object.
    """

    def __repr__(self): return 'SYMBOL'

    def data_to_str_and_precedence(self, cls, data):
        if isinstance(data, Expr):
            h, d = data.pair
            return h.data_to_str_and_precedence(cls, d)
        s = str(data)
        if _is_atomic(s):
            return s, heads_precedence.SYMBOL
        return s, 0.0 # force parenthesis

    def get_precedence_for_data(self, data, # obsolete
                                _p = heads_precedence.SYMBOL):
        if isinstance(data, Expr):
            h, d = data.pair
            return h.get_precedence_for_data(d)
        return _p

    def term_coeff(self, cls, expr):
        return expr, 1

    def neg(self, cls, expr):
        return cls(heads.TERM_COEFF_DICT, {expr:-1})

    def as_add(self, cls, expr):
        return cls(heads.ADD, [expr])
    
    def add(self, cls, lhs, rhs):
        if lhs==rhs:
            return cls(heads.TERM_COEFF_DICT, {lhs:2})
        h = rhs.head
        if h is self:
            return cls(heads.ADD, [lhs, rhs])
        if h is heads.NUMBER:
            return cls(heads.ADD, [lhs, rhs])
        raise NotImplementedError(`self, lhs, rhs`)

    def as_ncmul(self, cls, expr):
        return cls(heads.NCMUL, Pair(1, [expr])) # todo: check expr commutativity

    def base_exp(self, cls, expr):
        return expr, 1

    def ncmul(self, cls, lhs, rhs):
        if lhs==rhs:
            return cls(heads.POW, (lhs, 2))
        h = rhs.head
        if h is SYMBOL:
            return cls(heads.NCMUL, (1, [lhs, rhs]))
        lhs = self.as_ncmul(cls, lhs)
        return lhs.head.ncmul(cls, lhs, rhs)
        if h is heads.NCMUL:
            return heads.NCMUL.ncmul(cls, lhs.head.as_ncmul(cls, lhs), rhs)
        raise NotImplementedError(`self, lhs, h, rhs`)

    def pow(self, cls, base, exp):
        if exp==0:
            return cls(heads.NUMBER, 1)
        if exp==1:
            return base
        h, d = exp.pair
        if h is heads.NUMBER:
            return cls(heads.POW, (base, exp))
        if h is SYMBOL:
            return cls(heads.POW, (base, exp))
        raise NotImplementedError(`self, base, exp`)

SYMBOL = SymbolHead()
