
from .algebra import Calculus, I
from .functions import sin, cos, tan, cot, pi

Symbol = Calculus.Symbol
Number = Calculus.Number

Add = lambda *args: Calculus.Add(*map(Calculus.convert, args))
Mul = lambda *args: Calculus.Mul(*map(Calculus.convert, args))
Pow = lambda *args: Calculus.Pow(*map(Calculus.convert, args))
