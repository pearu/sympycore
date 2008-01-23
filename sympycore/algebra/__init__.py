
from .algebraic_structures import BasicAlgebra
from .primitive import PrimitiveAlgebra
from .pairs import CommutativeRingWithPairs
from .std_commutative_algebra import I, A, Calculus
from .integers import Integers

Symbol = A.Symbol
Number = A.Number

from numberlib import mpq, mpf, mpc, oo, moo, undefined, zoo
# a temporary convenience
#x,y,a,b = map(Symbol, 'xyab')
