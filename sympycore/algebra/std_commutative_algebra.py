
from ..core import sympify, classes
from .pairs import CommutativePairs
from .algebraic_structures import BasicAlgebra
from .primitive import PrimitiveAlgebra, SYMBOL, NUMBER, ADD, MUL

#from .pairs import (CommutativePairs, PairsCommutativeRing, CommutativeTerms,
#                    CommutativeFactors, PairsCommutativeSymbol, PairsNumber)

from .pairs import CommutativeRingWithPairs

from .numberlib import mpq, mpc

class StandardCommutativeAlgebra(CommutativeRingWithPairs):
    """ Represents an element of a symbolic algebra. The set of a
    symbolic algebra is a set of expressions. There are four kinds of
    expressions: Symbolic, SymbolicNumber, SymbolicTerms,
    SymbolicFactors.

    StandardCommutativeAlgebra basically models the structure of SymPy.
    """

    __slots__ = ['head', 'data', '_hash', 'one', 'zero']
    _hash = None
    
    @classmethod
    def Number(cls, num, denom=None):
        if denom is None:
            return cls(num, head=NUMBER)
        return cls(mpq(num, denom), head=NUMBER)

    @classmethod
    def Symbol(cls, obj):
        return cls(obj, head=SYMBOL)

    @classmethod
    def Pow(cls, base, exp):
        if exp is -1 and base.head is NUMBER:
            return cls.Number(mpq(1, base.data))
        if exp == 0:
            return cls.one
        if exp == 1 or cls.one==base:
            return base
        return cls({base:exp}, head=MUL)

one = StandardCommutativeAlgebra(1, head=NUMBER)
zero = StandardCommutativeAlgebra(0, head=NUMBER)
I = StandardCommutativeAlgebra(mpc(0,1), head=NUMBER)

StandardCommutativeAlgebra.one = one
StandardCommutativeAlgebra.zero = zero
StandardCommutativeAlgebra.algebra_class = StandardCommutativeAlgebra
StandardCommutativeAlgebra.algebra_numbers = (int, long, float, mpq)
