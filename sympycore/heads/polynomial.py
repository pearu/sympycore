
__all__ = ['SPARSE_POLY', 'DENSE_POLY']

from .base import Head, heads

from ..core import init_module, Pair
init_module.import_heads()

class SparsepolyHead(Head):
    """
    SparsepolyHead is a head for sparse polynomials represented as a
    dictionary of exponent and coefficient pairs, data can be dict or
    frozenset.
    """

    def __repr__(self): return 'SPARSE_POLY'

    def data_to_str_and_precedence(self, cls, data):
        return EXP_COEFF_DICT.data_to_str_and_precedence(cls, Pair(cls.variables, data))

    def reevaluate(self, cls, data):
        return cls(self, data)

    def to_lowlevel(self, cls, data, pair):
        return EXP_COEFF_DICT.to_lowlevel(cls, Pair(cls.variables, data), pair)

    def add(self, cls, lhs, rhs):
        rhead, rdata = rhs.pair
        if rhead is not self:
            rhs = rhead.to_SPARSE_POLY(cls, rdata, rhs)
            return lhs + rhs
        return NotImplemented

    inplace_add = add

    def sub(self, cls, lhs, rhs):
        return lhs + (-rhs)

    def commutative_mul(self, cls, lhs, rhs):
        rhead, rdata = rhs.pair
        if rhead is not self:
            rhs = rhead.to_SPARSE_POLY(cls, rdata, rhs)
            return lhs * rhs
        return NotImplemented

    def term_coeff(self, cls, expr):
        return expr, 1

class DensepolyHead(Head):
    """
    DensepolyHead is a head for dense polynomials represented
    as n-tuple of coefficients, data is a 2-tuple (symbol, coeffseq).
    """
    def __repr__(self): return 'DENSE_POLY'

    def data_to_str_and_precedence(self, cls, (symbol, data)):
        if not isinstance(symbol, cls):
            symbol = cls(SYMBOL, symbol)
        terms = []
        for exp, coeff in enumerate(data):
            if coeff:
                terms.append(cls(TERM_COEFF, (cls(POW, (symbol, exp)), coeff)))
        return ADD.data_to_str_and_precedence(cls, terms)
                     
SPARSE_POLY = SparsepolyHead()
DENSE_POLY = DensepolyHead()
