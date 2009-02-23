
__all__ = ['BASE_EXP_DICT']

from .base import heads, heads_precedence, ArithmeticHead

from ..core import init_module, Expr
init_module.import_heads()
init_module.import_numbers()
init_module.import_lowlevel_operations()

class BaseExpDictHead(ArithmeticHead):
    """ BASE_EXP_DICT expression data is a dictionary of base and
    exponent pairs. All base parts must be Expr instances.

    For example, ``Algebra(BASE_EXP_DICT. {x:2, y:a, 3:1, 2:1/2})``
    represents ``3 * 2**(1/2) * x**2 * y**a``.
    """

    def is_data_ok(self, cls, data):
        if type(data) is dict:
            for item in data.iteritems():
                msg = POW.is_data_ok(cls, item)
                if msg:
                    return 'POW data=%s: %s' % (item, msg)
        else:
            return 'data must be dict instance but got %s' % (type(data))
        return


    def __repr__(self): return 'BASE_EXP_DICT'

    def data_to_str_and_precedence(self, cls, base_exp_dict):
        factors = []
        coeff = None
        for base, exp in base_exp_dict.items():
            if exp==1 and base.head is NUMBER:
                coeff = base.data
            else:
                factors.append(cls(POW, (base, exp)))
        if coeff is not None:
            return TERM_COEFF.data_to_str_and_precedence(cls, (cls(MUL, factors), coeff))
        return MUL.data_to_str_and_precedence(cls, factors)

    def reevaluate(self, cls, data):
        r = cls(NUMBER, 1)
        for base, exp in data.iteritems():
            r *= base ** exp
        return r

    def term_coeff(self, cls, expr):
        coeff = base_exp_dict_get_coefficient(cls, expr.data)
        if coeff is not None:
            d = expr.data.copy()
            del d[coeff]
            r = BASE_EXP_DICT.new(cls, d)
            t, c = r.head.term_coeff(cls, r)
            return t, c * coeff 
        return expr, 1

    def new(self, cls, base_exp_dict, evaluate=True):
        m = len(base_exp_dict)
        if m==0:
            return cls(NUMBER, 1)
        if m==1:
            base, exp = dict_get_item(base_exp_dict)
            return POW.new(cls, (base, exp), evaluate=False)
        coeff = base_exp_dict_get_coefficient(cls, base_exp_dict)
        if coeff is not None:
            del base_exp_dict[coeff]
            if m==2:
                base, exp = dict_get_item(base_exp_dict)
                return TERM_COEFF.new(cls, (POW.new(cls, (base, exp)), coeff.data))
            return TERM_COEFF.new(cls, (cls(BASE_EXP_DICT, base_exp_dict), coeff.data))
        return cls(BASE_EXP_DICT, base_exp_dict)

    def neg(self, cls, expr):
        data = expr.data.copy()
        base_exp_dict_add_item(cls, data, cls(NUMBER,-1), 1)
        return BASE_EXP_DICT.new(cls, data)

    def add(self, cls, lhs, rhs):
        rhead, rdata = rhs.pair
        if rhead is BASE_EXP_DICT:
            lterm, lcoeff = self.term_coeff(cls, lhs)
            rterm, rcoeff = self.term_coeff(cls, rhs)
            if lterm==rterm:
                return TERM_COEFF.new(cls, (lterm, lcoeff + rcoeff))
            return cls(TERM_COEFF_DICT, {lterm:lcoeff, rterm:rcoeff})
        if rhead is ADD:
            return ADD.new(cls, [lhs]+rdata)
        if rhead is NUMBER:
            if rdata==0:
                return lhs
            lterm, lcoeff = self.term_coeff(cls, lhs)
            return cls(TERM_COEFF_DICT, {lterm:lcoeff, cls(NUMBER, 1):rdata})
        if rhead is APPLY or rhead is SYMBOL or rhead is POW:
            lterm, lcoeff = self.term_coeff(cls, lhs)
            return cls(TERM_COEFF_DICT, {lterm:lcoeff, rhs:1})
        if rhead is TERM_COEFF:
            rterm, rcoeff = rdata
            lterm, lcoeff = self.term_coeff(cls, lhs)
            if lterm==rterm:
                return TERM_COEFF.new(cls, (lterm, lcoeff + rcoeff))
            return cls(TERM_COEFF_DICT, {lterm:lcoeff, rterm:rcoeff})
        if rhead is TERM_COEFF_DICT:
            lterm, lcoeff = self.term_coeff(cls, lhs)
            data = rdata.copy()
            base_exp_dict_add_item(cls, data, lterm, lcoeff)
            return TERM_COEFF_DICT.new(cls, data)
        raise NotImplementedError(`self, cls, lhs.pair, rhs.pair`)

    inplace_add = add
    
    def commutative_imul(self, cls, data, rhs):
        rhead, rdata = rhs.pair
        if rhead is SYMBOL or rhead is ADD or rhead is APPLY:
            base_exp_dict_add_item(cls, data, rhs, 1)
        elif rhead is NUMBER:
            base_exp_dict_mul_item(cls, data, rhs, 1)
        elif rhead is TERM_COEFF:
            term, coeff = rdata
            base_exp_dict_add_item(cls, data, term, 1)
            base_exp_dict_mul_item(cls, data, cls(NUMBER, coeff), 1)
        elif rhead is BASE_EXP_DICT:
            base_exp_dict_add_dict(cls, data, rdata)
        elif rhead is POW:
            base, exp = rdata
            base_exp_dict_add_item(cls, data, base, exp)
        elif rhead is TERM_COEFF_DICT:
            base_exp_dict_add_item(cls, data, rhs, 1)
        else:
            raise NotImplementedError(`self, cls, rhs.pair`)
    
    def commutative_mul(self, cls, lhs, rhs):
        data = lhs.data.copy()
        self.commutative_imul(cls, data, rhs)
        return BASE_EXP_DICT.new(cls, data)

    def commutative_mul_number(self, cls, lhs, rhs):
        #TODO: optimize
        return self.commutative_mul(cls, lhs, cls(NUMBER, rhs))

    def scan(self, proc, cls, data, target):
        for b, e in data.iteritems():
            b.head.scan(proc, cls, b.data, target)
            if isinstance(e, Expr):
                e.head.scan(proc, cls, e.data, target)
            else:
                NUMBER.scan(proc, cls, e, target)
        proc(cls, self, data, target)

    def walk(self, func, cls, data, target):
        d = {}
        flag = False
        for b, e in data.iteritems():
            b1 = b.head.walk(func, cls, b.data, b)
            if isinstance(e, Expr):
                e1 = e.head.walk(func, cls, e.data, e)
            else:
                e1 = NUMBER.walk(func, cls, e, e)
            if b1 is not b or e1 is not e:
                flag = True
            self.commutative_imul(cls, d, b1**e1)
        if flag:
            r = BASE_EXP_DICT.new(cls, d)
            return func(cls, r.head, r.data, r)
        return func(cls, self, data, target)

    def pow(self, cls, base, exp):
        if type(exp) is cls:
            h, d = exp.pair
            if h is NUMBER and isinstance(d, numbertypes):
                exp = d
        if isinstance(exp, inttypes):
            if exp:
                data = base.data.copy()
                base_exp_dict_mul_value(cls, data, exp)
                return BASE_EXP_DICT.new(cls, data)
            return cls(NUMBER, 1)
        return POW.new(cls, (base, exp))

    pow_number = pow

    def expand(self, cls, expr):
        data = {}
        for b, e in expr.data.items():
            f = POW.new(cls, (b, e)).expand()
            h, d = f.pair
            data1 = {}
            if h is TERM_COEFF_DICT:
                data2 = d
            else:
                t, c = f.term_coeff()
                data2 = {t: c}
            if data:
                term_coeff_dict_mul_dict(cls, data1, data, data2)
                data = data1
            else:
                data = data2
        return TERM_COEFF_DICT.new(cls, data)

BASE_EXP_DICT = BaseExpDictHead()
