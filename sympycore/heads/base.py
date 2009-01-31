
__all__ = ['Head', 'UnaryHead', 'BinaryHead', 'NaryHead']

not_implemented_error_msg = '%s.%s() method, report to http://code.google.com/p/sympycore/issues/'

from ..core import Expr, heads, heads_precedence, Pair

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

    precedence_map = dict(
        LAMBDA = 0.0, ASSIGN = 0.0,
        ARG = 0.01, KWARG = 0.01, COLON = 0.01, COMMA = 0.01,
        OR = 0.02, AND = 0.03, NOT = 0.04,
        LT = 0.1, LE = 0.1, GT = 0.1, GE = 0.1, EQ = 0.09, NE = 0.09,
        IN = 0.1, NOTIN = 0.1, IS = 0.1, ISNOT = 0.1,
        BOR = 0.2, BXOR = 0.21, BAND = 0.22, 
        LSHIFT = 0.3, RSHIFT = 0.3,
        
        ADD = 0.4, SUB = 0.4, TERM_COEFF_DICT = 0.4,

        TERM_COEFF = 0.5, NCMUL = 0.5, MUL = 0.5, DIV = 0.5,
        MOD = 0.5, FLOORDIV = 0.5,
        FACTORS = 0.5, BASE_EXP_DICT = 0.5,

        POS = 0.6, NEG = 0.6, INVERT = 0.6,
        POW = 0.7, POWPOW = 0.71,
        ATTR = 0.81, SUBSCRIPT = 0.82, SLICE = 0.83, APPLY = 0.84, 
        TUPLE = 0.91, LIST = 0.92, DICT = 0.93,
        CALLABLE = 0.85,
        DOT = 0.9,
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
            obj._key = key
            obj.init(*args)
            if cls.is_singleton:
                cls._cache[key] = obj
                setattr(heads, repr(obj), obj)
        return obj

    def init(self, *args):
        # derived class may set attributes here
        pass #pragma NO COVER

    def as_unique_head(self):
        # used by the pickler support to make HEAD instances unique
        return self._cache.get(self._key, self)

    def data_to_str_and_precedence(self, cls, data):
        return '%s(%r, %r)' % (cls.__name__, self, data), 1.0

    def pair_to_lowlevel(self, pair):
        """
        Return a low-level representation of expression pair.  It is
        used in object comparison and hash computation methods.
        """
        return pair

class AtomicHead(Head):
    """
    AtomicHead is a base class to atomic expression heads.
    """

    def data_to_str(self, cls, data, parent_precedence):
        if isinstance(data, Expr):
            h, d = data.pair
            return h.data_to_str(cls, d, parent_precedence)
        s = '%s' % (data,)
        if self.get_precedence_for_data(data) < parent_precedence:
            return '(' + s + ')'
        return s

class UnaryHead(Head):
    """
    UnaryHead is base class for unary operation heads,
    data is an expression operand.
    """

    # Derived class must define a string member:
    op_symbol = None
    
    def data_to_str_and_precedence(self, cls, operand):
        u_p = getattr(heads_precedence, repr(self))
        o, o_p = operand.head.data_to_str_and_precedence(cls, operand.data)
        if o_p < u_p: o = '(' + o + ')'
        return self.op_symbol + o, u_p
    
class BinaryHead(Head):
    """
    BinaryHead is base class for binary operation heads,
    data is a 2-tuple of expression operands.
    """
    def data_to_str_and_precedence(self, cls, (lhs, rhs)):
        rel_p = getattr(heads_precedence, repr(self))
        l, l_p = lhs.head.data_to_str_and_precedence(cls, lhs.data)
        r, r_p = rhs.head.data_to_str_and_precedence(cls, rhs.data)
        if l_p < rel_p: l = '(' + l + ')'
        if r_p < rel_p: r = '(' + r + ')'
        return l + self.op_symbol + r, rel_p

class NaryHead(Head):
    """
    NaryHead is base class for n-ary operation heads,
    data is a n-tuple of expression operands.
    """
    def data_to_str_and_precedence(self, cls, operand_seq):
        op_p = getattr(heads_precedence, repr(self))
        l = []
        for operand in operand_seq:
            o, o_p = operand.head.data_to_str_and_precedence(cls, operand.data)
            if o_p < op_p: o = '(' + o + ')'
            l.append(o)
        return self.op_symbol.join(l), op_p

class ArithmeticHead(Head):
    """ Base class for heads representing arithmetic operations.
    """

    def term_coeff(self, cls, expr):
        """ Return (term, coefficent) pair such that

          expr = term * coefficent
          coefficent is a number instance

        """
        raise NotImplementedError(not_implemented_error_msg % (self, 'term_coeff'))

    def as_add(self, cls, expr):
        """ Return expr as ADD expression.
        """
        raise NotImplementedError(not_implemented_error_msg % (self, 'as_add'))

    def as_term_coeff_dict(self, cls, expr):
        """ Return expr as TERM_COEFF_DICT expression.
        """
        raise NotImplementedError(not_implemented_error_msg % (self, 'as_term_coeff_dict'))
    
    def as_ncmul(self, cls, expr):
        """ Return expr as NCMUL expression.
        """
        raise NotImplementedError(not_implemented_error_msg % (self, 'as_ncmul'))

    def neg(self, cls, expr):
        """ Return negated expression: -expr.
        """
        raise NotImplementedError(not_implemented_error_msg % (self, 'neg'))

    def add(self, cls, lhs, rhs):
        """ Return a sum of expressions: lhs + rhs.
        """
        raise NotImplementedError(not_implemented_error_msg % (self, 'add'))

    def sub(self, cls, lhs, rhs):
        """ Return a subtract of expressions: lhs + rhs.
        """
        raise NotImplementedError(not_implemented_error_msg % (self, 'sub'))

    def ncmul(self, cls, lhs, rhs):
        """ Return a non-commutative product of expressions: lhs * rhs.
        """
        raise NotImplementedError(not_implemented_error_msg % (self, 'ncmul'))

    def mul(self, cls, lhs, rhs):
        """ Return a product of expressions: lhs * rhs.
        """
        raise NotImplementedError(not_implemented_error_msg % (self, 'mul'))

    def pow(self, cls, base, exp):
        """ Return a power of expressions: base ** exp.
        """
        raise NotImplementedError(not_implemented_error_msg % (self, 'pow'))

    def expand(self, cls, expr):
        """ Return expanded expression: open parenthesis of arithmetic operations.
        """
        raise NotImplementedError(not_implemented_error_msg % (self, 'expand'))

    def expand_intpow(self, cls, expr, intexp):
        """ Return expanded expr ** intexp where intexp is integer.
        """
        raise NotImplementedError(not_implemented_error_msg % (self, 'expand_intpow'))
    
for k, v in Head.precedence_map.items():
    setattr(heads_precedence, k, v)
