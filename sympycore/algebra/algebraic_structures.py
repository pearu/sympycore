
from ..core import Basic, classes, objects, sympify, BasicType

class AlgebraicStructure(Basic):
    """ Represents an element of an algebraic structure.
    Subclasses will define operations between elements if any.
    """

    @classmethod
    def convert(cls, obj):
        if isinstance(obj, cls):
            return obj
        if isinstance(obj, cls.coefficient_structure):
            return PrimitiveAlgebra(obj, kind=NUMBER)
        if isinstance(obj, AlgebraicStructure):
            return obj.as_primitive()
        return PrimitiveAlgebra(obj, kind=SYMBOL)

    def as_primitve(self):
        raise NotImplementedError('%s must define as_primitive method'\
                                  % (type(self).__name__))

    def __str__(self):
        return str(self.as_primitive())

class BasicRing(AlgebraicStructure):
    """
    """

class BasicAlgebra(AlgebraicStructure):
    """ Collects implementation specific methods of algebra classes.
    
    They must be all compatible with PrimitiveAlgebra class via
    defining as_primitive method.

    The recommended way to construct + and * operation results is to
    define Add, Mul, Pow static methods which are used by default
    __add__, __mul__ etc methods.
    """

    def as_algebra(self, cls, source=None):
        """
        """
        # XXX: cache primitive algebras
        if cls is classes.PrimitiveAlgebra:
            return self.as_primitive()
        return self.as_primitive().as_algebra(cls, source=self)

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
        other = self.convert(other)
        return self.Add([self, other])

    def __radd__(self, other):
        other = self.convert(other)
        return self.Add([other, self])

    def __sub__(self, other):
        other = self.convert(other)
        return self + (-other)

    def __rsub__(self, other):
        other = self.convert(other)
        return other + (-self)

    def __mul__(self, other):
        other = self.convert(other)
        return self.Mul([self, other])

    def __rmul__(self, other):
        other = self.convert(other)
        return self.Mul([other, self])

    def __div__(self, other):
        other = self.convert(other)
        return self.Mul([self, self.Pow(other,-1)])

    def __rdiv__(self, other):
        other = self.convert(other)
        return self.Mul([other, self.Pow(self,-1)])

    def __pow__(self, other):
        other = self.convert(other)
        return self.Pow(self, other)

    def __rpow__(self, other):
        other = self.convert(other)
        return self.Pow(other, self)

    __truediv__ = __div__
    __rtruediv__ = __rdiv__


class StructureGenerator(BasicType):
    
    def __new__(cls, parameters, **kwargs):
        name = '%s(%s, %s)' % (cls.__name__, ', '.join(map(str, parameters)), kwargs)
        bases = (AlgebraicStructure,)
        attrdict = dict(parameters = parameters, **kwargs)
        cls = type.__new__(cls, name, bases, attrdict)
        return cls

class PolynomialGenerator(StructureGenerator):

    def __new__(cls, symbols, coeff_structure=None):
        if coeff_structure is None:
            coeff_structure = classes.IntegerRing
        return StructureGenerator.__new__(cls, symbols,
                                          coeff_structure=coeff_structure)

##############################################################
# These are ideas:

class CommutativeRing(AlgebraicStructure):
    """ Represents an element of a commutative ring and defines binary
    operations +, *, -.
    """

class CommutativeAlgebra(AlgebraicStructure):
    """ Represents an element of a commutative algebra and defines
    binary operations +, *, -, /, **.
    """

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
