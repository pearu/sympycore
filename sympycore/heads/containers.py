
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
        for t in data:
            h, d = t.pair
            try:
                s = h.data_to_str(d, precedence)
            except AttributeError: # a temporary hack
                s = str(d)
            l.append(s)
        if len(l)==1:
            return '(%s,)' % (l[0])
        return '(%s)' % (', '.join(l))        
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
        for t in data:
            h, d = t.pair
            try:
                s = h.data_to_str(d, precedence)
            except AttributeError: # a temporary hack
                s = str(d)
            l.append(s)
        r = '[%s]' % (', '.join(l))
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
        for k, v in data:
            h, d = k.pair
            try:
                sk = h.data_to_str(d, 0.0)
            except AttributeError: # a temporary hack
                sk = str(d)
            h, d = v.pair
            try:
                sv = h.data_to_str(d, 0.0)
            except AttributeError: # a temporary hack
                sv = str(d)
            s = '%s:%s' % (sk, sv)
            l.append(s)
        r = '{%s}' % (', '.join(l))
        if precedence < parent_precedence:
            return '(' + r + ')'
        return r

    def __repr__(self): return 'DICT'

TUPLE = TupleHead()
LIST = ListHead()
DICT = DictHead()
