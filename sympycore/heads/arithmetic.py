
__all__ = ['SUB', 'DIV', 'FLOORDIV', 'MUL', 'MOD', 'POW',
           'TERMS', 'FACTORS']


from .base import Head, UnaryHead, BinaryHead, NaryHead, Expr, heads



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

class TermsHead(Head):
    """
    TermsHead is a head of a sum of term and coefficient pairs, data
    is a dictionary or a frozenset of such pairs, coefficients are
    arbitrary Python objects.
    """

    def get_precedence_for_data(self, data,
                                _p1 = Head.precedence_map['MUL'],
                                _p2 = Head.precedence_map['TERMS']):
        return _p1 if len(data)==1 else _p2

    def data_to_str(self, cls, data, parent_precedence, _mul_p = Head.precedence_map['MUL']):
        l = []
        r = ''
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
                st = h.data_to_str(cls, d, precedence)
                s = st
            else:
                st = h.data_to_str(cls, d, _mul_p)
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
    arbitrary Python objects that are treated as NUMBER expressions.
    """

    def get_precedence_for_data(self, data,
                                _p1 = Head.precedence_map['POW'],
                                _p2 = Head.precedence_map['FACTORS']):
        return _p1 if len(data)==1 else _p2
            
    def data_to_str(self, cls, data, parent_precedence,
                    _pow_p = Head.precedence_map['POWPOW']):
        l = []
        l_append = l.append
        r = ''
        precedence = self.get_precedence_for_data(data)
        NUMBER_data_to_str = heads.NUMBER.data_to_str
        for b, e in data.iteritems():
            if isinstance(e, Expr):
                h, d = e.pair
                se = h.data_to_str(cls, d, precedence)
            else:
                se = NUMBER_data_to_str(cls, e, precedence)
            h, d = b.pair
            s = h.data_to_str(cls, d, _pow_p)
            if se!='1':
                s = s + '**' + se
            l_append(s)
        r = '*'.join(l)
        if precedence < parent_precedence:
            return '(' + r + ')'
        return r        
    def __repr__(self): return 'FACTORS'


TERMS = TermsHead()
FACTORS = FactorsHead()
SUB = SubHead()
MUL = MulHead()
MOD = ModHead()
DIV = DivHead()
FLOORDIV = FloordivHead()

