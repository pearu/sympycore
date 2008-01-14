
from ..core import sympify, classes
from .pairs import CommutativePairs
from .algebraic_structures import BasicAlgebra
from .primitive import PrimitiveAlgebra, SYMBOL, NUMBER, ADD, MUL

from .pairs import (CommutativePairs, PairsCommutativeRing, CommutativeTerms,
                    CommutativeFactors, PairsCommutativeSymbol, PairsNumber)

class StandardCommutativeAlgebra(PairsCommutativeRing):
    """ Represents an element of a symbolic algebra. The set of a
    symbolic algebra is a set of expressions. There are four kinds of
    expressions: Symbolic, SymbolicNumber, SymbolicTerms,
    SymbolicFactors.

    StandardCommutativeAlgebra basically models the structure of SymPy.
    """

    @staticmethod
    def Pow(base, exp):
        return SymbolicFactors({base:exp})

class Symbolic(PairsCommutativeSymbol, StandardCommutativeAlgebra): # rename to Symbol?

    def __hash__(self):
        return hash((type(self), self.data))

class SymbolicNumber(PairsNumber, StandardCommutativeAlgebra): # rename to Number?

    def __hash__(self):
        return hash((type(self), self.value))
        
class SymbolicTerms(CommutativeTerms, StandardCommutativeAlgebra):

    __str__ = StandardCommutativeAlgebra.__str__

class SymbolicFactors(CommutativeFactors, StandardCommutativeAlgebra):

    __str__ = StandardCommutativeAlgebra.__str__

one = SymbolicNumber(1)
zero = SymbolicNumber(0)

StandardCommutativeAlgebra.one = one
StandardCommutativeAlgebra.zero = zero
StandardCommutativeAlgebra.algebra_class = StandardCommutativeAlgebra
StandardCommutativeAlgebra.algebra_numbers = (int, long, float)
StandardCommutativeAlgebra.element_classes = {\
    SYMBOL: Symbolic,
    NUMBER: SymbolicNumber,
    ADD: SymbolicTerms,
    MUL: SymbolicFactors
    }

