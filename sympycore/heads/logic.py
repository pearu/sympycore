
__all__ = ['AND', 'OR', 'NOT', 'IN', 'NOTIN', 'IS', 'ISNOT']

from .base import Head, UnaryHead, BinaryHead, NaryHead

class NotHead(UnaryHead):
    """
    NotHead represents unary boolean NOT operation,
    data is an expression operand.
    """
    op_symbol = 'not '
    def __repr__(self): return 'NOT'

class AndHead(NaryHead):
    """
    AndHead represents n-ary boolean AND operation,
    data is a n-tuple of expression operands.
    """
    op_symbol = ' and '
    def __repr__(self): return 'AND'

class OrHead(NaryHead):
    """
    AndHead represents n-ary boolean OR operation,
    data is a n-tuple of expression operands.
    """
    op_symbol = ' or '
    def __repr__(self): return 'OR'

class IsHead(BinaryHead):
    """
    IsHead represents binary boolean IS operation,
    data is an expression operand.
    """
    op_symbol = ' is '
    def __repr__(self): return 'IS'

class IsnotHead(BinaryHead):
    """
    IsHead represents binary boolean IS NOT operation,
    data is an expression operand.
    """
    op_symbol = ' is not '
    def __repr__(self): return 'ISNOT'

class InHead(BinaryHead):
    """
    InHead represents binary boolean IN operation,
    data is an expression operand.
    """
    op_symbol = ' in '
    def __repr__(self): return 'IN'

class NotinHead(BinaryHead):
    """
    NotinHead represents binary boolean NOT IN operation,
    data is an expression operand.
    """
    op_symbol = ' not in '
    def __repr__(self): return 'NOTIN'

NOT = NotHead()
OR = OrHead()
AND = AndHead()
IS = IsHead()
ISNOT = IsnotHead()
IN = InHead()
NOTIN = NotinHead()
