
__all__ = ['SPARSE_POLY', 'DENSE_POLY']

from .base import Head, heads

class SparsepolyHead(Head):
    """
    SparsepolyHead is a head for sparse polynomials represented as a
    dictionary of exponent and coefficient pairs, data can be dict or
    frozenset.
    """

    def __repr__(self): return 'SPARSE_POLY'
    
    def get_precedence_for_data(self, data,
                                _p = Head.precedence_map['ADD'],
                                _num_p = Head.precedence_map['NUMBER'],
                                _sym_p = Head.precedence_map['SYMBOL'],
                                _mul_p = Head.precedence_map['MUL'],
                                ):
        if not data:
            return _num_p
        if len(data)==1:
            e, c = data.items()[0]
            if c==1:
                return _sym_p
            return _mul_p
        return _p
    
    def data_to_str(self, cls, data, parent_precedence,
                    _p = Head.precedence_map['ADD'],
                    _mul_p = Head.precedence_map['MUL'],
                    _pow_p = Head.precedence_map['POW']
                    ):
        if not data:
            return '0'
        preference = self.get_precedence_for_data(data)
        symbols = cls.variables
        is_univariate = len(symbols)==1
        terms = []
        SYMBOL_data_to_str = heads.SYMBOL.data_to_str
        NUMBER_data_to_str = heads.NUMBER.data_to_str
        for exps in sorted(data.keys(), reverse=True):
            coeff = data[exps]
            if coeff==1:
                p0 = _p
                factors = []
            else:
                p0 = _mul_p
                s = NUMBER_data_to_str(None, coeff, _mul_p)
                factors = [s]
            if is_univariate:
                symbol = symbols[0]
                if exps:
                    if exps==1:
                        s = SYMBOL_data_to_str(None, symbol, p0)
                        factors.append(s)
                    else:
                        s = SYMBOL_data_to_str(None, symbol, _pow_p)
                        factors.append('%s**%s' % (s, exps))
                    
            else:
                for symbol,e in zip(symbols, exps):
                    if e==1:
                        s = SYMBOL_data_to_str(None, symbol, p0)
                        factors.append(s)
                    else:
                        s = SYMBOL_data_to_str(None, symbol, _pow_p)
                        factors.append('%s**%s' % (s, e))
            if factors:
                terms.append('*'.join(factors))
            else:
                terms.append('1')
        r = ' + '.join(terms)
        if preference < parent_precedence:
            return '(' + r + ')'
        return r
    

class DensepolyHead(Head):
    """
    DensepolyHead is a head for dense polynomials represented
    as n-tuple of coefficients, data is a 2-tuple (symbol, coeffseq).
    """
    def __repr__(self): return 'DENSE_POLY'

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
