
__all__ = ['NEG']

from .base import heads_precedence, ArithmeticHead

def init_module(m):
    from ..arithmetic import numbers as n
    m.numbertypes = n.numbertypes
    from .base import heads
    for n,h in heads.iterNameValue(): setattr(m, n, h)

class NegHead(ArithmeticHead):

    """
    NegHead represents negative unary operation where operand (data)
    is an expression.
    """

    op_mth = '__neg__'
        
    def __repr__(self): return 'NEG'

    def data_to_str_and_precedence(self, cls, expr):
        if expr.head is NEG:
            expr = expr.data
            return expr.head.data_to_str_and_precedence(cls, expr.data)
        s, s_p = expr.head.data_to_str_and_precedence(cls, expr.data)
        neg_p = heads_precedence.NEG
        if s_p < neg_p:
            return '-(' + s + ')', neg_p
        return '-' + s, neg_p

    def to_lowlevel(self, cls, data, pair):
        if isinstance(data, numbertypes):
            return -data
        return cls(TERM_COEFF, (data, -1))

NEG = NegHead()
