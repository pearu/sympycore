
__all__ = ['NEG']

from .base import heads_precedence, ArithmeticHead
from ..core import init_module

init_module.import_heads()
init_module.import_numbers()

class NegHead(ArithmeticHead):

    """
    NegHead represents negative unary operation where operand (data)
    is an expression.
    """

    op_mth = '__neg__'

    def is_data_ok(self, cls, data):
        if not isinstance(data, cls):
            return '%s data part must be %s instance but got %s' % (self, cls, type(data))
        
    def __repr__(self): return 'NEG'

    def new(self, cls, expr, evaluate=True):
        if not evaluate:
            return cls(self, expr)
        h, d = expr.pair
        if h is NUMBER:
            return cls(NUMBER, -d)
        if h is TERM_COEFF:
            t, c = d
            return TERM_COEFF.new(cls, (t, -c))
        return cls(NEG, expr)

    def reevaluate(self, cls, expr):
        return -expr

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
        if data.head is NUMBER:
            return -data.data
        return cls(TERM_COEFF, (data, -1))

    def term_coeff(self, cls, expr):
        e = expr.data
        t, c = e.head.term_coeff(cls, e)
        return t, -c

    def scan(self, proc, cls, expr, target):
        expr.head.scan(proc, cls, expr.data, target)
        proc(cls, self, expr, target)

    def walk(self, func, cls, operand, target):
        operand1 = operand.head.walk(func, cls, operand.data, operand)
        if operand1 is operand:
            return func(cls, self, operand, target)
        r = self.new(cls, operand1)
        return func(cls, r.head, r.data, r)

NEG = NegHead()
