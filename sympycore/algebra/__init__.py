
from .algebraic_structures import AlgebraicStructure
from .primitive import PrimitiveAlgebra
from .std_commutative_algebra import StandardCommutativeAlgebra, I
#from .pairs import CommutativePairs

from .integers import Integers

Symbol = StandardCommutativeAlgebra.Symbol
Number = StandardCommutativeAlgebra.Number

# a temporary convenience
x,y,a,b = map(Symbol, 'xyab')
