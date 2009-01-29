
__all__ = ['EXP_COEFF_DICT']

from .base import Head, heads_precedence, Expr

def init_module(m):
    from .base import heads
    for n,h in heads.iterNameValue(): setattr(m, n, h)

class ExpCoeffDict(Head):
    """
    """

    def __repr__(self): return 'EXP_COEFF_DICT'

    def data_to_str_and_precedence(self, cls, (variables, exp_coeff_dict)):
        # This is a complete solution for converting expressions to
        # string with correct placement of parentheses.
        SYMBOL_data_to_str_and_precedence = SYMBOL.data_to_str_and_precedence
        NUMBER_data_to_str_and_precedence = NUMBER.data_to_str_and_precedence
        pow_p = heads_precedence.POW
        mul_p = heads_precedence.MUL
        add_p = heads_precedence.ADD
        num_p = heads_precedence.NUMBER
        terms_precedence = []
        t_append = terms_precedence.append
        vars_precedence = [SYMBOL_data_to_str_and_precedence(None, var) for var in variables]
        m = len(exp_coeff_dict)
        is_add = (m > 1)
        r = ''
        for exps in sorted(exp_coeff_dict, reverse=True):
            factors_precedence = [NUMBER_data_to_str_and_precedence(None, exp_coeff_dict[exps])]
            f_append = factors_precedence.append
            if not isinstance(exps, tuple):
                # temporary hook for SPARSE_POLY head, remove if block when SPARSE_POLY is gone
                exps = (exps,)
            for exp, vv_p in zip(exps, vars_precedence):
                if exp:
                    if exp==1:
                        f_append(vv_p)
                    else:
                        e, e_p = NUMBER_data_to_str_and_precedence(None, exp)
                        v_s = '(' + vv_p[0] + ')' if vv_p[1] < pow_p else vv_p[0]
                        e_s = '(' + e + ')' if e_p < pow_p else e
                        f_append((v_s + '**' + e_s, pow_p))

            n = len(factors_precedence)
            if n>1:
                t, t_p = '', mul_p
                for f, f_p in factors_precedence:
                    if not t:
                        t += '(' + f + ')' if f_p<t_p else f
                    else:
                        t += '*(' + f + ')' if f_p<t_p else '*' + f
                if t.startswith('1*'): t = t[2:]
                t_append((t, t_p))
            elif n==1:
                t, t_p = tt_p = factors_precedence[0]
                t_append(tt_p)
            else:
                t, t_p = '1', num_p
                t_append(('1', num_p))
                
            if is_add:
                if not r:
                    r += '(' + t + ')' if t_p < add_p else t
                elif t.startswith('-'):
                    r += ' - ' + t[1:]
                else:
                    r += ' + (' + t + ')' if t_p < add_p else ' + ' + t
            elif m:
                return t, t_p
        if not r:
            return '0', num_p
        return r, add_p

EXP_COEFF_DICT = ExpCoeffDict()
