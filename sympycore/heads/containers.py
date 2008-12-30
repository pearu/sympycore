
__all__ = ['TUPLE', 'LIST', 'DICT']

from .base import Head

class TupleHead(Head):
    """
    TupleHead represents n-tuple,
    data is n-tuple of expressions.
    """
    precedence = Head.precedence_map['TUPLE']
    def data_to_str(self, data, parent_precedence):
        precedence = self.precedence
        l = []
        l_append = l.append
        for t in data:
            h, d = t.pair
            s = h.data_to_str(d, precedence)
            l_append(s)
        if len(l)==1:
            return '('+ l[0] +',)'
        return '(' + (', '.join(l)) + ')'
    
    def __repr__(self): return 'TUPLE'

class ListHead(Head):
    """
    ListHead represents n-list,
    data is n-tuple of expressions.
    """
    precedence = Head.precedence_map['LIST']
    def data_to_str(self, data, parent_precedence):
        precedence = self.precedence
        l = []
        l_append = l.append
        for t in data:
            h, d = t.pair
            s = h.data_to_str(d, precedence)
            l_append(s)
        r = '[' + (', '.join(l)) + ']'
        if precedence < parent_precedence:
            return '(' + r + ')'
        return r

    def __repr__(self): return 'LIST'

class DictHead(Head):
    """
    DictHead represents n-dict,
    data is n-tuple of expression pairs.
    """
    precedence = Head.precedence_map['DICT']
    def data_to_str(self, data, parent_precedence):
        precedence = self.precedence
        l = []
        l_append = l.append
        for k, v in data:
            h, d = k.pair
            s1 = h.data_to_str(d, precedence)
            h, d = v.pair
            s2 = h.data_to_str(d, precedence)
            l_append(s1 + ':' + s2)
        r = '{'  + (', '.join(l)) + '}'
        if precedence < parent_precedence:
            return '(' + r + ')'
        return r

    def __repr__(self): return 'DICT'

TUPLE = TupleHead()
LIST = ListHead()
DICT = DictHead()
