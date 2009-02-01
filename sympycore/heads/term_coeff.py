
__all__ = ['TERM_COEFF']

from .base import heads_precedence, ArithmeticHead

def init_module(m):
    from .base import heads
    for n,h in heads.iterNameValue(): setattr(m, n, h)

class TermCoeff(ArithmeticHead):
    """ Expr(TERM_COEFF, (term, coeff)) represents term*coeff
    where term is symbolic expression and coeff is a number or
    symbolic expression.
    """

    def __repr__(self): return 'TERM_COEFF'

    def data_to_str_and_precedence(self, cls, (term, coeff)):
        neg_p = heads_precedence.NEG
        mul_p = heads_precedence.MUL
        if term==1:
            t, t_p = NUMBER.data_to_str_and_precedence(cls, coeff)
        elif coeff==1:
            t, t_p = term.head.data_to_str_and_precedence(cls, term.data)
        elif coeff==-1:
            t, t_p = term.head.data_to_str_and_precedence(cls, term.data)
            t, t_p = ('-('+t+')' if t_p < neg_p else '-' + t), neg_p
        elif coeff==0:
            t, t_p = '0', heads_precedence.NUMBER
        else:
            t, t_p = term.head.data_to_str_and_precedence(cls, term.data)
            c, c_p = NUMBER.data_to_str_and_precedence(cls, coeff)            
            cs = '('+c+')' if c_p < mul_p else c
            ts = '('+t+')' if t_p < mul_p else t
            t = cs + (ts[1:] if ts.startswith('1/') else '*' + ts)
            t_p = mul_p
        return t, t_p

    def as_ncmul(self, cls, expr):
        t, c = expr.data
        return cls(NCMUL, Pair(c, [t]))

TERM_COEFF = TermCoeff()
