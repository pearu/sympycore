
__all__ = ['CALLABLE']

import re
import types
from .base import AtomicHead, heads_precedence, Expr

from ..core import init_module

init_module.import_heads()

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

    def add(self, cls, lhs, rhs):
        rhead, rdata = rhs.pair
        if rhead is SYMBOL:
            return cls(TERM_COEFF_DICT, {lhs:1, rhs:1})
        raise NotImplementedError(`self, rhead`)

CALLABLE = CallableHead()
