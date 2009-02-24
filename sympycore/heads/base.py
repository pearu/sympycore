
__all__ = ['Head', 'UnaryHead', 'BinaryHead', 'NaryHead', 'HEAD']

not_implemented_error_msg = '%s.%s method, report to http://code.google.com/p/sympycore/issues/'

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

    def to_lowlevel(self, cls, data, pair):
        """
        Return a low-level representation of expression pair.  It is
        used in object comparison and hash computation methods.
        """
        return pair

    def scan(self, proc, cls, data, target):
        raise NotImplementedError(not_implemented_error_msg % (self, 'scan(proc, cls, data, target)')) #pragma NO COVER

    def walk(self, func, cls, data, target):
        raise NotImplementedError(not_implemented_error_msg % (self, 'walk(func, cls, data, target)')) #pragma NO COVER        

    def is_data_ok(self, cls, data):
        #print self, data
        return

    def __todo_repr__(self):
        # TODO: undefined __repr__ should raise not implemented error
        raise NotImplementedError('Head subclass must implement __repr__ method returning singleton name')
        
class AtomicHead(Head):
    """
    AtomicHead is a base class to atomic expression heads.
    """

    def scan(self, proc, cls, data, target):
        proc(cls, self, data, target)

    def walk(self, func, cls, data, target):
        return func(cls, self, data, target)

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

    def scan(self, proc, cls, expr, target):
        expr.head.scan(proc, cls, expr.data, target)
        proc(cls, self, expr, target)

    def walk(self, func, cls, operand, target):
        operand1 = operand.head.walk(func, cls, operand.data, operand)
        if operand1 is operand:
            return func(cls, self, operand, target)
        r = self.new(cls, operand1)
        return func(cls, r.head, r.data, r)
        
class BinaryHead(Head):
    """
    BinaryHead is base class for binary operation heads,
    data is a 2-tuple of expression operands.
    """
    def data_to_str_and_precedence(self, cls, (lhs, rhs)):
        rel_p = getattr(heads_precedence, repr(self))
        if isinstance(lhs, Expr):
            l, l_p = lhs.head.data_to_str_and_precedence(cls, lhs.data)
        else:
            l, l_p = str(lhs), 0.0
        if isinstance(rhs, Expr):
            r, r_p = rhs.head.data_to_str_and_precedence(cls, rhs.data)
        else:
            r, r_p = str(rhs), 0.0
        if l_p < rel_p: l = '(' + l + ')'
        if r_p < rel_p: r = '(' + r + ')'
        return l + self.op_symbol + r, rel_p

    def reevaluate(self, cls, (lhs, rhs)):
        return self.new(cls, (lhs, rhs))

    def scan(self, proc, cls, data, target):
        lhs, rhs = data
        lhs.head.scan(proc, cls, lhs.data, target)
        rhs.head.scan(proc, cls, rhs.data, target)
        proc(cls, self, data, target)

    def walk(self, func, cls, data, target):
        lhs, rhs = data
        lhs1 = lhs.head.walk(func, cls, lhs.data, lhs)
        rhs1 = rhs.head.walk(func, cls, rhs.data, rhs)
        if lhs1 is lhs and rhs1 is rhs:
            return func(cls, data, target)
        r = self.new(cls, (lhs1, rhs1))
        return func(cls, r.head, r.data, r)

class NaryHead(Head):
    """
    NaryHead is base class for n-ary operation heads,
    data is a n-tuple of expression operands.
    """
    def new(self, cls, data, evaluate=True):
        return cls(self, data)

    def reevaluate(self, cls, operands):
        return self.new(cls, operands)
    
    def data_to_str_and_precedence(self, cls, operand_seq):
        op_p = getattr(heads_precedence, repr(self))
        l = []
        for operand in operand_seq:
            o, o_p = operand.head.data_to_str_and_precedence(cls, operand.data)
            if o_p < op_p: o = '(' + o + ')'
            l.append(o)
        return self.op_symbol.join(l), op_p

    def scan(self, proc, cls, operands, target):
        for operand in operands:
            operand.head.scan(proc, cls, operand.data, target)
        proc(cls, self, operands, target)

    def walk(self, func, cls, operands, target):
        l = []
        flag = False
        for operand in operands:
            o = operand.head.walk(func, cls, operand.data, operand)
            if o is not operand:
                flag = True
            l.append(o)
        if flag:
            r = self.new(cls, l)
            return func(cls, r.head, r.data, r)
        return func(cls, self, operands, target)

class ArithmeticHead(Head):
    """ Base class for heads representing arithmetic operations.
    """

    def term_coeff(self, cls, expr):
        """ Return (term, coefficent) pair such that

          expr = term * coefficent
          coefficent is a number instance

        """
        raise NotImplementedError(not_implemented_error_msg % (self, 'term_coeff(self, cls, expr)')) #pragma NO COVER

    def as_add(self, cls, expr):
        """ Return expr as ADD expression.
        """
        raise NotImplementedError(not_implemented_error_msg % (self, 'as_add(cls, expr)')) #pragma NO COVER

    def as_term_coeff_dict(self, cls, expr):
        """ Return expr as TERM_COEFF_DICT expression.
        """
        raise NotImplementedError(not_implemented_error_msg % (self, 'as_term_coeff_dict(cls, expr)')) #pragma NO COVER
    
    def neg(self, cls, expr):
        """ Return negated expression: -expr.
        """
        raise NotImplementedError(not_implemented_error_msg % (self, 'neg(cls, expr)')) #pragma NO COVER

    def add(self, cls, lhs, rhs):
        """ Return a sum of expressions: lhs + rhs.
        """
        raise NotImplementedError(not_implemented_error_msg % (self, 'add(cls, lhs, rhs)')) #pragma NO COVER

    inplace_add = add_number = add

    def sub(self, cls, lhs, rhs):
        """ Return a subtract of expressions: lhs + rhs.
        """
        raise NotImplementedError(not_implemented_error_msg % (self, 'sub(cls, lhs, rhs)')) #pragma NO COVER

    def non_commutative_mul(self, cls, lhs, rhs):
        """ Return a non-commutative product of expressions: lhs * rhs.
        """
        raise NotImplementedError(not_implemented_error_msg % (self, 'non_commutative_mul(cls, lhs, rhs)')) #pragma NO COVER

    inplace_non_commutative_mul = non_commutative_mul_number = non_commutative_mul

    def commutative_mul(self, cls, lhs, rhs):
        """ Return a commutative product of expressions: lhs * rhs.
        """
        raise NotImplementedError(not_implemented_error_msg % (self, 'commutative_mul(cls, lhs, rhs)')) #pragma NO COVER

    inplace_commutative_mul = commutative_mul_number = commutative_mul

    def pow(self, cls, base, exp):
        """ Return a power of expressions: base ** exp.
        """
        raise NotImplementedError(not_implemented_error_msg % (self, 'pow(cls, base, exp)')) #pragma NO COVER

    def expand(self, cls, expr):
        """ Return expanded expression: open parenthesis of arithmetic operations.
        """
        raise NotImplementedError(not_implemented_error_msg % (self, 'expand(cls, expr)')) #pragma NO COVER

    def expand_intpow(self, cls, expr, intexp):
        """ Return expanded expr ** intexp where intexp is integer.
        """
        raise NotImplementedError(not_implemented_error_msg % (self, 'expand_intpow(cls, expr, intexpr)')) #pragma NO COVER
    
for k, v in Head.precedence_map.items():
    setattr(heads_precedence, k, v)

HEAD = Head()
