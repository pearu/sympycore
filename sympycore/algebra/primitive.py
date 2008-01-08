
from .algebraic_structures import AlgebraicStructure

class PrimitiveAlgebra(AlgebraicStructure):

    def __new__(cls, tree):
        if hasattr(tree, 'as_PrimitiveAlgebra'):
            tree = tree.as_PrimitiveAlgebra()
        if isinstance(tree, cls):
            return tree
        obj = object.__new__(cls)
        obj.tree = tree
        return obj

    def __repr__(self):
        return str(self.tree)

    def __eq__(self, other):
        if type(other) is PrimitiveAlgebra:
            return self.tree == other.tree
        return self.tree == other

    def __hash__(self):
        return hash(self.tree)

    def __add__(self, other): return PrimitiveAlgebra(('+', self, other))
    def __radd__(self, other): return PrimitiveAlgebra(('+', other, self))
    def __sub__(self, other): return PrimitiveAlgebra(('-', self, other))
    def __rsub__(self, other): return PrimitiveAlgebra(('-', other, self))
    def __mul__(self, other): return PrimitiveAlgebra(('*', self, other))
    def __rmul__(self, other): return PrimitiveAlgebra(('*', other, self))
    def __div__(self, other): return PrimitiveAlgebra(('/', self, other))
    def __rdiv__(self, other): return PrimitiveAlgebra(('/', other, self))
    def __pow__(self, other): return PrimitiveAlgebra(('**', self, other))
    def __rpow__(self, other): return PrimitiveAlgebra(('**', other, self))
    __truediv__ = __div__
    __rtruediv__ = __rdiv__
