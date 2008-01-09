from __future__ import absolute_import
import types
import compiler

from .algebraic_structures import AlgebraicStructure

NUMBER = intern('N')
SYMBOL = intern('S')
ADD = intern('+')
SUB = intern('-')
MUL = intern('*')
DIV = intern('/')
POW = intern('**')


class PrimitiveAlgebra(AlgebraicStructure):

    def __new__(cls, tree):
        if hasattr(tree, 'as_PrimitiveAlgebra'):
            tree = tree.as_PrimitiveAlgebra()
        if isinstance(tree, str): # XXX: unicode
            tree = string2PrimitiveAlgebra(tree)
        if isinstance(tree, cls):
            return tree
        if not isinstance(tree, tuple):
            tree = (SYMBOL, tree)
        obj = object.__new__(cls)
        obj.tree = tree
        return obj

    def __repr__(self):
        return str(self.tree)

    def __str__(self):
        head, rest = self.tree
        if head is NUMBER or head is SYMBOL:
            return str(rest)
        l = []
        for t in rest:
            l.append(str(t))
        return head.join(l)

    def __eq__(self, other):
        if type(other) is PrimitiveAlgebra:
            return self.tree == other.tree
        return self.tree == other

    def __hash__(self):
        return hash(self.tree)

    def __add__(self, other): return PrimitiveAlgebra((ADD, (self, other)))
    def __radd__(self, other): return PrimitiveAlgebra((ADD, (other, self)))
    def __sub__(self, other): return PrimitiveAlgebra((SUB, (self, other)))
    def __rsub__(self, other): return PrimitiveAlgebra((SUB, (other, self)))
    def __mul__(self, other): return PrimitiveAlgebra((MUL, (self, other)))
    def __rmul__(self, other): return PrimitiveAlgebra((MUL, (other, self)))
    def __div__(self, other): return PrimitiveAlgebra((DIV, (self, other)))
    def __rdiv__(self, other): return PrimitiveAlgebra((DIV, (other, self)))
    def __pow__(self, other): return PrimitiveAlgebra((POW, (self, other)))
    def __rpow__(self, other): return PrimitiveAlgebra((POW, (other, self)))
    __truediv__ = __div__
    __rtruediv__ = __rdiv__


########### string to PrimitiveAlgebra parser ############

node_names = []
skip_names = ['Module','Stmt','Discard']
Node = compiler.ast.Node
for n, cls in compiler.ast.__dict__.items():
    if n in skip_names:
        continue
    if isinstance(cls, (type,types.ClassType)) and issubclass(cls, Node):
        node_names.append(n)

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
            lst = stack[-1]
            if isinstance(lst[1], list):
                lst[1].append(obj)
            else:
                print "Cannot append %r to %s" % (obj, lst)
    def end(self):
        last = self.stack.pop()
        print last
        head, lst = last
        self.append(PrimitiveAlgebra((head, tuple(lst))))
    # for atomic instance:
    def add(self, obj):
        self.append(PrimitiveAlgebra(obj))

    for _n in node_names:
        exec '''\
def visit%s(self, node, *args):
    print "warning: using default visit%s"
    self.start(%r)
    for child in node.getChildNodes():
        self.visit(child, *args)
    self.end()
''' % (_n, _n, _n)

    # visitNode methods:
    def visitName(self, node):
        self.add((SYMBOL, node.name))

    def visitConst(self, node):
        self.add((NUMBER, node.value))

    def visitAdd(self, node):
        self.start(ADD)
        self.visit(node.left)
        self.visit(node.right)
        self.end()
    def visitMul(self, node):
        self.start(MUL)
        self.visit(node.left)
        self.visit(node.right)
        self.end()

def string2PrimitiveAlgebra(expr):
    node = compiler.parse(expr)
    return compiler.walk(node, PrimitiveWalker()).stack.pop()
