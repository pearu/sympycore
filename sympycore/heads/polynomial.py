
__all__ = ['SPARSE_POLY', 'DENSE_POLY']

from .base import Head, heads

def init_module(m):
    from .base import heads
    for n,h in heads.iterNameValue(): setattr(m, n, h)

class SparsepolyHead(Head):
    """
    SparsepolyHead is a head for sparse polynomials represented as a
    dictionary of exponent and coefficient pairs, data can be dict or
    frozenset.
    """

    def __repr__(self): return 'SPARSE_POLY'

    def data_to_str_and_precedence(self, cls, data):
        return heads.EXP_COEFF_DICT.data_to_str_and_precedence(cls, (cls.variables, data))

    def to_lowlevel(self, data, pair):
        n = len(data)
        if n==0:
            return 0
        if n==1:
            exp, coeff = data.items()[0]
            if exp==0:
                return coeff
        return pair
    
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
