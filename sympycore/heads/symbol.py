
__all__ = ['SYMBOL']

import re

from .base import AtomicHead, heads_precedence, Expr, Pair, ArithmeticHead

_is_atomic = re.compile(r'\A\w+\Z').match

def init_module(m):
    from ..arithmetic import numbers as n
    m.numbertypes = n.numbertypes
    from .base import heads
    for n,h in heads.iterNameValue(): setattr(m, n, h)

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

    def non_commutative_mul(self, cls, lhs, rhs):
        head, data = rhs.pair
        if head is NUMBER:
            if data==1:
                return lhs
            if data==0:
                return rhs
            return cls(TERM_COEFF, (lhs, data))
        if head is SYMBOL:
            if lhs.data == data:
                return cls(POW, (lhs, 2))
            return cls(MUL, [lhs, rhs])
        if head is TERM_COEFF:
            term, coeff = data
            return (lhs * term) * coeff
        if head is POW:
            return MUL.combine(cls, [lhs, rhs])
        if head is MUL:
            return MUL.combine(cls, [lhs] + data)
        raise NotImplementedError(`self, cls, lhs.pair, rhs.pair`)

    def term_coeff(self, cls, expr):
        return expr, 1

    def neg(self, cls, expr):
        return cls(TERM_COEFF, (expr, -1))

    def as_add(self, cls, expr):
        return cls(ADD, [expr])
    
    def add(self, cls, lhs, rhs):
        h,d = rhs.pair
        if h is SYMBOL:
            if lhs==rhs:
                return cls(TERM_COEFF_DICT, {lhs:2})
            return cls(TERM_COEFF_DICT, {lhs:1, rhs:1})
        if h is NUMBER:
            return cls(TERM_COEFF_DICT, {lhs:1, 1:d})
        lhs = self.as_term_coeff_dict(cls, lhs)
        return lhs.head.add(cls, lhs, rhs)

    def sub(self, cls, lhs, rhs):
        h,d = rhs.pair
        if h is SYMBOL:
            if lhs==rhs:
                return cls(NUMBER, 0)
            return cls(TERM_COEFF_DICT, {lhs:1, rhs:-1})
        if h is NUMBER:
            return cls(TERM_COEFF_DICT, {lhs:1, 1:-d})
        lhs = self.as_term_coeff_dict(cls, lhs)
        return lhs.head.sub(cls, lhs, rhs)


    def as_term_coeff_dict(self, cls, expr):
        return cls(TERM_COEFF_DICT, {expr: 1})

    def base_exp(self, cls, expr):
        return expr, 1

    def pow(self, cls, base, exp):
        if exp==0:
            return cls(NUMBER, 1)
        if exp==1:
            return base
        return cls(POW, (base, exp))

    def expand(self, cls, expr):
        return expr

    def expand_intpow(self, cls, expr, intexp):
        if intexp==0:
            return cls(NUMBER, 1)
        return cls(POW, (expr, intexp))

SYMBOL = SymbolHead()
