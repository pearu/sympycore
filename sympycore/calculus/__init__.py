
from .algebra import Calculus, I, integrate, oo, undefined
from .functions import exp, log, sqrt, sin, cos, tan, cot, pi, E

Symbol = Calculus.Symbol
Number = Calculus.Number

Add = lambda *args: Calculus.Add(*map(Calculus.convert, args))
Mul = lambda *args: Calculus.Mul(*map(Calculus.convert, args))
Pow = lambda *args: Calculus.Pow(*map(Calculus.convert, args))
