class Primitive:
    def __init__(self, tree):
        if isinstance(tree, Primitive):
            return tree
        self.tree = tree

    def __repr__(self):
        return str(self.tree)

    def __eq__(self, other):
        if isinstance(other, Primitive):
            return self.tree == other.tree
        return self.tree == other

    def __hash__(self):
        return hash(self.tree)

    def __add__(self, other): return Primitive(('+', self, other))
    def __radd__(self, other): return Primitive(('+', other, self))
    def __sub__(self, other): return Primitive(('-', self, other))
    def __rsub__(self, other): return Primitive(('-', other, self))
    def __mul__(self, other): return Primitive(('*', self, other))
    def __rmul__(self, other): return Primitive(('*', other, self))
    def __div__(self, other): return Primitive(('/', self, other))
    def __rdiv__(self, other): return Primitive(('/', other, self))
    def __pow__(self, other): return Primitive(('**', self, other))
    def __rpow__(self, other): return Primitive(('**', other, self))
    __truediv__ = __div__
    __rtruediv__ = __rdiv__
