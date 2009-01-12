
__all__ = ['NUMBER']

def init_module(m): # will be executed in sympycore/__init__.py
    from ..arithmetic import numbers as n
    m.realtypes = n.realtypes
    m.rationaltypes = n.rationaltypes
    m.complextypes = n.complextypes
    m.numbertypes = n.numbertypes
    m.try_power = n.try_power
    from .base import heads
    for n,h in heads.iterNameValue(): setattr(m, n, h)
            
import re

from .base import Head, Expr, heads_precedence, AtomicHead, Pair


_is_number = re.compile(r'\A[-]?\d+\Z').match
_is_neg_number = re.compile(r'\A-\d+([/]\d+)?\Z').match
_is_rational = re.compile(r'\A\d+[/]\d+\Z').match


class NumberHead(AtomicHead):
    """
    NumberHead is a head for symbols, data can be any Python object.
    """

    def __repr__(self): return 'NUMBER'

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

    def term_coeff(self, cls, expr):
        if isinstance(expr, Expr):
            return cls(NUMBER, 1), expr.data
        return cls(NUMBER, 1), expr

    def get_precedence_for_data(self, data): # obsolete
        if isinstance(data, complextypes):
            # todo: check for pure imaginary numbers
            return heads_precedence.ADD
        elif isinstance(data, rationaltypes):
            if data < 0:
                return heads_precedence.NEG
            return heads_precedence.DIV
        elif isinstance(data, realtypes):
            if data < 0:
                return heads_precedence.NEG
            return heads_precedence.NUMBER
        elif isinstance(data, Expr):
            h, d = data.pair
            return h.get_precedence_for_data(d)
        return heads_precedence.NUMBER
    
    def neg(self, cls, expr):
        return cls(self, -expr.data)

    def as_add(self, cls, expr):
        return cls(ADD, [expr])

    def as_term_coeff_dict(self, cls, expr):
        return cls(TERM_COEFF_DICT, {1: expr.data})
    
    def add(self, cls, lhs, rhs):
        h, d = rhs.pair
        if h is NUMBER:
            return cls(NUMBER, lhs.data + d)
        if h is SYMBOL:
            if lhs==0:
                return rhs
            return cls(ADD, [lhs, rhs])
        if h is ADD:
            terms = []
            for term in d:
                h1, c = term
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
        raise NotImplementedError(`self, lhs, rhs`)

    def as_ncmul(self, cls, expr):
        return cls(NCMUL, Pair(expr, []))

    def ncmul(self, cls, lhs, rhs):
        if rhs.head is NUMBER:
            return cls(NUMBER, lhs.data * rhs.data)
        lhs = self.as_ncmul(cls, lhs)
        return lhs.head.ncmul(cls, lhs, rhs)

    def pow(self, cls, base, exp):
        if isinstance(base, Expr):
            h, d = base.pair
            if h is NUMBER and isinstance(d, numbertypes):
                base = d
                if isinstance(exp, Expr):
                    h, d = exp.pair
                    if h is NUMBER and isinstance(d, numbertypes):
                        exp = d
        if isinstance(base, numbertypes):
            if isinstance(exp, Expr):
                h, d = exp.pair
                if h is NUMBER and isinstance(d, numbertypes):
                    exp = d
        if isinstance(base, numbertypes) and isinstance(exp, numbertypes):
            r, base_exp_list = try_power(base, exp)
            if not base_exp_list:
                return cls(NUMBER, r)
            return cls(MUL, [cls(NUMBER,r)] + [cls(POW, (cls(NUMBER, b), e)) for b,e in base_exp_list])
        return cls(POW, (base, exp))

    def expand(self, cls, expr):
        return expr

NUMBER = NumberHead()
