
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

    def as_term_coeff_dict(self, cls, expr):
        return cls(TERM_COEFF_DICT, {expr: 1})

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
        vcls = cls.get_value_algebra()
        dcls = cls.get_differential_algebra()
        d = dcls(FDIFF, vcls(NUMBER, argument_index))**order
        return cls(APPLY, (d, (expr,)))

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
