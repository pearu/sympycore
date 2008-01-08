
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
