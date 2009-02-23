
__all__ = ['TERM_COEFF']



from .base import heads_precedence, ArithmeticHead, Expr

from ..core import init_module

init_module.import_heads()
init_module.import_lowlevel_operations()

@init_module
def _import_numbertypes(m):
    from sympycore.arithmetic import numbers as n
    m.numbertypes = n.numbertypes
    m.inttypes = n.inttypes

class TermCoeff(ArithmeticHead):
    """ Expr(TERM_COEFF, (term, coeff)) represents term*coeff
    where term is symbolic expression and coeff is a number or
    symbolic expression.
    """

    def is_data_ok(self, cls, data):
        if type(data) is tuple and len(data)==2:
            term, coeff = data
            if isinstance(term, cls):
                if isinstance(coeff, numbertypes):
                    return
                elif isinstance(coeff, cls):
                    if coeff.head is NUMBER:
                        if not isinstance(coeff.data, numbertypes):
                            return 'data[1].data must be %s instance for NUMBER head but got %s instance' % (numbertypes, type(coeff.data))
                else:
                    return 'data[1] must be %s instance but got %s instance' % ((cls, numbertypes), type(coeff))
            else:
                return 'data[0] must be %s instance but got %s instance' % (cls, type(term))
        else:
            return 'data must be 2-tuple'
        return

    def __repr__(self): return 'TERM_COEFF'

    def new(self, cls, (term, coeff)):
        if coeff==1:
            return term
        if coeff==0 or term==1:
            return cls(coeff)
        return cls(self, (term, coeff))

    def reevaluate(self, cls, (term, coeff)):
        return term * coeff

    def to_EXP_COEFF_DICT(self, cls, (term, coeff), expr, variables=None):
        return term.head.to_EXP_COEFF_DICT(cls, term.data, term, variables) * coeff

    def data_to_str_and_precedence(self, cls, (term, coeff)):
        neg_p = heads_precedence.NEG
        mul_p = heads_precedence.MUL
        if term==1:
            t, t_p = NUMBER.data_to_str_and_precedence(cls, coeff)
        elif coeff==1:
            t, t_p = term.head.data_to_str_and_precedence(cls, term.data)
        elif coeff==-1:
            t, t_p = term.head.data_to_str_and_precedence(cls, term.data)
            t, t_p = ('-('+t+')' if t_p < mul_p else '-' + t), neg_p
        elif coeff==0:
            t, t_p = '0', heads_precedence.NUMBER
        else:
            t, t_p = term.head.data_to_str_and_precedence(cls, term.data)
            c, c_p = NUMBER.data_to_str_and_precedence(cls, coeff)
            if t=='1':
                return c, c_p
            cs = '('+c+')' if c_p < mul_p else c
            ts = '('+t+')' if t_p < mul_p else t
            t = cs + (ts[1:] if ts.startswith('1/') else '*' + ts)
            t_p = mul_p
        return t, t_p

    def term_coeff(self, cls, expr):
        return expr.data

    def neg(self, cls, expr):
        term, coeff = expr.data
        coeff = -coeff
        return TERM_COEFF.new(cls, (term, coeff))

    def add(self, cls, lhs, rhs):
        term, coeff = lhs.data
        head, data = rhs.pair
        if head is ADD:
            return ADD.new(cls, [lhs] + data)
        if head is TERM_COEFF_DICT:
            data = data.copy()
            dict_add_item(cls, data, term, coeff)
            return TERM_COEFF_DICT.new(cls, data)
        if head is NUMBER:
            if data==0:
                return lhs
            return cls(TERM_COEFF_DICT,{term:coeff, cls(NUMBER,1):data})
        if head is SYMBOL:
            if term==rhs:
                return TERM_COEFF.new(cls, (term, coeff + 1))
            return cls(TERM_COEFF_DICT,{term:coeff, rhs:1})
        if head is TERM_COEFF:
            rterm, rcoeff = data
            if rterm==term:
                return TERM_COEFF.new(cls, (term, coeff + rcoeff))
            return cls(TERM_COEFF_DICT,{term:coeff, rterm:rcoeff})
        if head is BASE_EXP_DICT:
            rcoeff = base_exp_dict_get_coefficient(cls, data)
            if rcoeff is not None:
                d = data.copy()
                del d[rcoeff]
                rterm = BASE_EXP_DICT.new(cls, d)
                if rterm==term:
                    return TERM_COEFF.new(cls, (term, coeff + rcoeff))
                return cls(TERM_COEFF_DICT,{term:coeff, rterm:rcoeff})
            else:
                if term==rhs:
                    return TERM_COEFF.new(cls, (term, coeff + 1))
                return cls(TERM_COEFF_DICT,{term:coeff, rhs:1})
        if head is POW or head is APPLY:
            if term==rhs:
                return TERM_COEFF.new(cls, (term, coeff + 1))
            return cls(TERM_COEFF_DICT,{term:coeff, rhs:1})
        raise NotImplementedError(`self, rhs.head`)

    inplace_add = add

    def sub(self, cls, lhs, rhs):
        return lhs + (-rhs)

    def non_commutative_mul(self, cls, lhs, rhs):
        term, coeff = lhs.data
        head, data = rhs.pair
        if head is NUMBER:
            return TERM_COEFF.new(cls, (term, coeff * data))
        return (term * rhs) * coeff

    commutative_mul = non_commutative_mul

    def commutative_mul_number(self, cls, lhs, rhs):
        if rhs==1:
            return lhs
        if rhs==0:
            return cls(NUMBER, 0)
        term, coeff = lhs.data
        new_coeff = coeff * rhs
        if new_coeff==1:
            return term
        return cls(TERM_COEFF, (term, new_coeff))

    def pow(self, cls, base, exp):
        term, coeff = base.data
        if isinstance(exp, Expr):
            head, data = exp.pair
            if head is NUMBER:
                exp = data
        if isinstance(exp, inttypes):
            if exp<0:
                return term ** exp / coeff ** (-exp)
            return term ** exp * coeff ** exp
        return POW.new(cls, (base, exp))

    def pow_number(self, cls, base, exp):
        term, coeff = base.data
        if isinstance(exp, inttypes):
            if exp<0:
                return term ** exp / coeff ** (-exp)
            return term ** exp * coeff ** exp
        return cls(POW, (base, exp))

    def walk(self, func, cls, data, target):
        term, coeff = data
        h, d = term.pair
        term = h.walk(func, cls, d, term)
        if isinstance(coeff, Expr):
            h, d = coeff.pair
            coeff = h.walk(func, type(coeff), d, coeff)
        s = term * coeff
        h, d = s.pair
        return func(cls, h, d, s)

    def scan(self, proc, cls, data, target):
        term, coeff = data
        term.head.scan(proc, cls, term.data, target)    
        if isinstance(coeff, Expr):
            coeff.head.scan(proc, type(coeff), coeff.data, target)
        proc(cls, self, data, target)

    def expand(self, cls, expr):
        term, coeff  = expr.data
        return term.head.expand(cls, term) * coeff
        

TERM_COEFF = TermCoeff()
