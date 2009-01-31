__all__ = ['SUB']

from .base import heads_precedence, ArithmeticHead

class SubHead(ArithmeticHead):

    """
    SubHead represents subtraction n-ary operation where operands is
    given as a n-tuple of expressions.
    """
    op_mth = '__sub__'
    op_rmth = '__rsub__'

    def __repr__(self): return 'SUB'
    
    def data_to_str_and_precedence(self, cls, operands):
        m = len(operands)
        if m==0:
            return '0', heads_precedence.NUMBER
        if m==1:
            op = operands[0]
            return op.head.data_to_str_and_precedence(cls, op.data)
        sub_p = heads_precedence.SUB
        r = ''
        for op in operands:
            t,t_p = op.head.data_to_str_and_precedence(cls, op.data)
            if not r:
                r += '(' + t + ')' if t_p < sub_p else t
            elif t.startswith('-') and t_p > sub_p:
                r += ' + ' + t[1:]
            else:
                r += ' - (' + t + ')' if t_p <= sub_p else ' - ' + t
        return r, sub_p


SUB = SubHead()
