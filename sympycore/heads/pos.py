
__all__ = ['POS']

from .base import UnaryHead, heads_precedence, ArithmeticHead

class PosHead(ArithmeticHead, UnaryHead):

    """
    PosHead represents positive unary operation where operand (data)
    is an expression.
    """

    op_mth = '__pos__'
    
    op_symbol = '+' # obsolete
    precedence = UnaryHead.precedence_map['POS'] # obsolete
    
    def __repr__(self): return 'POS'

    def data_to_str_and_precedence(self, cls, data):
        h, d = data.pair
        s, s_p = h.data_to_str_and_precedence(cls, d)
        if s_p < heads_precedence.POS:
            return '+(' + s + ')', heads_precedence.POS
        return '+' + s, heads_precedence.POS

POS = PosHead()
