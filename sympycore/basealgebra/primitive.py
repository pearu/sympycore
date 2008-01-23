
from __future__ import absolute_import
import types
import re
import compiler
from compiler import ast

from .algebra import BasicAlgebra

OR = intern(' or ')
AND = intern(' and ')
NOT = intern('not ')

LT = intern('<')
LE = intern('<=')
GT = intern('>')
GE = intern('>=')
EQ = intern('==')
NE = intern('!=')

BAND = intern('&')
BOR = intern('|')
BXOR = intern('^')
INVERT = intern('~')

POS = intern('+')
NEG = intern('-')
ADD = intern(' + ')
SUB = intern(' - ')
MOD = intern('%')
MUL = intern('*')
DIV = intern('/')
POW = intern('**')

NUMBER = intern('N')
SYMBOL = intern('S')
APPLY = intern('A')
TUPLE = intern('T')
LAMBDA = intern('L')

head_to_string = {\
    OR:'OR', AND:'AND', NOT:'NOT',
    LT:'LT', LE:'LE', GT:'GT', GE:'GE', NE:'NE',
    BAND:'BAND', BOR:'BOR', BXOR:'BXOR', INVERT:'INVERT',
    POS:'POS', NEG:'NEG', ADD:'ADD', SUB:'SUB', MOD:'MOD', MUL:'MUL', DIV:'DIV', POW:'POW',
    NUMBER:'NUMBER', SYMBOL:'SYMBOL', APPLY:'APPLY', TUPLE:'TUPLE', LAMBDA:'LAMBDA',
    }

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
            return cmp(a,b)
        else:
            return cmp(head_order.index(APPLY), head_order.index(b.tree[0]))
    elif callable(b):
        return cmp(head_order.index(a.tree[0]), head_order.index(APPLY))
    h1 = a.tree[0]
    h2 = b.tree[0]
    c = cmp(head_order.index(h1), head_order.index(h2))
    if c:
        return c
    t1,t2 = a.tree[1], b.tree[1]
    if h1 is SYMBOL or h1 is NUMBER or h1 is APPLY:
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

class PrimitiveAlgebra(BasicAlgebra):

    commutative_add = None
    commutative_mul = None
    disable_sorting = None

    def __new__(cls, tree, head=None):
        if head is None:
            return cls.convert(tree)
        if isinstance(tree, cls):
            return tree
        if type(tree) is not tuple:
            tree = (head, tree)
        obj = object.__new__(cls)
        obj.tree = tree
        return obj

    #def __repr__(self):
    #    return '%s(%r, head=%s)' % (self.__class__.__name__, self.tree[1],
    #                                head_to_string[self.tree[0]])

    @classmethod
    def convert(cls, obj):
        if isinstance(obj, (str, unicode)):
            obj = string2PrimitiveAlgebra(obj)
        if hasattr(obj, 'as_primitive'):
            return obj.as_primitive()
        if isinstance(obj, cls):
            return obj
        return PrimitiveAlgebra(obj, head=SYMBOL)

    def as_primitive(self):
        return self

    def as_algebra(self, cls, source=None):
        head, rest = self.tree
        if head is NUMBER:
            return cls(rest, head=NUMBER)
        if head is SYMBOL:
            return cls(rest, head=SYMBOL)
        if head is ADD:
            return cls.Add(*[r.as_algebra(cls) for r in rest])
        if head is SUB:
            return rest[0].as_algebra(cls) - cls.Add(*[r.as_algebra(cls) for r in rest[1:]])
        if head is MUL:
            return cls.Mul(*[r.as_algebra(cls) for r in rest])
        if head is DIV:
            return rest[0].as_algebra(cls) / cls.Mul(*[r.as_algebra(cls) for r in rest[1:]])
        if head is POW:
            return cls.Pow(*[r.as_algebra(cls) for r in rest])
        if head is NEG:
            return -(rest[0].as_algebra(cls))
        if head is POS:
            return +(rest[0].as_algebra(cls))
        raise NotImplementedError('as_algebra(%s): %s' % (cls, self))

    def __str__(self):
        head, rest = self.tree
        if head is SYMBOL or head is NUMBER:
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
        if len(rest)>100:
            self.disable_sorting = True
        if head is ADD:
            if self.commutative_add:
                if not self.disable_sorting:
                    rest = sorted(rest, cmp=tree_sort)
            r = ''
            for t in rest:
                h = t.tree[0]
                while h is POS:
                    t = t.tree[1][0]
                    h = t.tree[0]
                sign = ' + '
                if h is NEG:
                    if not r:
                        r = str(t)
                        continue
                    sign = ' - '
                    s = str(t.tree[1][0])
                else:
                    s = str(t)
                    if not r:
                        r = s
                        continue
                    sign = ' + '
                r += sign + s
            return r
        if head is MUL and self.commutative_mul:
            if not self.disable_sorting:
                rest = sorted(rest, cmp=tree_sort)
        l = []
        for t in rest:
            h = t.tree[0]
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

        if len(l)==1: # unary operation
            return head + l[0]
        return head.join(l)

    def as_tree(self, tab='', level=0):
        if level:
            r = []
        else:
            r = [self.__class__.__name__+':']
        head, rest = self.tree
        if head in [SYMBOL, NUMBER]:
            r.append(tab + '%s[%s]' % (head_to_string[head], rest))
        else:
            r.append(tab + '%s[' % (head_to_string[head]))
            for t in rest:
                r.append(t.as_tree(tab=tab + '  ', level=level+1))
            r.append(tab+']')
        return '\n'.join(r)

    def __eq__(self, other):
        if type(other) is PrimitiveAlgebra:
            return self.tree == other.tree
        return self.tree == other

    def __hash__(self):
        return hash(self.tree)

    def __pos__(self):
        return PrimitiveAlgebra((POS, (self,)))
    def __neg__(self):
        return PrimitiveAlgebra((NEG, (self,)))
    def __add__(self, other):
        other = self.convert(other)
        return PrimitiveAlgebra((ADD, (self, other)))
    def __radd__(self, other):
        other = self.convert(other)
        return PrimitiveAlgebra((ADD, (other, self)))
    def __sub__(self, other):
        other = self.convert(other)
        return PrimitiveAlgebra((SUB, (self, other)))
    def __rsub__(self, other):
        other = self.convert(other)
        return PrimitiveAlgebra((SUB, (other, self)))
    def __mul__(self, other):
        other = self.convert(other)
        return PrimitiveAlgebra((MUL, (self, other)))
    def __rmul__(self, other):
        other = self.convert(other)
        return PrimitiveAlgebra((MUL, (other, self)))
    def __div__(self, other):
        other = self.convert(other)
        return PrimitiveAlgebra((DIV, (self, other)))
    def __rdiv__(self, other):
        other = self.convert(other)
        return PrimitiveAlgebra((DIV, (other, self)))
    def __pow__(self, other):
        other = self.convert(other)
        return PrimitiveAlgebra((POW, (self, other)))
    def __rpow__(self, other):
        other = self.convert(other)
        return PrimitiveAlgebra((POW, (other, self)))
    __truediv__ = __div__
    __rtruediv__ = __rdiv__


########### string to PrimitiveAlgebra parser ############

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
compare_map = {'<':LT, '>':GT, '<=':LT, '>=':GE,
               '==':EQ, '!=':NE}

class PrimitiveWalker:

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
        self.append(PrimitiveAlgebra((head, tuple(lst))))
    # for atomic instance:
    def add(self, obj):
        self.append(PrimitiveAlgebra(obj))

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
        self.add((SYMBOL, node.name))

    def visitConst(self, node):
        self.add((NUMBER, node.value))

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

def string2PrimitiveAlgebra(expr):
    """ Parse string expr to PrimitiveAlgebra.
    """
    node = compiler.parse(expr)
    return compiler.walk(node, PrimitiveWalker()).stack.pop()
