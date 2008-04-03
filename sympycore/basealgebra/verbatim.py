#
# Created in 2007 by Fredrik Johansson
# Expression parser added by Pearu Peterson
#
""" Provides PrimitiveAlgebra class and expression parser.
"""
from __future__ import absolute_import
__docformat__ = "restructuredtext"
__all__ = ['Verbatim']

import types
import re
import compiler
from compiler import ast

from .algebra import Algebra
from ..utils import (OR, AND, NOT, LT, LE, GT, GE, EQ, NE, BAND, BOR, BXOR,
                     INVERT, POS, NEG, ADD, SUB, MOD, MUL, DIV, POW,
                     NUMBER, SYMBOL, APPLY, TUPLE, LAMBDA, head_to_string)
from ..core import classes, Expr

# XXX: Unimplemented expression parts:
# XXX: LeftShift, RightShift, List*, Subscript, Slice, KeyWord, GetAttr, Ellipsis
# XXX: function calls assume no optional nor *args nor *kwargs, same applies to lambda

boolean_lst = [AND, OR, NOT]
compare_lst = [LT, LE, GT, GE, EQ, NE]
bit_lst = [BAND, BOR, BXOR, INVERT]
arith_lst = [POS, NEG, ADD, SUB, MOD, MUL, DIV, POW]
parentheses_map = {
    OR: [LAMBDA],
    AND: [LAMBDA, OR],
    NOT: [LAMBDA, AND, OR],
    LT: [LAMBDA] + boolean_lst,
    LE: [LAMBDA] + boolean_lst,
    GT: [LAMBDA] + boolean_lst,
    GE: [LAMBDA] + boolean_lst,
    EQ: [LAMBDA] + boolean_lst,
    NE: [LAMBDA] + boolean_lst,
    BOR: [LAMBDA] + compare_lst + boolean_lst,
    BXOR: [LAMBDA, BOR] + compare_lst + boolean_lst,
    BAND: [LAMBDA, BOR, BXOR] + compare_lst + boolean_lst,
    INVERT: [LAMBDA, BOR, BXOR, BAND] + compare_lst + boolean_lst,
    ADD: [LAMBDA] + compare_lst + boolean_lst,
    SUB: [LAMBDA, ADD] + compare_lst + boolean_lst,
    POS: [LAMBDA, ADD, SUB] + compare_lst + boolean_lst,
    NEG: [LAMBDA, ADD, SUB] + compare_lst + boolean_lst,
    MOD: [LAMBDA, ADD, SUB, POS, NEG] + compare_lst + boolean_lst,
    MUL: [LAMBDA, ADD, SUB, POS, NEG, MOD] + compare_lst + boolean_lst,
    DIV: [LAMBDA, ADD, SUB, POS, NEG, MOD, MUL,] + compare_lst + boolean_lst,
    POW: [LAMBDA, ADD, SUB, POS, NEG, MOD, MUL, DIV, POW] + compare_lst + boolean_lst,
    }

_is_name = re.compile(r'\A[a-zA-z_]\w*\Z').match
_is_number = re.compile(r'\A\d+\Z').match

head_order = [NUMBER, SYMBOL, APPLY,
              POS, ADD,
              SUB,
              MOD, MUL, DIV, POW,
              NEG,
              BOR, BXOR, BAND, INVERT,
              EQ, NE, LT, GT, LE, GE,
              OR, AND, NOT,
              LAMBDA, TUPLE
              ]

def tree_sort(a, b):
    if callable(a):
        if callable(b):
            return cmp(str(a),str(b))
        else:
            return cmp(head_order.index(APPLY), head_order.index(b.head))
    elif callable(b):
        return cmp(head_order.index(a.head), head_order.index(APPLY))
    h1 = a.head
    h2 = b.head
    c = cmp(head_order.index(h1), head_order.index(h2))
    if c:
        return c
    t1,t2 = a.data, b.data
    if h1 is SYMBOL or h1 is NUMBER:
        return cmp(t1, t2)
    c = cmp(len(t1), len(t2))
    if c:
        return c
    if h1 in [ADD, MUL]:
        t1 = sorted(t1, cmp=tree_sort)
        t2 = sorted(t2, cmp=tree_sort)
    for i1,i2 in zip(t1,t2):
        c = tree_sort(i1, i2)
        if c: return c
    return 0

class Verbatim(Algebra):
    """ Represents an unevaluated expression.
    """

    commutative_add = None
    commutative_mul = None
    disable_sorting = None

    _str = None

    @classmethod
    def convert(cls, obj):
        if isinstance(obj, (str, unicode)):
            obj = string2Verbatim(obj)
        if hasattr(obj, 'as_verbatim'):
            return obj.as_verbatim()
        if isinstance(obj, cls):
            return obj
        return Verbatim(SYMBOL, obj)

    def as_verbatim(self):
        return self

    def as_algebra(self, cls, source=None):
        head, rest = self.pair
        if head is NUMBER:
            if hasattr(rest,'coefftypes') and isinstance(rest, cls.coefftypes):
                return cls.Number(rest)
            return cls.convert(rest)
        if head is SYMBOL:
            r = cls.get_predefined_symbols(rest)
            if r is not None:
                return r
            return cls.Symbol(rest)
        if head is ADD:
            return cls.Add(*[r.as_algebra(cls) for r in rest])
        if head is SUB:
            return cls.Sub(*[r.as_algebra(cls) for r in rest])
            return rest[0].as_algebra(cls) - cls.Add(*[r.as_algebra(cls) for r in rest[1:]])
        if head is MUL:
            return cls.Mul(*[r.as_algebra(cls) for r in rest])
        if head is DIV:
            return cls.Div(*[r.as_algebra(cls) for r in rest])
        if head is POW:
            base, exp = rest
            h, r = exp.pair
            if h is NUMBER:
                return cls.Pow(base.as_algebra(cls), cls.convert_exponent(r))
            return cls.Pow(base.as_algebra(cls), exp.as_algebra(cls))
        if head is NEG:
            if isinstance(rest, tuple):
                assert len(rest)==1,`rest`
                rest = rest[0]
            return -(rest.as_algebra(cls))
        if head is POS:
            if isinstance(rest, tuple):
                assert len(rest)==1,`rest`
                rest = rest[0]
            return +(rest.as_algebra(cls))
        if head is APPLY:
            func = rest[0].as_algebra(cls)
            args = [cls(a) for a in rest[1:]]
            #if callable(func):
            #    return func(*args)
            return cls(APPLY, (func,)+ tuple(args))
        if head is LT: return cls.Lt(*[r.as_algebra(classes.Calculus) for r in rest])
        if head is LE: return cls.Le(*[r.as_algebra(classes.Calculus) for r in rest])
        if head is GT: return cls.Gt(*[r.as_algebra(classes.Calculus) for r in rest])
        if head is GE: return cls.Ge(*[r.as_algebra(classes.Calculus) for r in rest])
        if head is EQ: return cls.Eq(*[r.as_algebra(classes.Calculus) for r in rest])
        if head is NE: return cls.Ne(*[r.as_algebra(classes.Calculus) for r in rest])
        if head is AND:
            return cls.And(*[r.as_algebra(cls) for r in rest])
        if head is OR:
            return cls.Or(*[r.as_algebra(cls) for r in rest])
        if head is NOT:
            return cls.Not(rest[0].as_algebra(cls))
        if head is MOD:
            return cls.Mod(*[r.as_algebra(cls) for r in rest])
        raise TypeError('%r cannot be converted to %s algebra' % (self, cls.__name__))

    def __str__(self):
        s = self._str
        if s is None:
            self._str = s = self._compute_str()
        return s

    def _compute_str(self):
        head, rest = self.pair
        if head is SYMBOL or head is NUMBER:
            if callable(rest):
                s = rest.__name__
            else:
                s = str(rest)
            if not (_is_name(s) or _is_number(s)) and not s.startswith('('):
                s = '((%s))' % (s)
            return s
        if head is APPLY:
            func = rest[0]
            args = rest[1:]
            if callable(func) and hasattr(func,'__name__'):
                s = func.__name__
            else:
                s = str(func)
            if _is_name(s):
                return '%s(%s)' % (s, ', '.join(map(str,args)))
            return '(%s)(%s)' % (s, ', '.join(map(str,args)))
        if head is LAMBDA:
            args = rest[0]
            body = rest[1]
            return 'lambda %s: %s' % (str(args)[1:-1], body)
        if head is TUPLE:
            return '(%s)' % (', '.join(map(str,rest)))
        if head is NEG or head is POS or head is NOT:
            return '%s%s' % (head, rest)
        if head is ADD:
            if len(rest)>100:
                self.disable_sorting = True
            if self.commutative_add:
                if not self.disable_sorting:
                    rest = sorted(rest, cmp=tree_sort)
            r = ''
            for t in rest:
                h = t.head
                while h is POS:
                    h,t = r.pair
                sign = ' + '
                if h is NEG:
                    if not r:
                        r = str(t)
                        continue
                    sign = ' - '
                    s = str(t.data)
                else:
                    s = str(t)
                    if not r:
                        r = s
                        continue
                    sign = ' + '
                r += sign + s
            return r
        if head is MUL and self.commutative_mul:
            if len(rest)>100:
                self.disable_sorting = True
            if not self.disable_sorting:
                rest = sorted(rest, cmp=tree_sort)
        try:
            len(rest)
        except TypeError:
            return '((%s%s))' (head, rest)
        l = []
        for t in rest:
            h = t.head if isinstance(t, Algebra) else None
            s = str(t)
            if h is NUMBER and s.startswith('-'):
                h = ADD
                if h in parentheses_map.get(head, [h]) and l:
                    l.append('(%s)' % s)
                else:
                    l.append(s)
            elif h in parentheses_map.get(head, [h]):
                l.append('(%s)' % s)
            else:
                l.append(s)

        if callable(head):
            return '%s(%s)' % (head.__name__, ', '.join(l))

        if len(l)==1: # unary operation
            return head + l[0]
        return head.join(l)

    def as_tree(self, tab='', level=0):
        if level:
            r = []
        else:
            r = [self.__class__.__name__+':']
        head, rest = self.pair
        if head in [SYMBOL, NUMBER]:
            r.append(tab + '%s[%s]' % (head_to_string[head], rest))
        else:
            r.append(tab + '%s[' % (head_to_string[head]))
            if isinstance(rest, Verbatim):
                rest = rest,
            for t in rest:
                r.append(t.as_tree(tab=tab + '  ', level=level+1))
            r.append(tab+']')
        return '\n'.join(r)

    def __eq__(self, other):
        if type(other) is Verbatim:
            return self.pair == other.pair
        return False

    def __pos__(self):
        return Verbatim(POS, self)
    def __neg__(self):
        return Verbatim(NEG, self)
    def __add__(self, other):
        other = self.convert(other)
        return Verbatim(ADD, (self, other))
    def __radd__(self, other):
        other = self.convert(other)
        return Verbatim(ADD, (other, self))
    def __sub__(self, other):
        other = self.convert(other)
        return Verbatim(SUB, (self, other))
    def __rsub__(self, other):
        other = self.convert(other)
        return Verbatim(SUB, (other, self))
    def __mul__(self, other):
        other = self.convert(other)
        return Verbatim(MUL, (self, other))
    def __rmul__(self, other):
        other = self.convert(other)
        return Verbatim(MUL, (other, self))
    def __div__(self, other):
        other = self.convert(other)
        return Verbatim(DIV, (self, other))
    def __rdiv__(self, other):
        other = self.convert(other)
        return Verbatim(DIV, (other, self))
    def __pow__(self, other):
        other = self.convert(other)
        return Verbatim(POW, (self, other))
    def __rpow__(self, other):
        other = self.convert(other)
        return Verbatim(POW, (other, self))
    __truediv__ = __div__
    __rtruediv__ = __rdiv__


classes.Verbatim = Verbatim

########### string to Verbatim parser ############

node_names = []
skip_names = ['Module','Stmt','Discard']
for n, cls in ast.__dict__.items():
    if n in skip_names:
        continue
    if isinstance(cls, (type,types.ClassType)) and issubclass(cls, ast.Node):
        node_names.append(n)

node_map = dict(Add='ADD', Mul='MUL', Sub='SUB', Div='DIV', FloorDiv='DIV',
                UnaryAdd='POS', UnarySub='NEG', Mod='MOD', Not='NOT',
                Or='OR', And='AND', Power='POW',
                Bitand='BAND',Bitor='BOR',Bitxor='BXOR',CallFunc='APPLY',
                Tuple='TUPLE',
                )
compare_map = {'<':LT, '>':GT, '<=':LE, '>=':GE,
               '==':EQ, '!=':NE}

class VerbatimWalker:
    """ Helper class for expression parser.
    """

    def __init__(self):
        self.stack = []

    # for composite instance:
    def start(self, head):
        self.stack.append([head, []])
    def append(self, obj):
        stack = self.stack
        if not stack:
            stack.append(obj)
        else:
            stack[-1][1].append(obj)
    def end(self):
        head, lst = self.stack.pop()
        if self.stack:
            last = self.stack[-1]
            if last[0]==head and head in [ADD, MUL]:
                # apply associativity:
                last[1].extend(lst)
                return
        self.append(Verbatim(head, tuple(lst)))
    # for atomic instance:
    def add(self, *args):
        self.append(Verbatim(*args))

    for _n in node_names:
        if _n in node_map:
            continue
        exec '''\
def visit%s(self, node, *args):
    print "warning: using default visit%s"
    self.start(%r)
    for child in node.getChildNodes():
        self.visit(child, *args)
    self.end()
''' % (_n, _n, _n)

    for _n,_v in node_map.items():
        exec '''\
def visit%s(self, node):
    self.start(%s)
    for child in node.getChildNodes():
        self.visit(child)
    self.end()
''' % (_n, _v)

    # visitNode methods:
    def visitName(self, node):
        self.add(SYMBOL, node.name)

    def visitConst(self, node):
        self.add(NUMBER, node.value)

    def visitCompare(self, node):
        lhs = node.expr
        op, rhs = node.ops[0]
        if len(node.ops)==1:
            self.start(compare_map[op])
            self.visit(lhs)
            self.visit(rhs)
            self.end()
            return
        n = ast.And([ast.Compare(lhs, node.ops[:1]),
                     ast.Compare(rhs, node.ops[1:])])
        self.visit(n)

    def visitLambda(self, node):
        self.start(LAMBDA)
        self.visit(ast.Tuple([ast.Name(n) for n in node.argnames]))
        self.visit(node.code)
        self.end()

def string2Verbatim(expr):
    """ Parse string expr to Verbatim.
    """
    node = compiler.parse(expr)
    return compiler.walk(node, VerbatimWalker()).stack.pop()
