
from ..core import Basic, classes, objects, sympify
from ..core.sexpr import SYMBOLIC, NUMBER, TERMS, FACTORS


class AlgebraicStructure(Basic):
    """ Represents an element of an algebraic structure.
    Subclasses will define operations between elements if any.
    """

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
