
__all__ = ['Head', 'UnaryHead', 'BinaryHead', 'NaryHead']

class Head(object):

    """
    Head - base class for expression heads.

    Recall that expression is represented as a pair: Expr(head, data).
    The head part defines how the data part should be interpreted.
    Various operations on expressions can be defined as Head methods
    taking the data part as an argument.
    """

    """
    precedence defines the order of operations if they appear in the
    same expression. Operations with higher precedence are applied
    first. Operations with equal precedence are applied from left to
    right.

    For example, multiplication has higher precedence than addition.

    In the following, the precendence value is a floating point number
    in a range [0.0, 1.0]. Lowest precedence value 0.0 is assigned
    for atomic expressions.
    """
    precedence = 1.0
    precedence_map = dict(
        KWARG = 0.0,
        LAMBDA = 0.01,
        OR = 0.02, AND = 0.03, NOT = 0.04,
        LT = 0.1, LE = 0.1, GT = 0.1, GE = 0.1, EQ = 0.09, NE = 0.09,
        IN = 0.1, NOTIN = 0.1, IS = 0.1, ISNOT = 0.1,
        BOR = 0.2, BXOR = 0.21, BAND = 0.22, 
        LSHIFT = 0.3, RSHIFT = 0.3,
        ADD = 0.4, SUB = 0.4, TERMS = 0.45,
        MUL = 0.5, DIV = 0.5, MOD = 0.5, FLOORDIV = 0.5,
        FACTORS = 0.55,
        POS = 0.6, NEG = 0.6, INVERT = 0.6,
        POW = 0.7, POWPOW = 0.71,
        ATTR = 0.81, SUBSCRIPT = 0.82, SLICE = 0.83, APPLY = 0.84, 
        TUPLE = 0.91, LIST = 0.92, DICT = 0.93,
        SYMBOL = 1.0, NUMBER = 1.0, SPECIAL = 1.0
        )

    """
    op_mth and op_rmth contain the names of the corresponding Python
    left and right, respectively, operation methods.
    """
    op_mth = None
    op_rmth = None
    is_singleton = True

    _cache = {}
    
    def __new__(cls, *args):
        if len(args)==1:
            arg = args[0]
            key = '%s(%s:%s)' % (cls.__name__, arg, id(arg))
        else:
            key = '%s%r' % (cls.__name__, args)
        obj = cls._cache.get(key)
        if obj is None:
            obj = object.__new__(cls)
            if cls.is_singleton:
                cls._cache[key] = obj
            obj._key = key
            obj.init(*args)
        return obj

    def init(self, *args):
        # derived class may set attributes here
        pass #pragma NO COVER

    def as_unique_head(self):
        # used by the pickler support to make HEAD instances unique
        return self._cache.get(self._key, self)

    def data_to_str(self, data, parent_precedence):
        """ Convert expression data to Python string expression.
        """
        precedence = self.precedence
        if precedence < parent_precedence:
            return '(%s)' % data
        return '%s' % data

    def get_precedence_for_data(self, data):
        """
        Return the precedence order corresponding to given data.
        """
        return self.precedence

class UnaryHead(Head):
    """
    UnaryHead is base class for unary operation heads,
    data is an expression operand.
    """

    def data_to_str(self, data, parent_precedence):
        precedence = self.precedence
        h, d = data.pair
        try:
            r = self.op_symbol + h.data_to_str(d, precedence)
        except AttributeError: # a temporary hack
            r = self.op_symbol + str(data)
        if precedence < parent_precedence:
            return '(' + r + ')'
        return r

class BinaryHead(Head):
    """
    BinaryHead is base class for binary operation heads,
    data is a 2-tuple of expression operands.
    """
    def data_to_str(self, data, parent_precedence):
        precedence = self.precedence
        lhs, rhs = data
        h,d = lhs.pair
        try:
            sl = h.data_to_str(d, precedence)
        except AttributeError: # a temporary hack
            sl = str(d)
        h,d = rhs.pair
        try:
            sr = h.data_to_str(d, precedence)
        except AttributeError: # a temporary hack
            sr = str(d)
        r = '%s%s%s' % (sl, self.op_symbol, sr)
        if precedence < parent_precedence:
            return '(' + r + ')'
        return r

class NaryHead(Head):
    """
    NaryHead is base class for n-ary operation heads,
    data is a n-tuple of expression operands.
    """
    def data_to_str(self, data, parent_precedence):
        precedence = self.precedence
        r = ''
        for t in data:
            h, d = t.pair
            try:
                s = h.data_to_str(d, precedence)
            except AttributeError: # a temporary hack
                s = str(d)
            if r:
                r += self.op_symbol + s
            else:
                r += s
        if precedence < parent_precedence:
            return '(' + r + ')'
        return r
