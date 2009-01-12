__all__ = ['SUB']

from .base import NaryHead, Head, heads_precedence, ArithmeticHead

class SubHead(ArithmeticHead, NaryHead):

    """
    SubHead represents subtraction n-ary operation where operands is
    given as a n-tuple of expressions.
    """
    precedence = Head.precedence_map['SUB']
    op_mth = '__sub__'
    op_rmth = '__rsub__'
    op_symbol = ' - '
    def __repr__(self): return 'SUB'

    def data_to_str_and_precedence(self, cls, sub_list):
        num_p = heads_precedence.NUMBER
        m = len(sub_list)
        if not m:
            return '0', num_p
        add_p = heads_precedence.ADD
        r = ''
        for term in sub_list:
            h, d = term.pair
            t,t_p = h.data_to_str_and_precedence(cls, d)
            if m>1:
                if not r:
                    r += '(' + t + ')' if t_p < add_p else t
                elif t.startswith('-'):
                    r += ' + ' + t[1:]
                else:
                    r += ' - (' + t + ')' if t_p < add_p else ' - ' + t
            else:
                return t, t_p
        return r, add_p


SUB = SubHead()
