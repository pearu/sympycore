
__all__ = ['MUL']

from .base import Head, heads_precedence, Pair, Expr, ArithmeticHead

from ..core import init_module
init_module.import_heads()
init_module.import_numbers()
init_module.import_lowlevel_operations()

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

    def is_data_ok(self, cls, data):
        if type(data) in [tuple, list]:
            for a in data:
                if not isinstance(a, cls):
                    return '%s data item must be %s instance but got %s' % (self, cls, type(a))
        else:
            return '%s data part must be a list but got %s' % (self, type(data))

    def __repr__(self): return 'MUL'

    def new(self, cls, operands, evaluate=True):
        operands = [op for op in operands if op!=1]
        n = len(operands)
        if n==0:
            return cls(NUMBER, 1)
        if n==1:
            return operands[0]
        return cls(MUL, operands)

    def reevaluate(self, cls, operands):
        r = cls(NUMBER, 1)
        for op in operands:
            r *= op
        return r

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
            if f=='1': continue
            if not r or r=='-':
                r += '('+f+')' if f_p<mul_p else f
            elif f.startswith('1/'):
                r += f[1:]
            else:
                r += '*('+f+')' if f_p<mul_p else '*'+f
        if not r:
            return '1', heads_precedence.NUMBER
        return r, mul_p

    def term_coeff(self, cls, expr):
        return expr, 1

    def combine(self, cls, factors_list):
        """ Combine factors in a list and return result.
        """
        lst = []
        compart = 1
        for factor in factors_list:
            if factor.head is NUMBER:
                compart = compart * factor.data
                continue
            r = None
            b2, e2 = factor.head.base_exp(cls, factor)
            if lst and b2.head is MUL:
                l = b2.data
                if len(l)<=len(lst) and lst[-len(l):]==l:
                    # x*a*b*(a*b)**2 -> x*(a*b)**3
                    r = b2 ** (e2 + 1)
                    del lst[-len(l):]
            if lst and r is None:
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
        if compart==1:
            if len(lst)==1:
                return lst[0]
            return cls(MUL, lst)
        return cls(TERM_COEFF, (cls(MUL, lst), compart))

    def non_commutative_mul(self, cls, lhs, rhs):
        head, data = rhs.pair
        if head is NUMBER:
            if data==1:
                return lhs
            return TERM_COEFF.new(cls, (lhs, data))
        if head is SYMBOL or head is POW:
            return self.combine(cls, lhs.data + [rhs])
        if head is TERM_COEFF:
            term, coeff = data
            return (lhs * term) * coeff
        if head is MUL:
            return self.combine(cls, lhs.data + rhs.data)
        raise NotImplementedError(`self, cls, lhs.pair, rhs.pair`)

    def non_commutative_mul_number(self, cls, lhs, rhs):
        return term_coeff_new(cls, (lhs, rhs))

    non_commutative_rmul_number = non_commutative_mul_number

    def pow(self, cls, base, exp):
        if exp==0:
            return cls(NUMBER, 1)
        if exp==1:
            return base
        if exp==-1:
            factors_list = [factor**-1 for factor in base.data]
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
                    compart = NUMBER.pow_number(cls, a, d)
                    rest = factors_list[1:-1]
                    if not rest:
                        return compart
                    if len(rest)==1:
                        middle = rest[0]
                    else:
                        middle = cls(MUL, rest)
                    return compart * first * middle**d * last # could be optimized
            if h is NUMBER:
                exp = d
        return cls(POW, (base, exp))

    def pow_number(self, cls, base, exp):
        return self.pow(cls, base, cls(NUMBER, exp))

    def walk(self, func, cls, data, target):
        l = []
        flag = False
        for op in data:
            o = op.head.walk(func, cls, op.data, op)
            if op is not o:
                flag = True
            l.append(o)
        if flag:
            r = MUL.new(cls, l)
            return func(cls, r.head, r.data, r)
        return func(cls, self, data, target)

    def scan(self, proc, cls, operands, target):
        for operand in operands:
            operand.head.scan(proc, cls, operand.data, target)
        proc(cls, self, operands, target)

MUL = MulHead()
