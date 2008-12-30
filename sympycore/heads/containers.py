
__all__ = ['TUPLE', 'LIST', 'DICT']

from .base import Head

class TupleHead(Head):
    """
    TupleHead represents n-tuple,
    data is n-tuple of expressions.
    """

    def get_precedence_for_data(self, data,
                                _p = Head.precedence_map['TUPLE']):
        return _p
    
    def data_to_str(self, data, parent_precedence,
                    _p = Head.precedence_map['TUPLE']):
        l = []
        l_append = l.append
        for t in data:
            h, d = t.pair
            s = h.data_to_str(d, _p)
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

    def get_precedence_for_data(self, data,
                                _p = Head.precedence_map['LIST']):
        return _p

    def data_to_str(self, data, parent_precedence,
                    _p = Head.precedence_map['LIST']):
        l = []
        l_append = l.append
        for t in data:
            h, d = t.pair
            s = h.data_to_str(d, _p)
            l_append(s)
        r = '[' + (', '.join(l)) + ']'
        if _p < parent_precedence:
            return '(' + r + ')'
        return r

    def __repr__(self): return 'LIST'

class DictHead(Head):
    """
    DictHead represents n-dict,
    data is n-tuple of expression pairs.
    """

    def get_precedence_for_data(self, data,
                                _p = Head.precedence_map['DICT']):
        return _p

    def data_to_str(self, data, parent_precedence,
                    _p = Head.precedence_map['DICT']
                    ):
        l = []
        l_append = l.append
        for k, v in data:
            h, d = k.pair
            s1 = h.data_to_str(d, _p)
            h, d = v.pair
            s2 = h.data_to_str(d, _p)
            l_append(s1 + ':' + s2)
        r = '{'  + (', '.join(l)) + '}'
        if _p < parent_precedence:
            return '(' + r + ')'
        return r

    def __repr__(self): return 'DICT'

TUPLE = TupleHead()
LIST = ListHead()
DICT = DictHead()
