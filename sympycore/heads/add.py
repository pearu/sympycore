
__all__ = ['ADD']

from .base import heads_precedence, ArithmeticHead

def init_module(m):
    from .base import heads
    for n,h in heads.iterNameValue(): setattr(m, n, h)

class AddHead(ArithmeticHead):

    """
    AddHead represents addition n-ary operation where operands is
    given as a n-sequence of expressions. For example, expression 'a +
    2*b' is 'Expr(ADD, (a, 2*b))' where ADD=AddHead()
    """

    op_mth = '__add__'
    op_rmth = '__radd__'
    
    def __repr__(self): return 'ADD'

    def data_to_str_and_precedence(self, cls, operands):
        m = len(operands)
        if m==0:
            return '0', heads_precedence.NUMBER
        if m==1:
            op = operands[0]
            return op.head.data_to_str_and_precedence(cls, op.data)
        add_p = heads_precedence.ADD
        r = ''
        for op in operands:
            t,t_p = op.head.data_to_str_and_precedence(cls, op.data)
            if not r:
                r += '(' + t + ')' if t_p < add_p else t
            elif t.startswith('-'):
                r += ' - ' + t[1:]
            else:
                r += ' + (' + t + ')' if t_p < add_p else ' + ' + t
        return r, add_p

    def to_lowlevel(self, data, pair):
        m = len(data)
        if m==0:
            return 0
        if m==1:
            return data[0]
        return pair

    def term_coeff(self, cls, expr):
        term_list = expr.data
        if not term_list:
            return cls(NUMBER, 0), 1
        if len(term_list)==1:
            expr = term_list[0]
            return expr.head.term_coeff(cls, expr)
        return expr, 1

    def neg(self, cls, expr):
        terms = []
        for term in expr.data:
            terms.append(-term)
        return cls(ADD, terms)

    def add(self, cls, lhs, rhs):
        term_list = lhs.data
        head, data = rhs.pair
        if head is not ADD:
            head, data = head.as_add(cls, rhs).pair
        if head is ADD:
            l = []
            d = {}
            for t in lhs.data + data:
                term, coeff = t.head.term_coeff(cls, t)
                c = d.get(term)
                if c is None:
                    d[term] = coeff
                    l.append(term)
                else:
                    c = c + coeff
                    if not c:
                        del d[term]
                    else:
                        d[term] = c
            r = []
            one = cls(NUMBER, 1)
            for term in l:
                c = d.get(term)
                if c is not None:
                    if c==1:
                        r.append(term)
                    else:
                        if term==one:
                            r.append(cls(NUMBER, c))
                        else:
                            r.append(cls(TERM_COEFF_DICT, {term:c}))
            if not r:
                return cls(0)
            if len(r)==1:
                return r[0]
            return cls(ADD, r)
        raise NotImplementedError(`self, lhs, rhs`)

    def pow(self, cls, base, exp):
        if exp==0:
            return cls(NUMBER, 1)
        if exp==1:
            return base
        return cls(POW, (base, exp))

ADD = AddHead()
