
__all__ = ['BASE_EXP_DICT']

from .base import heads, heads_precedence, ArithmeticHead

def init_module(m):
    from .base import heads
    for n,h in heads.iterNameValue(): setattr(m, n, h)
    from ..core import expr_module
    #m.dict_add_item = expr_module.dict_add_item
    m.dict_get_item = expr_module.dict_get_item
    #m.dict_add_dict = expr_module.dict_add_dict
    #m.dict_sub_dict = expr_module.dict_sub_dict
    #m.dict_mul_dict = expr_module.dict_mul_dict
    #m.dict_mul_value = expr_module.dict_mul_value

class BaseExpDictHead(ArithmeticHead):

    def __repr__(self): return 'BASE_EXP_DICT'

    def data_to_str_and_precedence(self, cls, base_exp_dict):
        factors = [cls(POW, p) for p in base_exp_dict.items()]
        return MUL.data_to_str_and_precedence(cls, factors)

BASE_EXP_DICT = BaseExpDictHead()
