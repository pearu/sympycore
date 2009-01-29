
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
        NUMBER_data_to_str_and_precedence = NUMBER.data_to_str_and_precedence
        m = len(base_exp_dict)
        if not m:
            return '1', heads_precedence.NUMBER
        if m==1:
            return POW.data_to_str_and_precedence(cls, dict_get_item(base_exp_dict))
        mul_p = heads_precedence.MUL
        r = ''
        for base_exp in base_exp_dict.items():
            factors = []
            t, t_p = POW.data_to_str_and_precedence(cls, base_exp)
            if not r:
                r += '(' + t + ')' if t_p < mul_p else t
            elif t.startswith('1/'):
                r += t[1:]
            else:
                r += '*(' + t + ')' if t_p < mul_p else '*' + t
        return r, mul_p

BASE_EXP_DICT = BaseExpDictHead()
