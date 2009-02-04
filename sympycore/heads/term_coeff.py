
__all__ = ['TERM_COEFF']

from .base import heads_precedence, ArithmeticHead, Expr

def init_module(m):
    from ..arithmetic import numbers as n
    m.numbertypes = n.numbertypes
    m.inttypes = n.inttypes
    from .base import heads
    for n,h in heads.iterNameValue(): setattr(m, n, h)

class TermCoeff(ArithmeticHead):
    """ Expr(TERM_COEFF, (term, coeff)) represents term*coeff
    where term is symbolic expression and coeff is a number or
    symbolic expression.
    """

    def __repr__(self): return 'TERM_COEFF'

    def new(self, cls, term, coeff):
        if coeff==1:
            return term
        if coeff==0 or term==1:
            return coeff
        return cls(self, (term, coeff))

    def data_to_str_and_precedence(self, cls, (term, coeff)):
        neg_p = heads_precedence.NEG
        mul_p = heads_precedence.MUL
        if term==1:
            t, t_p = NUMBER.data_to_str_and_precedence(cls, coeff)
        elif coeff==1:
            t, t_p = term.head.data_to_str_and_precedence(cls, term.data)
        elif coeff==-1:
            t, t_p = term.head.data_to_str_and_precedence(cls, term.data)
            t, t_p = ('-('+t+')' if t_p < mul_p else '-' + t), neg_p
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

    def non_commutative_mul(self, cls, lhs, rhs):
        term, coeff = lhs.data
        head, data = rhs.pair
        if head is NUMBER:
            return TERM_COEFF.new(cls, term, coeff * data)
        return (term * rhs) * coeff

    commutative_mul = non_commutative_mul

    def pow(self, cls, base, exp):
        term, coeff = base.data
        if isinstance(exp, Expr):
            head, data = exp.pair
            if head is NUMBER:
                exp = data
        if isinstance(exp, inttypes):
            if exp<0:
                return term ** exp / coeff ** (-exp)
            return term ** exp * coeff ** exp
        return POW.new(cls, base, exp)

TERM_COEFF = TermCoeff()
