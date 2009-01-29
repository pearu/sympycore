
__all__ = ['SPARSE_POLY', 'DENSE_POLY']

from .base import Head, heads

class SparsepolyHead(Head):
    """
    SparsepolyHead is a head for sparse polynomials represented as a
    dictionary of exponent and coefficient pairs, data can be dict or
    frozenset.
    """

    def __repr__(self): return 'SPARSE_POLY'

    def data_to_str_and_precedence(self, cls, data):
        return heads.EXP_COEFF_DICT.data_to_str_and_precedence(cls, (cls.variables, data))
    
class DensepolyHead(Head):
    """
    DensepolyHead is a head for dense polynomials represented
    as n-tuple of coefficients, data is a 2-tuple (symbol, coeffseq).
    """
    def __repr__(self): return 'DENSE_POLY'

    def data_to_str_and_precedence(self, cls, data):
        # temporary hack
        return self.data_to_str(cls, data, 0.0), self.get_precedence_for_data(data)
    
    def get_precedence_for_data(self, (symbol, data),
                                _p = Head.precedence_map['ADD'],
                                _num_p = Head.precedence_map['NUMBER'],
                                _sym_p = Head.precedence_map['SYMBOL'],
                                _mul_p = Head.precedence_map['MUL'],
                                _pow_p = Head.precedence_map['POW'],
                                _neg_p = Head.precedence_map['NEG'],
                                ):
        if len(data)<=1:
            return _num_p
        n = len(data)-list(data).count(0)
        if n==1:
            c = data[-1]
            if c==1:
                return _pow_p
            if c < 0:
                return _neg_p
            return _mul_p
        return _p

    def data_to_str(self, cls, (symbol, data), parent_precedence,
                    _p = Head.precedence_map['ADD'],
                    _num_p = Head.precedence_map['NUMBER'],
                    _sym_p = Head.precedence_map['SYMBOL'],
                    _mul_p = Head.precedence_map['MUL'],
                    _pow_p = Head.precedence_map['POW'],
                    ):
        precedence = self.get_precedence_for_data((symbol, data))
        terms = []
        SYMBOL_data_to_str = heads.SYMBOL.data_to_str
        NUMBER_data_to_str = heads.NUMBER.data_to_str
        for exp, coeff in enumerate(data):
            if not coeff:
                continue
            if exp:
                if exp==1:
                    if coeff==1:
                        s = SYMBOL_data_to_str(None, symbol, precedence)
                        terms.append(s)
                    else:
                        s1 = NUMBER_data_to_str(None, coeff, _mul_p)
                        s2 = SYMBOL_data_to_str(None, symbol, _mul_p)
                        terms.append(s1 + '*' + s2)
                else:
                    if coeff==1:
                        s1 = SYMBOL_data_to_str(None, symbol, _pow_p)
                        s2 = NUMBER_data_to_str(None, exp, _pow_p)
                        terms.append(s1 + '**' + s2)
                    else:
                        s1 = NUMBER_data_to_str(None, coeff, _mul_p)
                        s2 = SYMBOL_data_to_str(None, symbol, _pow_p)
                        s3 = NUMBER_data_to_str(None, exp, _pow_p)
                        terms.append(s1 + '*' + s2 + '**' + s3)
            else:
                s = NUMBER_data_to_str(None, coeff, precedence)
                terms.append(s)
        if terms:
            r = ' + '.join(terms)
        else:
            return '0'
        if precedence < parent_precedence:
            return '(' + r + ')'
        return r

SPARSE_POLY = SparsepolyHead()
DENSE_POLY = DensepolyHead()
