
__all__ = ['POS', 'NEG', 'ADD', 'SUB', 'DIV', 'FLOORDIV', 'MUL', 'MOD', 'POW',
           'TERMS', 'FACTORS']

from .base import Head, UnaryHead, BinaryHead, NaryHead
from .atomic import NUMBER
Expr = None

class PosHead(UnaryHead):

    """
    PosHead represents positive unary operation where operand (data)
    is an expression.
    """
    precedence = Head.precedence_map['POS']
    op_mth = '__pos__'
    op_symbol = '+'
    def __repr__(self): return 'POS'


class NegHead(UnaryHead):

    """
    NegHead represents negation unary operation where operand is an
    expression.
    """
    precedence = Head.precedence_map['NEG']
    op_mth = '__neg__'
    op_symbol = '-'
    def __repr__(self): return 'NEG'

class AddHead(NaryHead):

    """
    AddHead represents addition n-ary operation where operands is
    given as a n-tuple of expressions. For example, expression 'a +
    2*b' is 'Expr(ADD, (a, 2*b))' where ADD=AddHead()
    """
    precedence = Head.precedence_map['ADD']
    op_mth = '__add__'
    op_rmth = '__radd__'
    
    def data_to_str(self, data, parent_precedence):
        precedence = self.precedence
        r = ''
        for t in data:
            h, d = t.pair
            s = h.data_to_str(d, precedence)
            if h is NEG or h is POS:
                r += s
            else:
                if r:
                    r += ' + ' + s
                else:
                    r += s
        if precedence < parent_precedence:
            return '(' + r + ')'
        return r

    def __repr__(self): return 'ADD'

class SubHead(NaryHead):

    """
    SubHead represents subtraction n-ary operation where operands is
    given as a n-tuple of expressions.
    """
    precedence = Head.precedence_map['SUB']
    op_mth = '__sub__'
    op_rmth = '__rsub__'
    op_symbol = ' - '
    def __repr__(self): return 'SUB'

class MulHead(NaryHead):

    """
    MulHead represents multiplication n-ary operation,
    data is a n-tuple of expression operands.
    """
    precedence = Head.precedence_map['MUL']
    op_mth = '__mul__'
    op_rmth = '__rmul__'
    op_symbol = '*'
    def __repr__(self): return 'MUL'

class ModHead(NaryHead):

    """
    ModHead represents module n-ary operation,
    data is a n-tuple of expression operands.
    """
    precedence = Head.precedence_map['MOD']
    op_mth = '__mod__'
    op_rmth = '__rmod__'
    op_symbol = '%'
    def __repr__(self): return 'MOD'

class DivHead(NaryHead):

    """
    DivHead represents division n-ary operation,
    data is a n-tuple of expression operands.
    """
    precedence = Head.precedence_map['DIV']
    op_mth = '__div__'
    op_rmth = '__rdiv__'
    op_symbol = '/'    
    def __repr__(self): return 'DIV'

class FloordivHead(NaryHead):
    """
    FloordivHead represents floor-division n-ary operation,
    data is a n-tuple of expression operands.
    """
    precedence = Head.precedence_map['FLOORDIV']
    op_mth = '__floordiv__'
    op_rmth = '__rfloordiv__'
    op_symbol = '//'    
    def __repr__(self): return 'FLOORDIV'

class PowHead(BinaryHead):
    """ PowHead represents exponentiation operation, data is a 2-tuple
    of base and exponent expressions.
    """
    precedence = Head.precedence_map['POW']
    op_mth = '__pow__'
    op_rmth = '__rpow__'
    op_symbol = '**'
    def __repr__(self): return 'POW'

class TermsHead(Head):
    """
    TermsHead is a head of a sum of term and coefficient pairs, data
    is a dictionary or a frozenset of such pairs, coefficients are
    arbitrary Python objects.
    """
    precedence = Head.precedence_map['TERMS']
    def get_precedence_for_data(self, data):
        if len(data)==1:
            return Head.precedence_map['MUL']
        else:
            return Head.precedence_map['TERMS']

    def data_to_str(self, data, parent_precedence):
        l = []
        r = ''
        mul_precedence = Head.precedence_map['MUL']
        precedence = self.get_precedence_for_data(data)
        for t, c in data.iteritems():
            h, d = t.pair
            sc = str(c)
            if sc.startswith('-'):
                sign = ' - '
                sc = sc[1:]
            else:
                sign = ' + '
            if sc=='1':
                st = h.data_to_str(d, precedence)
                s = st
            else:
                st = h.data_to_str(d, mul_precedence)
                if st=='1':
                    s = sc
                else:
                    s = sc + '*' + st
            if r:
                r += sign + s
            else:
                if sign==' - ':
                    r += '-' + s
                else:
                    r += s
        if precedence < parent_precedence:
            return '(' + r + ')'
        return r
    
    def __repr__(self): return 'TERMS'

class FactorsHead(Head):
    """
    FactorsHead is a head of a product of factor and exponent pairs,
    data is a dictionary or a frozenset of such pairs, exponents are
    arbitrary Python objects.
    """
    precedence = Head.precedence_map['FACTORS']
    def data_to_str(self, data, parent_precedence):
        l = []
        r = ''
        if len(data)==1:
            pow_precedence = Head.precedence_map['POWPOW']
            precedence = Head.precedence_map['POW']
        else:
            precedence = pow_precedence = self.precedence
        NUMBER_data_to_str = NUMBER.data_to_str
        for b, e in data.iteritems():
            if isinstance(e, Expr):
                h, d = e.pair
                se = h.data_to_str(d, precedence)
            else:
                se = NUMBER_data_to_str(e, precedence)
            h, d = b.pair
            if se=='1':
                s = sb = h.data_to_str(d, precedence)
            else:
                sb = h.data_to_str(d, pow_precedence)
                if sb=='1':
                    s = sb
                else:
                    s = sb + '**' + se
            if r:
                r += '*' + s
            else:
                r += s
        if precedence < parent_precedence:
            return '(' + r + ')'
        return r        
    def __repr__(self): return 'FACTORS'

POS = PosHead()
NEG = NegHead()
ADD = AddHead()
TERMS = TermsHead()
FACTORS = FactorsHead()
SUB = SubHead()
MUL = MulHead()
MOD = ModHead()
DIV = DivHead()
FLOORDIV = FloordivHead()
POW = PowHead()

