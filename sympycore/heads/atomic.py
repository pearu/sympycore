
__all__ = ['SYMBOL', 'NUMBER', 'SPECIAL', 'CALLABLE']

import re

from .base import Head

Expr = None # to be changed to Expr in sympycore/__init__.py

# The following tuples are updated in sympycore/__init__.py:
realtypes = ()
rationaltypes = ()
complextypes = ()

_is_name = re.compile(r'\A[a-zA-z_]\w*\Z').match
_is_number = re.compile(r'\A[-]?\d+\Z').match
_is_atomic = re.compile(r'\A\w+\Z').match
_is_neg_number = re.compile(r'\A-\d+([/]\d+)?\Z').match
_is_rational = re.compile(r'\A\d+[/]\d+\Z').match

class AtomicHead(Head):
    """
    AtomicHead is a base class to atomic expression heads.
    """

    def data_to_str(self, data, parent_precedence):
        if isinstance(data, Expr):
            h, d = data.pair
            return h.data_to_str(d, parent_precedence)
        s = '%s' % (data,)
        if self.get_precedence_for_data(data) < parent_precedence:
            return '(' + s + ')'
        return s

class SpecialHead(AtomicHead):
    """
    SpecialHead is head for special objects like None, NotImplemented,
    Ellipsis, etc.  Data can be any Python object.
    """

    def get_precedence_for_data(self, data,
                                _p = Head.precedence_map['SPECIAL']):
        return _p
    
    def data_to_str(self, data, parent_precedence):
        if data is Ellipsis:
            return '...'
        return AtomicHead.data_to_str(self, data, parent_precedence)

    def __repr__(self): return 'SPECIAL'

class SymbolHead(AtomicHead):
    """
    SymbolHead is a head for symbols, data can be any Python object.
    """

    def get_precedence_for_data(self, data,
                                _p = Head.precedence_map['SYMBOL']):
        if isinstance(data, Expr):
            h, d = data.pair
            return h.get_precedence_for_data(d)
        return _p
    
    def __repr__(self): return 'SYMBOL'

class NumberHead(AtomicHead):
    """
    NumberHead is a head for symbols, data can be any Python object.
    """

    def get_precedence_for_data(self, data,
                                _p = Head.precedence_map['NUMBER'],
                                _neg_p = Head.precedence_map['NEG'],
                                _add_p = Head.precedence_map['ADD'],
                                _div_p = Head.precedence_map['DIV'],
                                ):
        if isinstance(data, complextypes):
            # todo: check for pure imaginary numbers
            return _add_p
        elif isinstance(data, rationaltypes):
            if data < 0:
                return _neg_p
            return _div_p
        elif isinstance(data, realtypes):
            if data < 0:
                return _neg_p
            return _p
        elif isinstance(data, Expr):
            h, d = data.pair
            return h.get_precedence_for_data(d)
        return _p
    
    def __repr__(self): return 'NUMBER'

class CallableHead(AtomicHead):
    """
    CallableHead is a head for interpreting callable objects,
    data can be any callable Python object.
    """
    precedence = Head.precedence_map['SYMBOL']

    def data_to_str(self, func, parent_precedence):
        if hasattr(func, '__name__'):
            return func.__name__
        return AtomicHead.data_to_str(self, func, parent_precedence)

    def __repr__(self): return 'CALLABLE'


SYMBOL = SymbolHead()
NUMBER = NumberHead()
SPECIAL = SpecialHead()
CALLABLE = CallableHead()
