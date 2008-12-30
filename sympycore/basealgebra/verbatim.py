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
import compiler
from compiler import ast

from .algebra import Algebra
from ..utils import (OR, AND, NOT, LT, LE, GT, GE, EQ, NE, BAND, BOR, BXOR,
                     INVERT, POS, NEG, ADD, SUB, MOD, MUL, DIV, FLOORDIV, POW,
                     LSHIFT, RSHIFT, IS, ISNOT, LIST, SLICE,
                     NUMBER, SYMBOL, APPLY, TUPLE, LAMBDA, TERMS, FACTORS,
                     IN, NOTIN, SUBSCRIPT, SPECIAL, DICT, ATTR, KWARG)
from ..heads import CALLABLE
from ..core import classes, Expr, objects

# Restrictions:
#
#    Star and double star function arguments are not implemented,
#    i.e. parsing 'f(*a)' and 'f(**b)' will fail.
#
# TODO: IfExp support: parse `a if b else c` to Verbatim(IF, (b, a, c))

EllipsisType = type(Ellipsis)
special_types = (EllipsisType, type(None), type(NotImplemented))
special_objects = set([Ellipsis, None, NotImplemented])

containing_lst = set([IN, NOTIN])

atomic_lst = set([SYMBOL, NUMBER])
unary_lst = set([POS, NEG, NOT, INVERT])
binary_lst = set([AND, OR, BAND, BOR, BXOR, ADD, SUB, MUL, DIV, FLOORDIV,
                  MOD, POW, LSHIFT, RSHIFT])

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
            head, data = self.pair
            s = head.data_to_str(data, 0.0)
            if not self.is_writable:
                self._str = s
        return s

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
        if _h.op_mth:
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

    def __divmod__(self, other):
        other = self.convert(other)
        return Verbatim(APPLY, (Verbatim(CALLABLE, divmod), self, other))

    def __call__(self, *args, **kwargs):
        convert = self.convert
        args = map(convert, args)
        for k, v in kwargs.items():
            args.append(Verbatim(KWARG, (convert(k), convert(v))))
        return Verbatim(APPLY, (self,)+tuple(args))

    def __getitem__(self, key):
        if type(key) is tuple:
            key = tuple(map(self.convert, key))
            return Verbatim(SUBSCRIPT, (self,)+key)
        key = self.convert(key)
        return Verbatim(SUBSCRIPT, (self, key))

    def __getattr__(self, attr):
        # warning: with this feature hasattr() may return True when not desired.
        if not attr.startswith('_'):
            return Verbatim(ATTR, (self, self.convert(attr)))
        raise AttributeError

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

callfunc_map = dict(#divmod=DIVMOD,
                    slice=SLICE)

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
    print "WARNING: using default unsupported visit%s, node=", node
    self.start(%r)
    for child in node.asList():
        if isinstance(child, ast.Node):
            self.visit(child, *args)
        else:
            self.append(child)
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
        if node.value in special_objects:
            self.add(SPECIAL, node.value)
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
        assert not (node.kwargs or node.varargs),`node` # parsing `lambda *args, **kwargs: ..` not supported
        self.start(LAMBDA)
        self.start(TUPLE)
        for n,d in zip(node.argnames, (len(node.argnames) - len(node.defaults))*[None] + list(node.defaults)):
            if d is None:
                self.visit(ast.Name(n))
            else:
                self.visit(ast.Keyword(n, d))
        self.end()
        self.visit(node.code)
        self.end()

    def visitCallFunc(self, node):
        if node.star_args is not None:
            raise NotImplementedError('parsing function star arguments')
        if node.dstar_args is not None:
            raise NotImplementedError('parsing function double star arguments')
        func = node.node
        if isinstance(func, ast.Name) and func.name in callfunc_map:
            self.start(callfunc_map[func.name])
            for child in node.args:
                self.visit(child)
            self.end()
            return
        self.start(APPLY)
        self.visit(func)
        for child in node.args:
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

    def visitDict(self, node):
        self.start(DICT)
        for k,v in node.items:
            self.visit(k)
            self.visit(v)
            # collect key and value to a 2-tuple:
            self.stack[-1][1][-2] = tuple(self.stack[-1][1][-2:])
            del self.stack[-1][1][-1]
        self.end()

    def visitGetattr(self, node):
        self.start(ATTR)
        self.visit(node.expr)
        self.visit(ast.Name(node.attrname))
        self.end()

    def visitKeyword(self, node):
        self.start(KWARG)
        self.visit(ast.Name(node.name))
        self.visit(node.expr)
        self.end()

class ast_Pair(ast.Tuple):
    pass

def string2Verbatim(expr):
    """ Parse string expr to Verbatim.
    """
    node = compiler.parse(expr)
    return compiler.walk(node, VerbatimWalker()).stack.pop()
