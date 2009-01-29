
__all__ = ['APPLY', 'SUBSCRIPT', 'SLICE', 'LAMBDA', 'ATTR', 'KWARG']

from .base import Head, heads, heads_precedence

class FunctionalHead(Head):

    def data_to_str_and_precedence(self, cls, (func, args)):
        o_p = getattr(heads_precedence, repr(self))
        arg_p = heads_precedence.ARG        
        f, f_p = func.head.data_to_str_and_precedence(cls, func.data)
        if f_p < o_p: f = '('+f+')'
        l = []
        assert type(args) in [tuple], `args`
        for arg in args:
            a, a_p = arg.head.data_to_str_and_precedence(cls, arg.data)
            if a_p < arg_p: a = '('+a+')'
            l.append(a)
        p1,p2 = self.parenthesis
        return f + p1 + ', '.join(l) + p2, o_p

class ApplyHead(Head):
    """
    ApplyHead is a head for n-ary apply operation,
    data is a (1+n)-tuple of expression operands
    """
    precedence = Head.precedence_map['APPLY']
    op_mth = '__call__'

    def data_to_str_and_precedence(self, cls, (func, args)):
        f, f_p = func.head.data_to_str_and_precedence(cls, func.data)
        l = []
        for arg in args:
            h, d = arg.pair
            a, a_p = h.data_to_str_and_precedence(cls, d)
            l.append(a)
        apply_p = heads_precedence.APPLY
        if f_p < apply_p:
            return '('+f+')('+', '.join(l)+')', apply_p
        return f+'('+', '.join(l)+')', apply_p
        
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

class SubscriptHead(FunctionalHead):
    """
    SubscriptHead is a head for n-ary subscript operation,
    data is a (1+n)-tuple of expression operands
    """
    precedence = Head.precedence_map['SUBSCRIPT']
    op_mth = '__getitem__'
    parenthesis = '[]'

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

    def data_to_str_and_precedence(self, cls, (start, stop, step)):
        slice_p = heads_precedence.SLICE
        colon_p = heads_precedence.COLON
        h, d = start.pair
        if h is heads.SPECIAL and d is None:
            start = None
        else:
            start, p = h.data_to_str_and_precedence(cls, d)
            if p < colon_p: start = '('+start+')'
        h, d = stop.pair
        if h is heads.SPECIAL and d is None:
            stop = None
        else:
            stop, p = h.data_to_str_and_precedence(cls, d)
            if p < colon_p: stop = '('+stop+')'
        h, d = step.pair
        if h is heads.SPECIAL and d is None:
            step = None
        else:
            step, p = h.data_to_str_and_precedence(cls, d)
            if p < colon_p: step = '('+step+')'
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
        return r, slice_p

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
    def data_to_str_and_precedence(self, cls, (args, expr)):
        arg_p = heads_precedence.ARG
        colon_p = heads_precedence.COLON
        l = []
        assert type(args) in [tuple],`args`
        for arg in args:
            a, a_p = arg.head.data_to_str_and_precedence(cls, arg.data)
            if a_p < arg_p: a = '('+a+')'
            l.append(a)
        e, e_p = expr.head.data_to_str_and_precedence(cls, expr.data)
        if e_p < colon_p: e = '('+e+')'
        return 'lambda %s: %s' % (', '.join(l), e), heads_precedence.LAMBDA

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

    def data_to_str_and_precedence(self, cls, (expr, attr)):
        dot_p = heads_precedence.DOT
        e, e_p = expr.head.data_to_str_and_precedence(cls, expr.data)
        if e_p < dot_p: e = '('+e+')'
        a, a_p = attr.head.data_to_str_and_precedence(cls, attr.data)
        if a_p < dot_p: a = '('+a+')'
        return e + '.' + a, heads_precedence.ATTR
            
    def __repr__(self): return 'ATTR'

class KwargHead(Head):
    """
    Kwarg is a head for keyword argument,
    data is a 2-tuple of expression operands.
    """
    def data_to_str_and_precedence(self, cls, (name, expr)):
        kw_p = heads_precedence.KWARG
        assign_p = heads_precedence.ASSIGN
        n, n_p = name.head.data_to_str_and_precedence(cls, name.data)
        if n_p < assign_p: n = '('+n+')'
        e, e_p = expr.head.data_to_str_and_precedence(cls, expr.data)
        if e_p < assign_p: e = '('+e+')'
        return n + '=' + e, kw_p

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
