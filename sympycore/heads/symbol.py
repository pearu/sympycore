
__all__ = ['SYMBOL']

import re

from ..core import init_module
init_module.import_heads()
init_module.import_numbers()
init_module.import_lowlevel_operations()

from .base import AtomicHead, heads_precedence, Expr, Pair, ArithmeticHead

_is_atomic = re.compile(r'\A\w+\Z').match

class SymbolHead(AtomicHead):
    """
    SymbolHead is a head for symbols, data can be any Python object.
    """

    def new(self, cls, data, evaluate=True):
        return cls(self, data)

    def reevaluate(self, cls, data):
        return cls(self, data)

    def is_data_ok(self, cls, data):
        return

    def __repr__(self): return 'SYMBOL'

    def data_to_str_and_precedence(self, cls, data):
        if isinstance(data, Expr):
            h, d = data.pair
            return h.data_to_str_and_precedence(cls, d)
        s = str(data)
        if _is_atomic(s):
            return s, heads_precedence.SYMBOL
        return s, 0.0 # force parenthesis

    def to_EXP_COEFF_DICT(self, cls, data, expr, variables = None):
        variables = EXP_COEFF_DICT.combine_variables(data, variables)
        exp = EXP_COEFF_DICT.make_exponent(data, variables)
        assert len(exp)==len(variables), `exp, variables, i, data`
        return cls(EXP_COEFF_DICT, Pair(variables, {exp:1}))

    def non_commutative_mul(self, cls, lhs, rhs):
        head, data = rhs.pair
        if head is NUMBER:
            return term_coeff_new(cls, (lhs, data))
        if head is SYMBOL:
            if lhs.data == data:
                return cls(POW, (lhs, 2))
            return cls(MUL, [lhs, rhs])
        if head is TERM_COEFF:
            term, coeff = data
            return (lhs * term) * coeff
        if head is POW:
            return MUL.combine(cls, [lhs, rhs])
        if head is MUL:
            return MUL.combine(cls, [lhs] + data)
        raise NotImplementedError(`self, cls, lhs.pair, rhs.pair`)

    def commutative_mul(self, cls, lhs, rhs):
        rhead, rdata = rhs.pair
        if rhead is NUMBER:
            return term_coeff_new(cls, (lhs, rdata))
        if rhead is SYMBOL:
            if lhs.data==rdata:
                return cls(POW, (lhs, 2))
            return cls(BASE_EXP_DICT, {lhs:1, rhs:1})
        if rhead is TERM_COEFF:
            term, coeff = rdata
            return (lhs * term) * coeff
        if rhead is POW:
            rbase, rexp = rdata
            if rbase==lhs:
                return pow_new(cls, (lhs, rexp+1))
            return cls(BASE_EXP_DICT, {lhs:1, rbase:rexp})
        if rhead is BASE_EXP_DICT:
            data = rdata.copy()
            dict_add_item(cls, data, lhs, 1)
            return base_exp_dict_new(cls, data)
        if rhead is APPLY or rhead is ADD or rhead is TERM_COEFF_DICT:
            return cls(BASE_EXP_DICT, {lhs:1, rhs:1})
        raise NotImplementedError(`self, cls, lhs.pair, rhs.pair`)

    inplace_commutative_mul = commutative_mul

    def commutative_mul_number(self, cls, lhs, rhs):
        if rhs==1:
            return lhs
        if rhs==0:
            return cls(NUMBER, 0)
        return cls(TERM_COEFF, (lhs, rhs))

    def commutative_div_number(self, cls, lhs, rhs):
        return term_coeff_new(cls, (lhs, number_div(cls, 1, rhs)))

    def commutative_rdiv_number(self, cls, lhs, rhs):
        return term_coeff_new(cls, (cls(POW, (lhs, -1)), rhs))

    def commutative_div(self, cls, lhs, rhs):
        rhead, rdata = rhs.pair
        if rhead is NUMBER:
            return self.commutative_div_number(cls, lhs, rdata)
        if rhead is SYMBOL:
            if lhs.data==rdata:
                return cls(NUMBER, 1)
            return cls(BASE_EXP_DICT, {lhs:1, rhs:-1})
        if rhead is TERM_COEFF_DICT:
            return cls(BASE_EXP_DICT, {lhs:1, rhs:-1})
        if rhead is TERM_COEFF:
            term, coeff = rdata
            return (lhs / term) * number_div(cls, 1, coeff)
        if rhead is POW:
            rbase, rexp = rdata
            if lhs==rbase:
                return pow_new(cls, (lhs, 1-rexp))
            return cls(BASE_EXP_DICT, {lhs:1, rbase:-rexp, })
        if rhead is BASE_EXP_DICT:
            data = {lhs:1}
            base_exp_dict_sub_dict(cls, data, rdata)
            return base_exp_dict_new(cls, data)
        return ArithmeticHead.commutative_div(self, cls, lhs, rhs)

    def non_commutative_mul_number(self, cls, lhs, rhs):
        return term_coeff_new(cls, (lhs, rhs))

    non_commutative_rmul_number = commutative_mul_number
    
    def term_coeff(self, cls, expr):
        return expr, 1

    def neg(self, cls, expr):
        return cls(TERM_COEFF, (expr, -1))

    def as_add(self, cls, expr):
        return cls(ADD, [expr])
    
    def add(self, cls, lhs, rhs):
        h,d = rhs.pair
        if h is SYMBOL:
            if lhs==rhs:
                return cls(TERM_COEFF, (lhs, 2))
        elif h is NUMBER:
            if d==0:
                return lhs
            return cls(TERM_COEFF_DICT, {lhs:1, cls(NUMBER,1):d})
        elif h is ADD:
            return ADD.new(cls, [lhs]+d)
        elif h is TERM_COEFF:
            t,c = d
            if lhs==t:
                return term_coeff_new(cls, (t, c+1))
            return cls(TERM_COEFF_DICT, {t:c, lhs:1})
        elif h is TERM_COEFF_DICT:
            data = d.copy()
            dict_add_item(cls, data, lhs, 1)
            return term_coeff_dict_new(cls, data)
        return cls(TERM_COEFF_DICT, {lhs:1, rhs:1})

    inplace_add = add

    def add_number(self, cls, lhs, rhs):
        return cls(TERM_COEFF_DICT, {lhs:1, cls(NUMBER,1):rhs}) if rhs else lhs

    def sub_number(self, cls, lhs, rhs):
        return cls(TERM_COEFF_DICT, {lhs:1, cls(NUMBER,1):-rhs}) if rhs else lhs

    def sub(self, cls, lhs, rhs):
        return lhs + (-rhs)

    def as_term_coeff_dict(self, cls, expr):
        return cls(TERM_COEFF_DICT, {expr: 1})

    def base_exp(self, cls, expr):
        return expr, 1

    def pow(self, cls, base, exp):
        if type(exp) is cls and exp.head is NUMBER:
            exp = exp.data
        return pow_new(cls, (base, exp))

    def pow_number(self, cls, base, exp):
        if exp==1: return base
        if exp==0: return cls(NUMBER, 1)
        return cls(POW, (base, exp))

    def expand(self, cls, expr):
        return expr

    def expand_intpow(self, cls, expr, intexp):
        if intexp==0:
            return cls(NUMBER, 1)
        return cls(POW, (expr, intexp))

    def diff(self, cls, data, expr, symbol, order, cache={}):
        if order==0:
            return expr
        if data == symbol:
            assert order>0,`order`
            return cls(NUMBER, int(order==1))
        return cls(NUMBER, 0)

    def fdiff(self, cls, data, expr, argument_index, order):
        fcls = cls.get_function_algebra()
        dcls = fcls.get_differential_algebra()
        d = dcls(FDIFF, cls(NUMBER, argument_index))**order
        return fcls(APPLY, (d, (expr,)))

    def apply(self, cls, data, func, args):
        return cls(APPLY, (func, args))

    def integrate_indefinite(self, cls, data, expr, x):
        if data==x:
            return cls(TERM_COEFF, (cls(POW, (expr, 2)), mpq((1,2))))
        return cls(BASE_EXP_DICT, {expr:1, cls(SYMBOL, x):1})

    def integrate_definite(self, cls, data, expr, x, a, b):
        if data==x:
            return (b**2-a**2)/2
        return expr*(b-a)

SYMBOL = SymbolHead()
