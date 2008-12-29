
__all__ = ['APPLY', 'SUBSCRIPT', 'SLICE', 'LAMBDA', 'ATTR', 'KWARG', 'CallableHead']
functional
from .base import Head
from .atomic import SPECIAL

Expr = None

class ApplyHead(Head):
    """
    ApplyHead is a head for n-ary apply operation,
    data is a (1+n)-tuple of expression operands
    """
    precedence = Head.precedence_map['APPLY']
    op_mth = '__call__'

    def data_to_str(self, data, parent_precedence):
        precedence = self.precedence
        func = data[0]
        args = data[1:]

        h, d = func.pair
        try:
            r = h.data_to_str(d, precedence)
        except AttributeError: # a temporary hack
            r = str(d)
        l = []
        for a in args:
            h, d = a.pair
            try:
                s = h.data_to_str(d, 0.0)
            except AttributeError: # a temporary hack
                s = str(d)
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

    def data_to_str(self, data, parent_precedence):
        precedence = self.precedence
        func = data[0]
        args = data[1:]

        h, d = func.pair
        try:
            r = h.data_to_str(d, precedence)
        except AttributeError: # a temporary hack
            r = str(d)
        l = []
        for a in args:
            h, d = a.pair
            try:
                s = h.data_to_str(d, 0.0)
            except AttributeError: # a temporary hack
                s = str(d)
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

    def data_to_str(self, data, parent_precedence):
        precedence = self.precedence
        start, stop, step = data
        h, d = start.pair
        if h is SPECIAL and d is None: start = None
        h, d = stop.pair
        if h is SPECIAL and d is None: stop = None
        h, d = step.pair
        if h is SPECIAL and d is None: step = None
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
    def data_to_str(self, (args, expr), parent_precedence):
        precedence = self.precedence
        l = []
        h, args = args.pair
        for a in args:
            h, d = a.pair
            try:
                s = h.data_to_str(d, 0.0)
            except AttributeError: # a temporary hack
                s = str(d)
            l.append(s)
        h, d = expr.pair
        try:
            s = h.data_to_str(d, 0.0)
        except AttributeError: # a temporary hack
            s = str(d)
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
    def data_to_str(self, (expr, attr), parent_precedence):
        precedence = self.precedence
        h, d = expr.pair
        try:
            se = h.data_to_str(d, precedence)
        except AttributeError: # a temporary hack
            se = str(d)
        h, d = attr.pair
        try:
            sa = h.data_to_str(d, 0.0)
        except AttributeError: # a temporary hack
            sa = str(d)
        r = '%s.%s' % (se, sa)
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
    def data_to_str(self, (name, expr), parent_precedence):
        precedence = self.precedence
        h, d = name.pair
        try:
            s1 = h.data_to_str(d, precedence)
        except AttributeError: # a temporary hack
            s1 = str(d)
        h, d = expr.pair
        try:
            s2 = h.data_to_str(d, precedence)
        except AttributeError: # a temporary hack
            s2 = str(d)
        r = '%s=%s' % (s1, s2)
        if precedence < parent_precedence:
            return '(' + r + ')'
        return r
        
    def __repr__(self): return 'KWARG'

class CallableHead(Head):
    is_singleton = False
    precedence = Head.precedence_map['APPLY']

    def __hash__(self):
        return hash(self.func)
    def __eq__(self, other):
        if type(self) is type(other):
            return self.func == other.func
        return False

    def init(self, func):
        self.func = func
        if hasattr(func, '__name__'):
            self.__name__ = func.__name__
        else:
            self.__name__ = str(func)

    def data_to_str(self, args, parent_precedence):
        precedence = self.precedence
        func = self.func
        if isinstance(func, Expr):
            h, d = func.pair
            r = h.data_to_str(d, precedence)
        else:
            r = str(self)
        l = []
        for a in args:
            h, d = a.pair
            try:
                s = h.data_to_str(d, 0.0)
            except AttributeError: # a temporary hack
                s = str(d)
            l.append(s)
        r += '(%s)' % (', '.join(l))
        if precedence < parent_precedence:
            return '(' + r + ')'
        return r

    def __str__(self):
        func = self.func
        if callable(func):
            return self.__name__
        return str(func)

    def __repr__(self):
        return 'CallableHead(%s)' % (repr(self.func))

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)

APPLY = ApplyHead()
SUBSCRIPT = SubscriptHead()
SLICE = SliceHead()
LAMBDA = LambdaHead()
ATTR = AttrHead()
KWARG = KwargHead()
