
__all__ = ['EQ', 'NE', 'LT', 'LE', 'GT', 'GE']

from .base import Head, BinaryHead

class EqHead(BinaryHead):

    op_symbol = '=='
    op_mth = '__eq__'
    precedence = Head.precedence_map['EQ']
    def __repr__(self): return 'EQ'

class NeHead(BinaryHead):

    op_symbol = '!='
    op_mth = '__ne__'
    precedence = Head.precedence_map['NE']
    def __repr__(self): return 'NE'
    
class LtHead(BinaryHead):

    op_symbol = '<'
    op_mth = '__lt__'
    precedence = Head.precedence_map['LT']
    def __repr__(self): return 'LT'

class LeHead(BinaryHead):

    op_symbol = '<='
    op_mth = '__le__'
    precedence = Head.precedence_map['LE']
    def __repr__(self): return 'LE'
    
class GtHead(BinaryHead):

    op_symbol = '>'
    op_mth = '__gt__'
    precedence = Head.precedence_map['GE']
    def __repr__(self): return 'GT'
    
class GeHead(BinaryHead):

    op_symbol = '>='
    op_mth = '__ge__'
    precedence = Head.precedence_map['GE']
    def __repr__(self): return 'GE'

EQ = EqHead()
NE = NeHead()
LT = LtHead()
LE = LeHead()
GT = GtHead()
GE = GeHead()
