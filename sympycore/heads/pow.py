
__all__ = ['POW']

from .base import BinaryHead, heads_precedence, Head, Expr, Pair, ArithmeticHead

def init_module(m):
    from ..arithmetic import numbers as n
    m.numbertypes = n.numbertypes
    m.inttypes = n.inttypes
    from .base import heads
    for n,h in heads.iterNameValue(): setattr(m, n, h)

    from ..core import expr_module
    m.dict_add_item = expr_module.dict_add_item
    m.dict_get_item = expr_module.dict_get_item
    m.dict_add_dict = expr_module.dict_add_dict
    m.dict_sub_dict = expr_module.dict_sub_dict
    m.dict_mul_dict = expr_module.dict_mul_dict
    m.dict_mul_value = expr_module.dict_mul_value

class PowHead(ArithmeticHead):
    """ PowHead represents exponentiation operation, data is a 2-tuple
    of base and exponent expressions. Both can be number instances or
    algebra instances.
    """
    op_mth = '__pow__'
    op_rmth = '__rpow__'
    def __repr__(self): return 'POW'

    def new(self, cls, base, exp):
        if exp==1:
            return base
        if exp==0 or base==1:
            return cls(NUMBER, 1)
        return cls(self, (base, exp))

    def data_to_str_and_precedence(self, cls, (base, exp)):
        pow_p = heads_precedence.POW
        div_p = heads_precedence.DIV
        if isinstance(base, Expr):
            b, b_p = base.head.data_to_str_and_precedence(cls, base.data)
        elif isinstance(base, numbertypes):
            b, b_p = NUMBER.data_to_str_and_precedence(cls, base)
        else:
            b, b_p = SYMBOL.data_to_str_and_precedence(cls, base)

        if isinstance(exp, Expr):
            h, d = exp.pair
            if h is NUMBER and isinstance(d, numbertypes):
                exp = d
        if isinstance(exp, numbertypes):
            if exp==0:
                return '1', heads_precedence.NUMBER
            if exp==1:
                return b, b_p
            if exp < 0:
                if exp==-1:
                    s1 = '('+b+')' if b_p <= pow_p else b
                    return '1/' + s1, div_p
                e, e_p = NUMBER.data_to_str_and_precedence(cls, -exp)
                s1 = '('+b+')' if b_p < pow_p else b
                s2 = '('+e+')' if e_p < pow_p else e
                return '1/' + s1 + '**' + s2, div_p
            e, e_p = NUMBER.data_to_str_and_precedence(cls, exp)
        else:
            if isinstance(exp, Expr):
                e, e_p = exp.head.data_to_str_and_precedence(cls, exp.data)
            else:
                e, e_p = str(exp), 0.0
        s1 = '('+b+')' if b_p <= pow_p else b
        s2 = '('+e+')' if e_p < pow_p else e
        return s1 + '**' + s2, pow_p

    def non_commutative_mul(self, cls, lhs, rhs):
        rhead, rdata = rhs.pair
        if rhead is NUMBER:
            return TERM_COEFF.new(cls, lhs, rdata)
        if rhead is SYMBOL or rhead is POW:
            return MUL.combine(cls, [lhs, rhs])
        if rhead is TERM_COEFF:
            term, coeff = rdata
            return (lhs * term) * coeff
        raise NotImplementedError(`self, cls, lhs.pair, rhs.pair`)

    def commutative_mul(self, cls, lhs, rhs):
        rhead, rdata = rhs.pair
        if rhead is NUMBER:
            return TERM_COEFF.new(cls, lhs, rdata)
        if rhead is SYMBOL:
            lbase, lexp = lhs.data
            if lbase == rhs:
                return POW.new(cls, lbase, lexp + 1)
            return cls(BASE_EXP_DICT, {rhs:1, lbase:lexp})
        if rhead is POW:
            lbase, lexp = lhs.data
            rbase, rexp = rdata
            if lbase==rbase:
                return POW.new(cls, lbase, lexp + rexp)
            return cls(BASE_EXP_DICT, {lbase:lexp, rbase:rexp})
        if rhead is BASE_EXP_DICT:
            base, exp = lhs.data
            data = rhs.data.copy()
            dict_add_item(data, base, exp)
            return BASE_EXP_DICT.new(cls, data)
        raise NotImplementedError(`self, cls, lhs.pair, rhs.pair`)

    def as_term_coeff_dict(self, cls, expr):
        return cls(TERM_COEFF_DICT, {expr:1})

    def base_exp(self, cls, expr):
        base, exp = expr.data
        return base, exp

    def pow(self, cls, base, exp):
        if exp==0:
            return cls(NUMBER, 1)
        if exp==1:
            return base
        if isinstance(exp, Expr) and exp.head is NUMBER:
            exp = exp.data
        if isinstance(exp, inttypes):
            b, e = base.data
            base, exp = b, e*exp
        return POW.new(cls, base, exp)

    def expand(self, cls, expr):
        base, exp = expr.data
        if isinstance(exp, Expr):
            exp = exp.expand()
            h, d = exp.pair
            if h is NUMBER and isinstance(d, int):
                exp = d
        if isinstance(base, Expr):
            base = base.expand()
            if isinstance(exp, int):
                return base.head.expand_intpow(cls, base, exp)
        return cls(POW, (base, exp))

POW = PowHead()
