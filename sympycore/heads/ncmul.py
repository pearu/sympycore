
__all__ = ['NCMUL']

from .base import Head, heads, heads_precedence, Pair

class NCMulHead(Head):
    """
    Algebra(NCMUL, Pair(<commutative_part>, <list of non-commutative factors>))
    """
    def __repr__(self): return 'NCMUL'
    def data_to_str_and_precedence(self, cls, (commutative_part, factor_list)):
        m = len(factor_list)
        ncmul_p = heads_precedence.NCMUL
        num_p = heads_precedence.NUMBER
        if commutative_part==1:
            r = ''
            is_mul = m>1
        else:
            f, f_p = heads.NUMBER.data_to_str_and_precedence(cls, commutative_part)
            r = '('+f+')' if f_p < ncmul_p else f
            is_mul = True
        for factor in factor_list:
            h, d = factor.pair
            f, f_p = h.data_to_str_and_precedence(cls, d)
            if is_mul:
                if not r:
                    r += '('+f+')' if f_p<ncmul_p else f
                else:
                    r += '*('+f+')' if f_p<ncmul_p else '*'+f
            else:
                return f, f_p
        return r, ncmul_p

    def as_ncmul(self, cls, expr):
        return expr

    def ncmul(self, cls, lhs, rhs):
        head, data = rhs.pair
        if head is not NCMUL:
            head, data = head.as_ncmul(cls, rhs).pair
        if head is NCMUL:
            compart1, factors_list1 = lhs.data
            compart2, factors_list2 = data
            compart = compart1 * compart2
            factors = []
            for factor in factors_list1 + factors_list2:
                if not factors:
                    factors.append(factor)
                    last_base, last_exp = factor.head.base_exp(cls, factor)
                    continue
                base, exp = factor.head.base_exp(cls, factor)
                if base==last_base:
                    exp = last_exp + exp
                    if not exp:
                        del factors[-1]
                        if factors:
                            last_factor = factors[-1]
                            last_base, last_exp = last_factor.head.base_exp(cls, last_factor)
                        continue
                    if exp==1:
                        factors[-1] = base
                    else:
                        factors[-1] = base ** exp # todo: check commutativity
                else:
                    factors.append(factor)
                last_base, last_exp = base, exp
            if not factors:
                return cls(compart)
            return cls(NCMUL, Pair(compart, factors))
        raise NotImplementedError(`self, lhs, rhs`)

NCMUL = NCMulHead()
