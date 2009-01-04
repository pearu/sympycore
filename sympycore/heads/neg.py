
__all__ = ['NEG']

from .base import UnaryHead, heads_precedence

class NegHead(UnaryHead):

    """
    PosHead represents positive unary operation where operand (data)
    is an expression.
    """

    op_mth = '__neg__'
    
    op_symbol = '-' # obsolete
    precedence = UnaryHead.precedence_map['NEG'] # obsolete
    
    def __repr__(self): return 'NEG'

    def data_to_str_and_precedence(self, cls, data):
        h, d = data.pair
        s, s_p = h.data_to_str_and_precedence(cls, d)
        if s_p < heads_precedence.NEG:
            return '-(' + s + ')', heads_precedence.NEG
        return '-' + s, heads_precedence.NEG

NEG = NegHead()
