
from .algebra import Calculus, I, integrate, oo, undefined, moo, zoo
from .functions import exp, log, sqrt, sin, cos, tan, cot, pi, E

Symbol = Calculus.Symbol

def Number(num, denom=None):
    n = Calculus.Number(Calculus.convert_coefficient(num))
    if denom is None:
        return n
    return n / denom

def Rational(num, denom):
    #XXX: use Div
    return Calculus.Number(Calculus.convert_coefficient(num)) / denom

Add = lambda *args: Calculus.Add(*map(Calculus.convert, args))
Mul = lambda *args: Calculus.Mul(*map(Calculus.convert, args))
Pow = lambda *args: Calculus.Pow(*map(Calculus.convert, args))

from ..arithmetic.number_theory import factorial as _factorial
def factorial(n):
    return Number(_factorial(n))
    
