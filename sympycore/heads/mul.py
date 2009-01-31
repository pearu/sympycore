
__all__ = ['MUL']

from .base import Head, heads_precedence, Pair, Expr, ArithmeticHead

def init_module(m):
    from ..arithmetic import numbers as n
    m.numbertypes = n.numbertypes
    m.inttypes = n.inttypes
    from .base import heads
    for n,h in heads.iterNameValue(): setattr(m, n, h)

class MulHead(ArithmeticHead, Head):
    """
    Algebra(MUL, <list of factors>)

    The list of factors is should not contain numeric expressions
    representing a coefficient, numeric part should be represented
    via TERM_COEFF expression:
    
      Algebra(TERM_COEFF, (Algebra(MUL, <list of factors>), <numeric part>))

    """
    op_mth = '__mul__'
    op_rmth = '__rmul__'
    def __repr__(self): return 'MUL'

    def base_exp(self, cls, expr):
        return expr, 1

    def data_to_str_and_precedence(self, cls, operands):
        m = len(operands)
        if m==0:
            return '1', heads_precedence.NUMBER
        if m==1:
            op = operands[0]
            return op.head.data_to_str_and_precedence(cls, op.data)
        mul_p = heads_precedence.MUL
        r = ''
        for op in operands:
            f, f_p = op.head.data_to_str_and_precedence(cls, op.data)
            if not r or r=='-':
                r += '('+f+')' if f_p<mul_p else f
            elif f.startswith('1/'):
                r += f[1:]
            else:
                r += '*('+f+')' if f_p<mul_p else '*'+f
        return r, mul_p

    def pair_to_lowlevel(self, pair):
        head, data = pair
        m = len(data)
        if m==0: return 1
        if m==1:
            h, d = p = data[0].pair
            return h.pair_to_lowlevel(p)
        return pair

    def term_coeff(self, cls, expr):
        return expr, 1

    def as_mul(self, cls, expr):
        return expr

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
            if b2.head is MUL:
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
                    if b1.head is MUL:
                        c, l = b1.data
                        if l == lst[-i:] and c==1:
                            # x*(a*b)**2*a*b -> x*(a*b)**3
                            r = b1 ** (e1 + 1)
                            del lst[-i-1:]
                            break
                    if lst[-i:]==lst[-2*i:-i]:
                        # x*a*b * a*b -> x*(a*b)**2
                        r = cls(MUL, lst[-i:])**2
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
        return cls(TERM_COEFF, (cls(MUL, lst), compart))

    def non_commutative_mul(self, cls, lhs, rhs):
        head, data = rhs.pair
        if head is NUMBER:
            if data==1:
                return lhs
            if data==0:
                return rhs
            return cls(TERM_COEFF, (lhs, rhs))
        if head is not MUL:
            head, data = head.as_mul(cls, rhs).pair
        if head is MUL:
            return self.combine(cls, factors_list1 + factors_list2)
        raise NotImplementedError(`self, lhs, rhs`)

    def pow(self, cls, base, exp):
        if exp==0:
            return cls(NUMBER, 1)
        if exp==1:
            return base
        if exp==-1:
            factors_list = [factor**-1 for factor in factors_list]
            factors_list.reverse()
            return cls(MUL, factors_list)
        term, coeff = self.term_coeff(cls, base)
        if coeff!=1:
            return NUMBER.pow(cls, coeff, exp) * term**exp
        if isinstance(exp, Expr):
            h, d = exp.pair
            if h is NUMBER and isinstance(d, inttypes) and d>0:
                factors_list = base.data
                first = factors_list[0]
                last = factors_list[-1]
                a = last * first
                if a is not None and a.head is NUMBER: # todo: or a is commutative
                    compart = NUMBER.pow(cls, a, d)
                    rest = factors_list[1:-1]
                    if not rest:
                        return compart
                    if len(rest)==1:
                        middle = rest[0]
                    else:
                        middle = cls(MUL, rest)
                    return compart * first * middle**d * last # could be optimized
        return cls(POW, (base, exp))

MUL = MulHead()
