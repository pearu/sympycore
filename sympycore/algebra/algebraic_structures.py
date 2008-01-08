
from ..core import Basic, classes, objects, sympify
from ..core.sexpr import SYMBOLIC, NUMBER, TERMS, FACTORS


class AlgebraicStructure(Basic):
    """ Represents an element of an algebraic structure.
    Subclasses will define operations between elements if any.
    """

class BasicAlgebra(AlgebraicStructure):
    """ Collects implementation specific methods of algebra classes.
    
    They must be all compatible with PrimitiveAlgebra class via
    defining as_PrimitiveAlgebra and from_PrimitiveAlgebra methods.

    Recommended way to construct + and * operation results is to
    define Add, Mul, Pow static methods which are used by default
    __add__, __mul__ etc methods.
    """

    def as_PrimitiveAlgebra(self):
        raise NotImplementedError('%s must define as_PrimitiveAlgebra method'\
                                  % (type(self).__name__))

    def from_PrimitiveAlgebra(self):
        raise NotImplementedError('%s must define from_PrimitiveAlgebra method'\
                                  % (type(self).__name__))

    def __str__(self):
        return str(self.as_PrimitiveAlgebra())

    @staticmethod
    def Add(seq):
        raise NotImplementedError('BasicAlgebra subclass must define staticmethod Add')

    @staticmethod
    def Mul(seq):
        raise NotImplementedError('BasicAlgebra subclass must define staticmethod Mul')

    @staticmethod
    def Pow(base, exponent):
        raise NotImplementedError('BasicAlgebra subclass must define staticmethod Pow')

    def __pos__(self):
        return self

    def __neg__(self):
        return self.Mul([self, -1])

    #XXX: need to deal with other algebras where self is a number, should return NotImplemented
    def __add__(self, other):
        return self.Add([self, other])

    def __radd__(self, other):
        return self.Add([other, self])

    def __sub__(self, other):
        return self + (-other)

    def __rsub__(self, other):
        return other + (-self)

    def __mul__(self, other):
        return self.Mul([self, other])

    def __rmul__(self, other):
        return self.Mul([other, self])

    def __div__(self, other):
        return self.Mul([self, self.Pow(other,-1)])

    def __rdiv__(self, other):
        return self.Mul([other, self.Pow(self,-1)])

    def __pow__(self, other):
        return self.Pow(self, other)

    def __rpow__(self, other):
        return self.Pow(other, self)

    __truediv__ = __div__
    __rtruediv__ = __rdiv__


class CommutativeRing(AlgebraicStructure):
    """ Represents an element of a commutative ring and defines binary
    operations +, *, -.
    """

class CommutativeAlgebra(AlgebraicStructure):
    """ Represents an element of a commutative algebra and defines
    binary operations +, *, -, /, **.
    """


##############################################################

class PolynomialAlgebra(AlgebraicStructure):
    """ Represents a polynomial.
    """

class PolynomialAlgebra(AlgebraicStructure):
    """ Represents a polynomial function.
    """

    def __new__(cls, obj, symbols, coefficient_symbols=[]):
        o = object.__new__(cls)
        o.coefficient_symbols = coefficient_symbols
        if len(symbols)==1:
            o.data = (UnivariatePolynomialAlgebra(obj), symbols)
        else:
            o.data = (MultivariatePolynomialAlgebra(obj), symbols)
        return o
