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
                     INVERT, POS, NEG, ADD, SUB, MOD, MUL, DIV, FLOORDIV, POW,
                     LSHIFT, RSHIFT, DIVMOD, IS, ISNOT, LIST, SLICE,
                     NUMBER, SYMBOL, APPLY, TUPLE, LAMBDA, TERMS, FACTORS,
                     IN, NOTIN, SUBSCRIPT, SPECIAL)
from ..core import classes, Expr, objects

# XXX: Unimplemented expression parts:
# XXX: KeyWord, GetAttr
# XXX: function calls assume no optional nor *args nor *kwargs, same applies to lambda

EllipsisType = type(Ellipsis)
special_types = (EllipsisType, type(None))
containing_lst = set([IN, NOTIN])
boolean_lst = [AND, OR, NOT]
compare_lst = [LT, LE, GT, GE, EQ, NE, IN, NOTIN]
bit_lst = [BAND, BOR, BXOR, INVERT]
arith_lst = [POS, NEG, ADD, SUB, MOD, MUL, DIV, FLOORDIV, POW]
parentheses_map = { # defines operator precedence
    OR: [LAMBDA],
    AND: [LAMBDA, OR],
    NOT: [LAMBDA, AND, OR],
    LT: [LAMBDA] + boolean_lst,
    LE: [LAMBDA] + boolean_lst,
    GT: [LAMBDA] + boolean_lst,
    GE: [LAMBDA] + boolean_lst,
    EQ: [LAMBDA] + boolean_lst,
    NE: [LAMBDA] + boolean_lst,
    IN: [LAMBDA] + boolean_lst,
    NOTIN: [LAMBDA] + boolean_lst,
    IS: [LAMBDA, IN, NOTIN] + boolean_lst,
    ISNOT: [LAMBDA, IS, ISNOT] + boolean_lst,
    BOR: [LAMBDA] + compare_lst + boolean_lst,
    BXOR: [LAMBDA, BOR] + compare_lst + boolean_lst,
    BAND: [LAMBDA, BOR, BXOR] + compare_lst + boolean_lst,
    LSHIFT: [LAMBDA, BOR, BXOR, BAND] + compare_lst + boolean_lst,
    RSHIFT: [LAMBDA, BOR, BXOR, BAND] + compare_lst + boolean_lst,
    INVERT: [LAMBDA, BOR, BXOR, BAND, LSHIFT, RSHIFT] + compare_lst + boolean_lst,
    ADD: [LAMBDA] + compare_lst + boolean_lst,
    SUB: [LAMBDA, ADD] + compare_lst + boolean_lst,
    POS: [LAMBDA, ADD, SUB] + compare_lst + boolean_lst,
    NEG: [LAMBDA, ADD, SUB] + compare_lst + boolean_lst,
    MOD: [LAMBDA, ADD, SUB, POS, NEG] + compare_lst + boolean_lst,
    MUL: [LAMBDA, ADD, SUB, POS, NEG] + compare_lst + boolean_lst,
    DIV: [LAMBDA, ADD, SUB, POS, NEG] + compare_lst + boolean_lst,
    FLOORDIV: [LAMBDA, ADD, SUB, POS, NEG] + compare_lst + boolean_lst,
    POW: [LAMBDA, ADD, SUB, POS, NEG, MOD, MUL, DIV, FLOORDIV, POW] + compare_lst + boolean_lst,
    }

atomic_lst = set([SYMBOL, NUMBER])
unary_lst = set([POS, NEG, NOT, INVERT])
binary_lst = set([AND, OR, BAND, BOR, BXOR, ADD, SUB, MUL, DIV, FLOORDIV,
                  MOD, POW, LSHIFT, RSHIFT, DIVMOD])

_is_name = re.compile(r'\A[a-zA-z_]\w*\Z').match
_is_number = re.compile(r'\A[-]?\d+\Z').match

head_order = [NUMBER, SYMBOL, APPLY,
              POS, ADD,
              SUB,
              MOD, MUL, DIV, FLOORDIV, POW,
              NEG,
              BOR, BXOR, BAND, INVERT,
              EQ, NE, LT, GT, LE, GE,
              OR, AND, NOT,
              LAMBDA, TUPLE, LIST
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
    if h1 in atomic_lst:
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

convert_head_Op_map = {
    NEG : 'Neg',
    POS : 'Pos',
    ADD : 'Add',
    SUB : 'Sub',
    MUL : 'Mul',
    DIV : 'Div',
    FLOORDIV : 'FloorDiv',
    POW : 'Pow',
    MOD : 'Mod',
    AND : 'And',
    OR : 'Or',
    NOT : 'Not',
    LT : 'Lt',
    GT : 'Gt',
    LE : 'Le',
    GE : 'Ge',
    EQ : 'Eq',
    NE : 'Ne',
    }

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
            # handle low-level numbers and constants, as well as Verbatim subclasses
            return obj.as_verbatim()
        if isinstance(obj, slice):
            slice_args = obj.start, obj.stop, obj.step
            return cls(SLICE, tuple(map(cls.convert, slice_args)))
        elif isinstance(obj, tuple):
            return cls(TUPLE, tuple(map(cls.convert, obj)))
        elif isinstance(obj, list):
            return cls(LIST, tuple(map(cls.convert, obj)))
        elif isinstance(obj, special_types):
            return cls(SPECIAL, obj)
        return Verbatim(SYMBOL, obj)

    def as_verbatim(self):
        return self

    def as_algebra(self, cls, source=None):
        head, rest = self.pair
        if head is NUMBER:
            return cls(rest)
        if head is SYMBOL:
            return cls.convert_symbol(rest)
        n = convert_head_Op_map.get(head)
        if n is not None:
            if head in unary_lst:
                return getattr(cls, n)(rest.as_algebra(cls.get_operand_algebra(head, 0)))
            return getattr(cls, n)(*[r.as_algebra(cls.get_operand_algebra(head, i)) for i,r in enumerate(rest)])
        if head is APPLY:
            func = rest[0]
            args = rest[1:]
            fcls = objects.get_function_ring((cls,)*len(args), cls)
            f = func.as_algebra(fcls)
            return f(*[a.as_algebra(cls) for a in args])
        if head in containing_lst:
            element, container = rest
            container = container.as_algebra(cls.get_operand_algebra(IN, 1))
            element_algebra = container.get_element_algebra()
            element = element.as_algebra(element_algebra)
            r = cls.Element(element, container)
            if head is NOTIN:
                return cls.Not(r)
            return r
        if head is SUBSCRIPT:
            obj, index = rest
            obj = obj.as_algebra(cls)
            return obj[index]
        print `head, rest`
        raise TypeError('%r cannot be converted to %s algebra' % (self, cls.__name__))

    def __repr__(self):
        return '%s(%r, %r)' % (type(self).__name__, self.head, self.data)

    def __str__(self):
        s = self._str
        if s is None:
            self._str = s = self._compute_str()
        return s

    def _compute_str(self):
        head, rest = self.pair
        if head in atomic_lst:
            if callable(rest):
                s = rest.__name__
            else:
                s = str(rest)
            if not (_is_name(s) or _is_number(s)) and not s.startswith('('):
                s = '((%s))' % (s)
            return s
        if head is SPECIAL:
            if isinstance(rest, EllipsisType):
                return '...'
            return str(rest)
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
        if head is SUBSCRIPT:
            obj = rest[0]
            indices = rest[1:]
            s = str(obj)
            if _is_name(s):
                return '%s[%s]' % (s, ', '.join(map(str, indices)))
            return '(%s)[%s]' % (s, ', '.join(map(str, indices)))
        if head is SLICE:
            start, stop, step = rest
            h, d = start.pair
            if h is SPECIAL and d is None: start = None
            h, d = stop.pair
            if h is SPECIAL and d is None: stop = None
            h, d = step.pair
            if h is SPECIAL and d is None: step = None
            if start is None:
                if stop is None:
                    if step is None: return ':'
                    else: return '::%s' % step
                else:
                    if step is None: return ':%s' % stop
                    else: return ':%s:%s' % (stop, step)
            else:
                if stop is None:
                    if step is None: return '%s:' % start
                    else: return '%s::%s' % (start, step)
                else:
                    if step is None: return '%s:%s' % (start, stop)
                    else: return '%s:%s:%s' % (start, stop, step)
        if head is LAMBDA:
            args = rest[0]
            assert args.head is TUPLE,`args`
            body = rest[1]
            if len(args.data)==1:
                return 'lambda %s: %s' % (str(args.data[0]), body)
            return 'lambda %s: %s' % (str(args)[1:-1], body)
        if head is TUPLE:
            if len(rest)==1:
                return '(%s,)' % (rest[0])
            return '(%s)' % (', '.join(map(str,rest)))
        if head is LIST:
            return '[%s]' % (', '.join(map(str,rest)))
        if head in unary_lst:
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
        if head is DIVMOD:
            return 'divmod(%s, %s)' % rest
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
            return str(head) + l[0]
        return str(head).join(l)

    def as_tree(self, tab='', level=0):
        if level:
            r = []
        else:
            r = [self.__class__.__name__+':']
        head, rest = self.pair
        if head in atomic_lst:
            r.append(tab + '%r[%s]' % (head, rest))
        else:
            r.append(tab + '%r[' % (head))
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

    for _h in unary_lst:
        exec '''\
def %s(self):
    return Verbatim(%r, self)
''' % (_h.op_mth, _h)

    for _h in binary_lst:
        if _h.op_mth:
            exec '''\
def %s(self, other):
    other = self.convert(other)
    return Verbatim(%r, (self, other))
''' % (_h.op_mth, _h)
        if _h.op_rmth:
            exec '''\
def %s(self, other):
    other = self.convert(other)
    return Verbatim(%r, (other, self))
''' % (_h.op_rmth, _h)

    __truediv__ = __div__
    __rtruediv__ = __rdiv__

    def __call__(self, *args):
        return Verbatim(APPLY, (self,)+args)

    def __getitem__(self, key):
        if type(key) is tuple:
            key = tuple(map(self.convert, key))
            return Verbatim(SUBSCRIPT, (self,)+key)
        key = self.convert(key)
        return Verbatim(SUBSCRIPT, (self, key))

classes.Verbatim = Verbatim

########### string to Verbatim parser ############

node_names = []
skip_names = ['Module','Stmt','Discard']
for n, cls in ast.__dict__.items():
    if n in skip_names:
        continue
    if isinstance(cls, (type,types.ClassType)) and issubclass(cls, ast.Node):
        node_names.append(n)

node_map = dict(Add=ADD, Mul=MUL, Sub=SUB,
                Div=DIV, FloorDiv=FLOORDIV, TrueDiv=DIV,
                UnaryAdd=POS, UnarySub=NEG, Mod=MOD, Not=NOT,
                Or=OR, And=AND, Power=POW,
                Bitand=BAND,Bitor=BOR,Bitxor=BXOR,
                Tuple=TUPLE, Subscript=SUBSCRIPT,
                Invert=INVERT, LeftShift=LSHIFT, RightShift=RSHIFT,
                List=LIST, Sliceobj=SLICE
                )

callfunc_map = dict(divmod=DIVMOD, slice=SLICE)

compare_map = {'<':LT, '>':GT, '<=':LE, '>=':GE,
               '==':EQ, '!=':NE, 'in':IN, 'not in': NOTIN,
               'is':IS, 'is not':ISNOT}

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
        if head in unary_lst:
            assert len(lst)==1,`lst`
            self.append(Verbatim(head, lst[0]))
        else:
            self.append(Verbatim(head, tuple(lst)))
        
    # for atomic instance:
    def add(self, *args):
        self.append(Verbatim(*args))

    for _n in node_names:
        if _n in node_map:
            continue
        exec '''\
def visit%s(self, node, *args):
    print "warning: using default visit%s:", node
    self.start(%r)
    for child in node.getChildNodes():
        self.visit(child, *args)
    self.end()
''' % (_n, _n, _n)

    for _n,_v in node_map.items():
        exec '''\
def visit%s(self, node):
    self.start(%r)
    for child in node.getChildNodes():
        self.visit(child)
    self.end()
''' % (_n, _v)

    # visitNode methods:

    def visitName(self, node):
        self.add(SYMBOL, node.name)

    def visitConst(self, node):
        if node.value is None:
            self.add(SPECIAL, None)
        else:
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

    def visitCallFunc(self, node):
        childs = node.getChildNodes()
        func = childs[0]
        if isinstance(func, ast.Name) and func.name in callfunc_map:
            self.start(callfunc_map[func.name])
            for child in childs[1:]:
                self.visit(child)
            self.end()
            return
        self.start(APPLY)
        for child in childs:
            self.visit(child)
        self.end()

    def visitSlice(self, node):
        n = ast.Subscript(node.expr, compiler.consts.OP_APPLY, [ast.Sliceobj(node.asList()[2:])])
        self.visit(n)

    def visitSliceobj(self, node):
        childs = list(node.asList())
        childs.extend([None]*(3-len(childs)))
        assert len(childs)==3,`childs`
        self.start(SLICE)
        for child in childs:
            if child is None:
                self.add(SPECIAL, child)
            else:
                self.visit(child)
        self.end()

    def visitEllipsis(self, node):
        self.add(SPECIAL, Ellipsis)

def string2Verbatim(expr):
    """ Parse string expr to Verbatim.
    """
    node = compiler.parse(expr)
    return compiler.walk(node, VerbatimWalker()).stack.pop()
