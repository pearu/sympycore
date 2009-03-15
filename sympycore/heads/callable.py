
__all__ = ['CALLABLE']

import re
import types
from .base import AtomicHead, heads_precedence, Expr

from ..core import init_module, classes

init_module.import_heads()
init_module.import_numbers()
init_module.import_lowlevel_operations()


_is_atomic = re.compile(r'\A\w+\Z').match

class CallableHead(AtomicHead):
    """
    CallableHead is a head for interpreting callable objects,
    data can be any callable Python object.
    """

    def is_data_ok(self, cls, data):
        if not callable(data):
            if isinstance(data, type):
                return
            return 'data instance must be callable but got %s' % (`data.pair`)
        if isinstance(data, Expr):
            if data.head==CALLABLE:
                return 'data should not have CALLABLE head'
        if not issubclass(cls, classes.FunctionRing) and cls is not classes.Verbatim:
            return 'Algebra class should be subclass of FunctionRing but got %s' % (cls.__name__)
        
    def __repr__(self): return 'CALLABLE'

    def data_to_str_and_precedence(self, cls, func):
        if isinstance(func, Expr):
            h, d = func.pair
            return h.data_to_str_and_precedence(cls, d)
        if hasattr(func, '__name__'):
            s = func.__name__
        else:
            s = str(func)
        if _is_atomic(s):
            return s, heads_precedence.CALLABLE
        return s, 0.0 # force parenthesis

    def neg(self, cls, expr):
        return cls(TERM_COEFF,(expr, -1))

    def add(self, cls, lhs, rhs):
        rhead, rdata = rhs.pair
        if rhead is SYMBOL:
            return cls(TERM_COEFF_DICT, {lhs:1, rhs:1})
        raise NotImplementedError(`self, rhead`)

    def pow_number(self, cls, base, exp):
        return pow_new(cls, (base, exp))

    def non_commutative_mul_number(self, cls, lhs, rhs):
        return term_coeff_new(cls, (lhs, rhs))

    def apply(self, cls, data, func, args):
        return data(*args)

    def fdiff(self, cls, data, expr, argument_index, order):
        if hasattr(data, 'fdiff'):# and isinstance(order, inttypes):
            return data.fdiff(cls, argument_index, order)
        fcls = cls.get_function_algebra()
        dcls = fcls.get_differential_algebra()
        d = dcls(FDIFF, cls(NUMBER, argument_index))**order
        return fcls(APPLY, (d, (expr,)))

CALLABLE = CallableHead()
