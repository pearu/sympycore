
__all__ = ['CALLABLE']

from .base import AtomicHead, heads_precedence, Expr
import re

def init_module(m):
    from .base import heads
    for n,h in heads.iterNameValue(): setattr(m, n, h)

_is_atomic = re.compile(r'\A\w+\Z').match

class CallableHead(AtomicHead):
    """
    CallableHead is a head for interpreting callable objects,
    data can be any callable Python object.
    """
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

CALLABLE = CallableHead()
