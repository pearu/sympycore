
__all__ = ['NCMUL']

from .base import Head, heads_precedence, Pair, Expr

def init_module(m):
    from ..arithmetic import numbers as n
    m.numbertypes = n.numbertypes
    m.inttypes = n.inttypes
    from .base import heads
    for n,h in heads.iterNameValue(): setattr(m, n, h)

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
        elif commutative_part==-1:
            r = '-'
            is_mul = m>1
        else:
            f, f_p = NUMBER.data_to_str_and_precedence(cls, commutative_part)
            r = '('+f+')' if f_p < ncmul_p else f
            is_mul = True
        for factor in factor_list:
            h, d = factor.pair
            f, f_p = h.data_to_str_and_precedence(cls, d)
            if is_mul:
                if not r:
                    r += '('+f+')' if f_p<ncmul_p else f
                elif f.startswith('1/'):
                    r += f[1:]
                else:
                    r += '*('+f+')' if f_p<ncmul_p else '*'+f
            else:
                return f, f_p
        return r, ncmul_p

    def term_coeff(self, cls, expr):
        compart, ncmul_list = expr.data
        term, coeff = compart.head.term_coeff(cls, compart)
        if coeff==1:
            return expr, 1
        return cls(NCMUL, Pair(coeff, ncmul_list)), coeff

    def as_ncmul(self, cls, expr):
        return expr

    def as_term_coeff_dict(self, cls, expr):
        compart, ncmul_list = expr.data
        if isinstance(compart, Expr):
            term, coeff = compart.head.term_coeff(cls, compart)
        else:
            term, coeff = NUMBER.term_coeff(cls, compart)
        if coeff==1:
            return cls(TERM_COEFF_DICT, {expr:1})
        if term==1 and len(ncmul_list)==1:
            return cls(TERM_COEFF_DICT, {ncmul_list[0]: coeff})
        return cls(TERM_COEFF_DICT, {cls(NCMUL, Pair(term, ncmul_list)):coeff})

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

    def pow(self, cls, base, exp):
        if exp==0:
            return cls(NUMBER, 1)
        if exp==1:
            return base
        if isinstance(exp, Expr):
            h, d = exp.pair
            if h is NUMBER and isinstance(d, inttypes):
                compart, factors_list = base.data
                compart = NUMBER.pow(cls, compart, d)
                factors_list = [factor**d for factor in factors_list]
                if exp<0:
                    factors_list.reverse()
                return cls(NCMUL, Pair(compart, factors_list)) * cls(NCMUL, Pair(1,[])) # to force normalization
        return cls(POW, (base, exp))

    def expand(self, cls, expr):
        compart, ncmul_list = expr.data
        if isinstance(compart, Expr):
            compart = compart.expand()
        ncmul_list = [f.expand() for f in ncmul_list]
        return cls(NCMUL, Pair(compart, ncmul_list))

NCMUL = NCMulHead()
