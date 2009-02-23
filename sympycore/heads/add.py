
__all__ = ['ADD']

from .base import heads_precedence, ArithmeticHead

from ..core import init_module
init_module.import_heads()
init_module.import_lowlevel_operations()

@init_module
def _init(module):
    from ..arithmetic.number_theory import multinomial_coefficients
    module.multinomial_coefficients = multinomial_coefficients

class AddHead(ArithmeticHead):

    """
    AddHead represents addition n-ary operation where operands is
    given as a n-sequence of expressions. For example, expression 'a +
    2*b' is 'Expr(ADD, (a, 2*b))' where ADD=AddHead()
    """

    op_mth = '__add__'
    op_rmth = '__radd__'

    def is_data_ok(self, cls, data):
        if type(data) in [tuple, list]:
            for a in data:
                if not isinstance(a, cls):
                    return '%s data item must be %s instance but got %s' % (self, cls, type(a))
        else:
            return '%s data part must be a list but got %s' % (self, type(data))
    
    def __repr__(self): return 'ADD'

    def new(self, cls, operands, evaluate=True):
        if not evaluate:
            n = len(operands)
            if n==1:
                return operands[0]
            if n==0:
                return cls(NUMBER, 0)
            return cls(self, operands)
        d = {}
        l = []
        operands = list(operands)
        while operands:
            op = operands.pop(0)
            if op==0:
                continue
            head, data = op.pair
            if head is ADD:
                operands.extend(data)
                continue
            elif head is SUB:
                operands.append(data[0])
                for o in data[1:]:
                    operands.append(-o)
                continue
            elif head is TERM_COEFF_DICT:
                for term, coeff in data.iteritems():
                    n = len(d)
                    dict_add_item(cls, d, term, coeff)
                    if n < len(d):
                        l.append(term)
                    elif n > len(d):
                        l.remove(term)
            else:
                term, coeff = op.head.term_coeff(cls, op)
                n = len(d)
                dict_add_item(cls, d, term, coeff)
                if n < len(d):
                    l.append(term)
                elif n > len(d):
                    l.remove(term)
        r = []
        one = cls(NUMBER, 1)
        for term in l:
            r.append(TERM_COEFF.new(cls, (term, d[term])))
        m = len(r)
        if m==0:
            return cls(NUMBER, 0)
        if m==1:
            return r[0]
        return cls(self, r)

    def reevaluate(self, cls, operands):
        r = cls(NUMBER, 0)
        for op in operands:
            r += op
        return r

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

    def term_coeff(self, cls, expr):
        term_list = expr.data
        if not term_list:
            return cls(NUMBER, 0), 1
        if len(term_list)==1:
            expr = term_list[0]
            return expr.head.term_coeff(cls, expr)
        return expr, 1

    def neg(self, cls, expr):
        return cls(ADD, [-term for term in expr.data])

    def add(self, cls, lhs, rhs):
        term_list = lhs.data
        rhead, rdata = rhs.pair
        if rhead is ADD:
            return ADD.new(cls, lhs.data + rdata)
        if rhead is TERM_COEFF_DICT:
            rdata = [t * c for t, c in rdata.items()]
            return ADD.new(cls, lhs.data + rdata)
        if rhead is SUB:
            rdata = rdata[:1] + [-op for op in rdata[1:]]
            return ADD.new(cls, lhs.data + rdata)
        return ADD.new(cls, lhs.data + [rhs])

    inplace_add = add

    def sub(self, cls, lhs, rhs):
        return lhs + (-rhs)

    def commutative_mul(self, cls, lhs, rhs):
        rhead, rdata = rhs.pair
        if rhead is NUMBER:
            return ADD.new(cls, [op*rhs for op in lhs.data])
        if rhead is SYMBOL:
            return cls(BASE_EXP_DICT, {lhs:1, rhs:1})
        if rhead is ADD:
            if lhs==rhs:
                return lhs ** 2
            return cls(BASE_EXP_DICT, {lhs:1, rhs:1})
        if rhead is TERM_COEFF:
            term, coeff = rdata
            return (lhs * term) * coeff
        if rhead is POW:
            base, exp = rhs.data
            if lhs==base:
                return POW.new(cls, (base, exp + 1))
            return cls(BASE_EXP_DICT, {lhs:1, base:exp})
        if rhead is BASE_EXP_DICT:
            data = rdata.copy()
            dict_add_item(cls, data, lhs, 1)
            return BASE_EXP_DICT.new(cls, data)

        raise NotImplementedError(`self, lhs.pair, rhs.pair`)

    def commutative_mul_number(self, cls, lhs, rhs):
        return ADD.new(cls, [op*rhs for op in lhs.data])

    def pow(self, cls, base, exp):
        return POW.new(cls, (base, exp))

    pow_number = pow

    def walk(self, func, cls, data, target):
        l = []
        flag = False
        for op in data:
            o = op.head.walk(func, cls, op.data, op)
            if op is not o:
                flag = True
            l.append(o)
        if flag:
            r = ADD.new(cls, l)
            return func(cls, r.head, r.data, r)
        return func(cls, self, data, target)

    def scan(self, proc, cls, operands, target):
        for operand in operands:
            operand.head.scan(proc, cls, operand.data, target)
        proc(cls, self, operands, target)

    def expand(self, cls, expr):
        l = []
        for op in expr.data:
            h, d = op.pair
            l.append(h.expand(cls, op))
        return self.new(cls, l)

    def expand_intpow(self, cls, expr, intexp):
        if intexp<=1:
            return POW.new(cls, (expr, intexp))
        operands = expr.data
        mdata = multinomial_coefficients(len(operands), intexp)
        s = cls(NUMBER, 0)
        for exps, n in mdata.iteritems():
            m = cls(NUMBER, n)
            for i,e in enumerate(exps):
                m *= operands[i] ** e
            s += m
        return s

ADD = AddHead()
