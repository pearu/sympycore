
__all__ = ['POW']

from .base import BinaryHead, heads, heads_precedence, Head, Expr, Pair

def init_module(m):
    import sys
    n = sys.modules['sympycore.arithmetic.numbers']
    m.numbertypes = n.numbertypes

class PowHead(BinaryHead):
    """ PowHead represents exponentiation operation, data is a 2-tuple
    of base and exponent expressions.
    """
    precedence = Head.precedence_map['POW'] # obsolete
    op_mth = '__pow__'
    op_rmth = '__rpow__'
    op_symbol = '**' #obsolete
    def __repr__(self): return 'POW'

    def data_to_str_and_precedence(self, cls, (base, exp)):
        pow_p = heads_precedence.POW
        b, b_p = base.head.data_to_str_and_precedence(cls, base.data)
        if isinstance(exp, numbertypes):
            e, e_p = heads.NUMBER.data_to_str_and_precedence(cls, exp)
        else:
            e, e_p = exp.head.data_to_str_and_precedence(cls, exp.data)
        s1 = '('+b+')' if b_p < pow_p else b
        s2 = '('+e+')' if e_p < pow_p else e
        return s1 + '**' + s2, pow_p

    def as_ncmul(self, cls, expr):
        return cls(heads.NCMUL, Pair(1, [expr])) # todo: check expr commutativity

    def base_exp(self, cls, expr):
        base, exp = expr.data
        return base, exp

POW = PowHead()
