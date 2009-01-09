
__all__ = ['TERM_COEFF_DICT']

from .base import Head, heads, heads_precedence

def init_module(m):
    from .base import heads
    for n,h in heads.iterNameValue(): setattr(m, n, h)
    from ..core import expr_module
    m.dict_add_item = expr_module.dict_add_item
    m.dict_get_item = expr_module.dict_get_item
    m.dict_add_dict = expr_module.dict_add_dict
    m.dict_sub_dict = expr_module.dict_sub_dict

class TermCoeffDictHead(Head):

    def __repr__(self): return 'TERM_COEFF_DICT'

    def term_coeff(self, cls, expr):
        term_coeff_dict = expr.data
        if len(term_coeff_dict)==1:
            return term_coeff_dict.items()[0]
        return expr, 1

    def data_to_str_and_precedence(self, cls, term_coeff_dict):
        NUMBER_data_to_str_and_precedence = NUMBER.data_to_str_and_precedence
        neg_p = heads_precedence.NEG
        add_p = heads_precedence.ADD
        mul_p = heads_precedence.MUL
        num_p = heads_precedence.NUMBER
        m = len(term_coeff_dict)
        is_add = m>1
        r = ''
        one = cls(NUMBER, 1)
        for term, coeff in term_coeff_dict.items():
            factors = []
            if term==one:
                t, t_p = NUMBER_data_to_str_and_precedence(cls, coeff)
            elif coeff==1:
                t, t_p = term.head.data_to_str_and_precedence(cls, term.data)
            elif coeff==-1:
                t, t_p = term.head.data_to_str_and_precedence(cls, term.data)
                t, t_p = ('-('+t+')' if t_p < neg_p else '-' + t), neg_p
            else:
                t, t_p = term.head.data_to_str_and_precedence(cls, term.data)
                c, c_p = NUMBER_data_to_str_and_precedence(cls, coeff)            
                t = ('('+c+')' if c_p < mul_p else c) +'*'+ ('('+t+')' if t_p < mul_p else t)
                t_c = mul_p
            if is_add:
                if not r:
                    r += '(' + t + ')' if t_p < add_p else t
                elif t.startswith('-'):
                    r += ' - ' + t[1:]
                else:
                    r += ' + (' + t + ')' if t_p < add_p else ' + ' + t
            elif m:
                return t, t_p
            else:
                return '0', num_p
        return r, add_p

    def as_add(self, cls, expr):
        add_list = []
        for term, coeff in expr.data.items():
            add_list.append(term * coeff)
        return cls(ADD, add_list)

    def add(self, cls, lhs, rhs):
        
        d = lhs.data.copy()
        h2, d2 = rhs.pair

        if h2 is SYMBOL:
            dict_add_item(d, rhs, 1)
        elif h2 is NUMBER:
            dict_add_item(d, 1, d2)
        elif h2 is TERM_COEFF_DICT:
            dict_add_dict(d, d2)
        else:
            rhs = h2.as_term_coeff_dict(cls, rhs)
            dict_add_dict(d, rhs.data)

        if len(d)==1:
            t,c = dict_get_item(d)
            if c==1:
                return t
            if t==1:
                return cls(NUMBER, c)
        return cls(TERM_COEFF_DICT, d)

    def sub(self, cls, lhs, rhs):
        d = lhs.data.copy()
        h2, d2 = rhs.pair

        if h2 is SYMBOL:
            dict_add_item(d, rhs, -1)
        elif h2 is NUMBER:
            dict_add_item(d, 1, -d2)
        elif h2 is TERM_COEFF_DICT:
            dict_sub_dict(d, d2)
        else:
            rhs = h2.as_term_coeff_dict(cls, rhs)
            dict_sub_dict(d, rhs.data)

        if len(d)==1:
            t,c = dict_get_item(d)
            if c==1:
                return t
            if t==1:
                return cls(NUMBER, c)
        return cls(TERM_COEFF_DICT, d)

    def pow(self, cls, base, exp):
        if exp==0:
            return cls(NUMBER, 1)
        if exp==1:
            return base
        return cls(POW, (base, exp))

    def neg(self, cls, expr):
        d = expr.data.copy()
        for key in d:
            d[key] = -d[key]
        return cls(TERM_COEFF_DICT, d)


TERM_COEFF_DICT = TermCoeffDictHead()
