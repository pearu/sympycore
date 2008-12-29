
__all__ = ['SYMBOL', 'NUMBER', 'SPECIAL']

import re

from .base import Head

_is_name = re.compile(r'\A[a-zA-z_]\w*\Z').match
_is_number = re.compile(r'\A[-]?\d+\Z').match
_is_atomic = re.compile(r'\A\w+\Z').match
_is_neg_number = re.compile(r'\A-\d+([/]\d+)?\Z').match
_is_rational = re.compile(r'\A\d+[/]\d+\Z').match

class SpecialHead(Head):
    """
    SpecialHead is head for special objects like None, NotImplemented,
    Ellipsis, etc.  Data can be any Python object.
    """
    precedence = Head.precedence_map['SPECIAL']

    def data_to_str(self, data, parent_precedence):
        if data is Ellipsis:
            return '...'
        s = '%s' % (data,)
        return s

    def __repr__(self): return 'SPECIAL'

class SymbolHead(Head):
    """
    SymbolHead is a head for symbols, data can be any Python object.
    """
    precedence = Head.precedence_map['SYMBOL']
    
    def data_to_str(self, data, parent_precedence):
        if hasattr(data, '__name__'):
            s = data.__name__
        else:
            s = '%s' % (data,)
        if _is_atomic(s):
            return s
        return '(S(' + s + '))'

    def __repr__(self): return 'SYMBOL'

class NumberHead(Head):
    """
    NumberHead is a head for symbols, data can be any Python object.
    """
    precedence = Head.precedence_map['NUMBER']
    
    def data_to_str(self, data, parent_precedence):
        s = '%s' % (data,)
        if _is_atomic(s):
            return s
        if _is_neg_number(s):
            precedence = Head.precedence_map['NEG']
        elif _is_rational(s):
            precedence = Head.precedence_map['DIV']
        else:
            precedence = self.precedence
        if precedence < parent_precedence:
            return '(' + s + ')'
        return s

    def __repr__(self): return 'NUMBER'

SYMBOL = SymbolHead()
NUMBER = NumberHead()
SPECIAL = SpecialHead()
