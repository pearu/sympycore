
__all__ = ['EQ', 'NE', 'LT', 'LE', 'GT', 'GE']

from .base import Head, BinaryHead, heads_precedence

class EqHead(BinaryHead):

    op_symbol = '=='
    op_mth = '__eq__'
    def __repr__(self): return 'EQ'

class NeHead(BinaryHead):

    op_symbol = '!='
    op_mth = '__ne__'
    def __repr__(self): return 'NE'
    
class LtHead(BinaryHead):

    op_symbol = '<'
    op_mth = '__lt__'
    def __repr__(self): return 'LT'

class LeHead(BinaryHead):

    op_symbol = '<='
    op_mth = '__le__'
    def __repr__(self): return 'LE'
    
class GtHead(BinaryHead):

    op_symbol = '>'
    op_mth = '__gt__'
    def __repr__(self): return 'GT'
    
class GeHead(BinaryHead):

    op_symbol = '>='
    op_mth = '__ge__'
    def __repr__(self): return 'GE'

EQ = EqHead()
NE = NeHead()
LT = LtHead()
LE = LeHead()
GT = GtHead()
GE = GeHead()
