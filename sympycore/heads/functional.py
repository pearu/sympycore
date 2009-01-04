
__all__ = ['APPLY', 'SUBSCRIPT', 'SLICE', 'LAMBDA', 'ATTR', 'KWARG']

from .base import Head, heads

class ApplyHead(Head):
    """
    ApplyHead is a head for n-ary apply operation,
    data is a (1+n)-tuple of expression operands
    """
    precedence = Head.precedence_map['APPLY']
    op_mth = '__call__'

    def data_to_str(self, cls, data, parent_precedence):
        precedence = self.precedence
        func = data[0]
        args = data[1:]
        h, d = func.pair
        r = h.data_to_str(cls, d, precedence)
        l = []
        for a in args:
            h, d = a.pair
            s = h.data_to_str(cls, d, 0.0)
            l.append(s)
        r += '(%s)' % (', '.join(l))
        if precedence < parent_precedence:
            return '(' + r + ')'
        return r

    def __repr__(self): return 'APPLY'

class SubscriptHead(Head):
    """
    SubscriptHead is a head for n-ary subscript operation,
    data is a (1+n)-tuple of expression operands
    """
    precedence = Head.precedence_map['SUBSCRIPT']
    op_mth = '__getitem__'

    def data_to_str(self, cls, data, parent_precedence):
        precedence = self.precedence
        func = data[0]
        args = data[1:]

        h, d = func.pair
        r = h.data_to_str(cls, d, precedence)
        l = []
        for a in args:
            h, d = a.pair
            s = h.data_to_str(cls, d, 0.0)
            l.append(s)
        r += '[%s]' % (', '.join(l))
        if precedence < parent_precedence:
            return '(' + r + ')'
        return r

    def __repr__(self): return 'SUBSCRIPT'

class SliceHead(Head):
    """
    SliceHead is a head for 3-ary slice operation,
    data is a 3-tuple of expression operands
    """
    precedence = Head.precedence_map['SLICE']

    def data_to_str(self, cls, data, parent_precedence):
        precedence = self.precedence
        start, stop, step = data
        h, d = start.pair
        if h is heads.SPECIAL and d is None: start = None
        h, d = stop.pair
        if h is heads.SPECIAL and d is None: stop = None
        h, d = step.pair
        if h is heads.SPECIAL and d is None: step = None
        if start is None:
            if stop is None:
                if step is None: r = ':'
                else: r = '::%s' % step
            else:
                if step is None: r = ':%s' % stop
                else: r = ':%s:%s' % (stop, step)
        else:
            if stop is None:
                if step is None: r = '%s:' % start
                else: r = '%s::%s' % (start, step)
            else:
                if step is None: r ='%s:%s' % (start, stop)
                else: r = '%s:%s:%s' % (start, stop, step)
        if precedence < parent_precedence:
            return '(' + r + ')'
        return r

    def __repr__(self): return 'SLICE'

class LambdaHead(Head):
    """
    LambdaHead is a head for lambda expression,
    data is a 2-tuple of arguments and an expression.
    """
    precedence = Head.precedence_map['LAMBDA']
    def data_to_str(self, cls, (args, expr), parent_precedence):
        precedence = self.precedence
        l = []
        h, args = args.pair
        for a in args:
            h, d = a.pair
            s = h.data_to_str(cls, d, precedence)
            l.append(s)
        h, d = expr.pair
        s = h.data_to_str(cls, d, precedence)
        r = 'lambda %s: %s' % (', '.join(l), s)
        if precedence < parent_precedence:
            return '(' + r + ')'
        return r
        
    def __repr__(self): return 'LAMBDA'

class AttrHead(Head):
    """
    AttrHead is a head for attribute operation,
    data is a 2-tuple of expression operands.
    """
    precedence = Head.precedence_map['ATTR']
    def data_to_str(self, cls, (expr, attr), parent_precedence):
        precedence = self.precedence
        h, d = expr.pair
        s1 = h.data_to_str(cls, d, precedence)
        h, d = attr.pair
        s2 = h.data_to_str(cls, d, 0.0)
        r = s1 + '.' + s2
        if precedence < parent_precedence:
            return '(' + r + ')'
        return r
        
    def __repr__(self): return 'ATTR'

class KwargHead(Head):
    """
    Kwarg is a head for keyword argument,
    data is a 2-tuple of expression operands.
    """
    precedence = Head.precedence_map['KWARG']
    def data_to_str(self, cls, (name, expr), parent_precedence):
        precedence = self.precedence
        h, d = name.pair
        s1 = h.data_to_str(cls, d, precedence)
        h, d = expr.pair
        s2 = h.data_to_str(cls, d, precedence)
        r = s1 + '=' + s2
        if precedence < parent_precedence:
            return '(' + r + ')'
        return r
        
    def __repr__(self): return 'KWARG'

APPLY = ApplyHead()
SUBSCRIPT = SubscriptHead()
SLICE = SliceHead()
LAMBDA = LambdaHead()
ATTR = AttrHead()
KWARG = KwargHead()
