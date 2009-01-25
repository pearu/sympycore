
__all__ = ['NCMUL']

from .base import Head, heads_precedence, Pair, Expr, ArithmeticHead

def init_module(m):
    from ..arithmetic import numbers as n
    m.numbertypes = n.numbertypes
    m.inttypes = n.inttypes
    from .base import heads
    for n,h in heads.iterNameValue(): setattr(m, n, h)

class NCMulHead(ArithmeticHead, Head):
    """
    Algebra(NCMUL, Pair(<commutative_part>, <list of non-commutative factors>))

    <commutative part> is a number is instance or an instance of
    commutative algebra class. For a normalized NCMUL expression, the list
    of non-commutative factors has length equal to 2 or larger.
    Algebra(NCMUL, Pair(c,[f])) should be normalized to Algebra(TERM_COEFF_DICT, {f:c})
    """

    def __repr__(self): return 'NCMUL'

    def base_exp(self, cls, expr):
        return expr, 1
    
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
                if not r or r=='-':
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
        if isinstance(compart, Expr):
            term, coeff = compart.head.term_coeff(cls, compart)
        else:
            term, coeff = NUMBER.term_coeff(cls, compart)
        if coeff==1:
            return expr, 1
        if term==1 and len(ncmul_list)==1:
            return ncmul_list[0], coeff
        return cls(NCMUL, Pair(term, ncmul_list)), coeff

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

    def try_combine_ncmul(self, cls, lhs, rhs):
        
        return None

    def combine(self, cls, factors_list):
        """ Combine factors in a list and return result.
        """
        lst = []
        compart = 1
        for factor in factors_list:
            if not lst:
                lst.append(factor)
                continue
            r = None
            b2, e2 = factor.head.base_exp(cls, factor)
            if b2.head is NCMUL:
                c, l = b2.data
                if len(l)<=len(lst) and lst[-len(l):]==l and c==1:
                    # x*a*b*(a*b)**2 -> x*(a*b)**3
                    r = b2 ** (e2 + 1)
                    del lst[-len(l):]
            if r is None:
                b1, e1 = lst[-1].head.base_exp(cls, lst[-1])
                if b1==b2:
                    # x*a**3*a**2 -> x*a**5
                    r = b2 ** (e1 + e2)
                    del lst[-1]
            if r is None:
                lst.append(factor)
                for i in range(2,len(lst)):
                    b1, e1 = lst[-i-1].head.base_exp(cls, lst[-i-1]);
                    if b1.head is NCMUL:
                        c, l = b1.data
                        if l == lst[-i:] and c==1:
                            # x*(a*b)**2*a*b -> x*(a*b)**3
                            r = b1 ** (e1 + 1)
                            del lst[-i-1:]
                            break
                    if lst[-i:]==lst[-2*i:-i]:
                        # x*a*b * a*b -> x*(a*b)**2
                        r = cls(NCMUL, Pair(1, lst[-i:]))**2
                        del lst[-2*i:]
                        break
            if r is not None:
                if r.head is NUMBER:
                    compart = compart * r
                else:
                    lst.append(r)            
        if not lst:
            return compart
        if len(lst)==1 and compart==1:
            return lst[0]
        return cls(NCMUL, Pair(compart, lst))


    def ncmul(self, cls, lhs, rhs):
        head, data = rhs.pair
        if head is NUMBER:
            compart, factor_list = lhs.data
            compart = compart * data
            return cls(NCMUL, Pair(compart, factor_list))
        if head is not NCMUL:
            head, data = head.as_ncmul(cls, rhs).pair
        if head is NCMUL:
            compart1, factors_list1 = lhs.data
            compart2, factors_list2 = data
            compart = compart1 * compart2
            return self.combine(cls, factors_list1 + factors_list2) * compart
        raise NotImplementedError(`self, lhs, rhs`)

    def pow(self, cls, base, exp):
        if exp==0:
            return cls(NUMBER, 1)
        if exp==1:
            return base
        if exp==-1:
            compart, factors_list = base.data
            compart = NUMBER.pow(cls, compart, -1)
            factors_list = [factor**-1 for factor in factors_list]
            factors_list.reverse()
            if compart==1 and len(factors_list)==1:
                return factors_list[0]
            return cls(NCMUL, Pair(compart, factors_list))
        term, coeff = self.term_coeff(cls, base)
        if coeff!=1:
            return NUMBER.pow(cls, coeff, exp) * term**exp
        if isinstance(exp, Expr):
            h, d = exp.pair
            if h is NUMBER and isinstance(d, inttypes) and d>0:
                compart, factors_list = base.data
                compart = NUMBER.pow(cls, compart, d)
                first = factors_list[0]
                last = factors_list[-1]
                a = last * first
                if a is not None and a.head is NUMBER: # todo: or a is commutative
                    compart = compart * NUMBER.pow(cls, a, d)
                    rest = factors_list[1:-1]
                    if not rest:
                        return compart
                    if len(rest)==1:
                        middle = rest[0]
                    else:
                        middle = cls(NCMUL, Pair(1, rest))
                    return compart * first * middle**d * last # could be optimized
                if compart != 1:
                    if len(factors_list)==1:
                        new_base = factors_list[0]
                    else:
                        new_base = cls(NCMUL, Pair(1, factors_list))
                    return cls(TERM_COEFF_DICT, {cls(POW, (new_base, exp)):compart})
        return cls(POW, (base, exp))

    def expand(self, cls, expr):
        compart, ncmul_list = expr.data
        if isinstance(compart, Expr):
            compart = compart.expand()
        ncmul_list = [f.expand() for f in ncmul_list]
        return cls(NCMUL, Pair(compart, ncmul_list))

NCMUL = NCMulHead()
