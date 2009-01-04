
__all__ = ['TERM_COEFF_DICT']

from .base import Head, heads, heads_precedence

class TermCoeffDictHead(Head):

    def __repr__(self): return 'TERM_COEFF_DICT'

    def data_to_str_and_precedence(self, cls, term_coeff_dict):
        NUMBER_data_to_str_and_precedence = heads.NUMBER.data_to_str_and_precedence
        neg_p = heads_precedence.NEG
        add_p = heads_precedence.ADD
        mul_p = heads_precedence.MUL
        num_p = heads_precedence.NUMBER
        m = len(term_coeff_dict)
        is_add = m>1
        r = ''
        one = cls(heads.NUMBER, 1)
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

TERM_COEFF_DICT = TermCoeffDictHead()
