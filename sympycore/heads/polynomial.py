
__all__ = ['SPARSE_POLY', 'DENSE_POLY']

from .base import Head

class SparsepolyHead(Head):
    """
    SparsepolyHead is a head for sparse polynomials represented as a
    dictionary of exponent and coefficient pairs, data can be dict or
    frozenset.
    """
    def data_to_str(self, cls, data, parent_precedence):
        if not data:
            return '0'
        symbols = map(str, cls.variables)
        is_univariate = len(symbols)==1
        terms = []
        for exps in sorted(data.keys(), reverse=True):
            coeff = data[exps]
            if coeff==1:
                factors = []
            else:
                factors = ['%s' % (coeff,)]
            if is_univariate:
                if exps:
                    if exps==1:
                        factors.append(symbols[0])
                    else:
                        factors.append('%s**%s' % (symbols[0], exps))
            else:
                for s,e in zip(symbols, exps):
                    if e==1:
                        factors.append(s)
                    else:
                        factors.append('%s**%s' % (s, e))
            if factors:
                terms.append('*'.join(factors))
            else:
                terms.append('1')
        r = ' + '.join(terms)
        return r
    

class DensepolyHead(Head):
    """
    DensepolyHead is a head for dense polynomials represented
    as n-tuple of coefficients, data is a 2-tuple (symbol, coeffseq).
    """
    def data_to_str(self, cls, (symbol, data), parent_precedence):
        str_symbol = str(symbol)
        terms = []
        for exp, coeff in enumerate(data):
            if not coeff:
                continue
            if exp:
                if exp==1:
                    if coeff==1:
                        terms.append(str_symbol)
                    else:
                        terms.append('%s*%s' % (coeff, str_symbol))
                else:
                    if coeff==1:
                        terms.append('%s**%s' % (str_symbol, exp))
                    else:
                        terms.append('%s*%s**%s' % (coeff, str_symbol, exp))
            else:
                terms.append('%s' % (coeff,))
        if terms:
            r = ' + '.join(terms)
        else:
            r = '0'
        return r

SPARSE_POLY = SparsepolyHead()
DENSE_POLY = DensepolyHead()
