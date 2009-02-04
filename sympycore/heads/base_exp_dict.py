
__all__ = ['BASE_EXP_DICT']

from .base import heads, heads_precedence, ArithmeticHead

def init_module(m):
    from .base import heads
    for n,h in heads.iterNameValue(): setattr(m, n, h)
    from ..core import expr_module
    m.dict_add_item = expr_module.dict_add_item
    m.dict_get_item = expr_module.dict_get_item
    m.dict_add_dict = expr_module.dict_add_dict
    #m.dict_sub_dict = expr_module.dict_sub_dict
    #m.dict_mul_dict = expr_module.dict_mul_dict
    #m.dict_mul_value = expr_module.dict_mul_value

class BaseExpDictHead(ArithmeticHead):

    def __repr__(self): return 'BASE_EXP_DICT'

    def data_to_str_and_precedence(self, cls, base_exp_dict):
        factors = [cls(POW, p) for p in base_exp_dict.items()]
        return MUL.data_to_str_and_precedence(cls, factors)

    def new(self, cls, base_exp_dict):
        m = len(base_exp_dict)
        if m==0:
            return cls(NUMBER, 1)
        if m==1:
            base, exp = dict_get_item(base_exp_dict)
            return POW.new(cls, base, exp)
        return cls(BASE_EXP_DICT, base_exp_dict)

    def commutative_mul(self, cls, lhs, rhs):
        rhead, rdata = rhs.pair
        if rhead is NUMBER:
            return cls(TERM_COEFF, (lhs, rdata))
        if rhead is SYMBOL:
            data = lhs.data.copy()
            dict_add_item(data, rhs, 1)
            return BASE_EXP_DICT.new(cls, data)
        if rhead is TERM_COEFF:
            term, coeff = rdata
            return (lhs * term) * coeff
        if rhead is BASE_EXP_DICT:
            data = lhs.data.copy()
            dict_add_dict(data, rhs.data)
            return BASE_EXP_DICT.new(cls, data)
        raise NotImplementedError(`self, cls, lhs.pair, rhs.pair`)

BASE_EXP_DICT = BaseExpDictHead()
