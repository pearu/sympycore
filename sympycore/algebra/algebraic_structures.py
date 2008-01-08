
from ..core import Basic, classes, objects, sympify
from ..core.sexpr import SYMBOLIC, NUMBER, TERMS, FACTORS
from .pairs import CommutativePairs

class AlgebraicStructure(Basic):
    """ Represents an element of an algebraic structure.
    Subclasses will define operations between elements.
    """

class CommutativeRing(AlgebraicStructure):
    """ Represents an element of a commutative ring and defines binary
    operations +, *, -.
    """

class CommutativeAlgebra(AlgebraicStructure):
    """ Represents an element of a commutative algebra and defines
    binary operations +, *, -, /, **.
    """

######################################################################

class SymbolicAlgebra(CommutativeAlgebra):
    """ Represents an element of a symbolic algebra. The set of a
    symbolic algebra is a set of expressions. There are four kinds of
    expressions: Symbolic, SymbolicNumber, SymbolicTerms,
    SymbolicFactors.

    SymbolicAlgebra basically models the structure of SymPy.
    """

    def __new__(cls, obj, kind=None):
        if type(obj) is cls:
            return obj
        if kind is None:
            if isinstance(obj, cls):
                # XXX: need another way to specify coefficent and exponent algebras
                kind = NUMBER
            elif isinstance(obj, (int, long, float, complex)):
                obj = sympify(obj)
                kind = NUMBER
            else:
                kind = SYMBOLIC

        if kind is SYMBOLIC:
            return Symbolic(obj)
        if kind is NUMBER:
            return SymbolicNumber(obj)
        if kind is TERMS:
            return SymbolicTerms(obj)
        if kind is FACTORS:
            return SymbolicFactors(obj)
        return NotImplementedError(`cls, obj, kind`)

class Symbolic(SymbolicAlgebra):
    
    def __new__(cls, obj):
        o = object.__new__(cls)
        o.data = obj
        return o

class SymbolicNumber(SymbolicAlgebra):
    
    def __new__(cls, obj):
        o = object.__new__(cls)
        o.data = obj
        return o

class SymbolicTerms(CommutativePairs, SymbolicAlgebra):
    
    pass

class SymbolicFactors(CommutativePairs, SymbolicAlgebra):
    
    pass


##############################################################

class PolynomialAlgebra(CommutativePairs, AlgebraicStructure):
    """ Represents a polynomial.
    """

class SymbolicPolynomialAlgebra(AlgebraicStructure):
    """ Represents a polynomial function.
    """

    def __new__(cls, obj, symbols):
        o = object.__new__(cls)
        o.data = (PolynomialAlgebra(obj), symbols)
        return o
