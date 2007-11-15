
from ..core import Atom, Basic, sympify, classes, objects
from ..core.utils import singleton
from .basic import BasicArithmetic

__all__ = ['MathematicalSymbol', 'EulersNumber', 'Pi', 'GoldenRation',
           'EulerConstant', 'Feigenbaum1', 'Feigenbaum2',
           'NaN', 'Infinity', 'ComplexInfinity', 'ImaginaryUnit',
           'initialize_constants'
           ]

def initialize_constants():
    """Creates singletion instances of MathematicalSymbol classes.
    """
    EulersNumber()
    Pi()
    GoldenRatio()
    EulerConstant()
    Feigenbaum1()
    Feigenbaum2()
    NaN()
    Infinity()
    ComplexInfinity()
    ImaginaryUnit()
    
class MathematicalSymbol(BasicArithmetic, Atom):
    """Base class to various mathematical symbols and constants
    for which arithmetic operations are defined.
    """

    @singleton
    def __new__(cls):
        obj = object.__new__(cls)
        setattr(objects, obj.tostr(), obj)
        return obj

    def __eq__(self, other):
        if sympify(other) is self: return True
        return False

class EulersNumber(MathematicalSymbol):
    """Euler's number e=2.71828182845904523536...

    Reference:
      http://en.wikipedia.org/wiki/E_(mathematical_constant)
    """

    def tostr(self, level=0):
        return 'E'

    def evalf(self, precision=None):
        return classes.Float(1, precision).evalf_exp()

    def try_power_(self, other):
        return classes.Exp(other)

class Pi(MathematicalSymbol):
    """Circular constant pi=3.14159265358979323846...

    Reference:
      http://en.wikipedia.org/wiki/Pi
    """

    def tostr(self, level=0):
        return "pi"

    def evalf(self, precision=None):
        return classes.Float.evalf_pi(precision)

class GoldenRatio(MathematicalSymbol):
    """Golden ratio phi=1.6180339887498948482...

    Reference:
      http://en.wikipedia.org/wiki/Golden_ratio
    """

    def tostr(self, level=0):
        return 'phi'

    def evalf(self, precision=None):
        return (classes.Float(5).evalf_sqrt(precision)+1)/2

class EulerConstant(MathematicalSymbol):
    """Euler-Masheroni constant gamma=0.5772156649015328606...

    Reference:
      http://en.wikipedia.org/wiki/Euler-Mascheroni_constant
    """

    def tostr(self, level=0):
        return 'gamma'

    def evalf(self, precision=None):
        return classes.Float.evalf_gamma(precision)

class Feigenbaum1(MathematicalSymbol):
    """Feigenbaum's first constant alpha=4.66920160910299067185...
    
    Reference:
      http://en.wikipedia.org/wiki/Feigenbaum_constants
    """
    def tostr(self, level=0):
        return 'alpha'


class Feigenbaum2(MathematicalSymbol):
    """Feigenbaum's second constant delta=2.50290787509589282228...
    
    Reference:
      http://en.wikipedia.org/wiki/Feigenbaum_constants
    """
    def tostr(self, level=0):
        return 'delta'

class NaN(MathematicalSymbol):
    """Not-a-Number nan.
    """

    def tostr(self, level=0):
        return 'nan'

    def try_power(self, other):
        if other.is_zero:
            return objects.one
        return self

class Infinity(MathematicalSymbol):
    """Positive infinity oo.

    Reference:
      http://en.wikipedia.org/wiki/Infinity
      http://en.wikipedia.org/wiki/Extended_real_number_line
      http://en.wikipedia.org/wiki/Real_projective_line
    """

    def tostr(self, level=0):
        return 'oo'

    def try_power(self, other):
        if other.is_NaN:
            return other
        if other.is_Number:
            if other.is_zero:
                return objects.one
            if other.is_one:
                return
            if other.is_positive:
                return self
            if other.is_negative:
                return objects.zero
        if other.is_Infinity:
            return self
        if other==-self:
            return objects.zero


class ComplexInfinity(MathematicalSymbol):
    """Complex infinity zoo.

    Reference:
      http://en.wikipedia.org/wiki/Riemann_sphere
    """

    def tostr(self, level=0):
        return 'zoo'

    def try_power(self, other):
        if other.is_NaN:
            return other
        if other.is_Number:
            if other.is_zero:
                return objects.one
            if other.is_positive:
                return self
            if other.is_negative:
                return objects.zero

class ImaginaryUnit(MathematicalSymbol):
    """Positive imaginary unit I = Sqrt(-1).

    Reference:
      http://en.wikipedia.org/wiki/Imaginary_unit
    """

    def tostr(self, level=0):
        return 'I'

    def try_power(self, other):
        if other.is_Integer:
            if other.is_one:
                # nothing to evaluate
                return
            e = other.p % 4
            if e==0: return objects.one
            if e==1: return objects.I
            if e==2: return -objects.one
            return -objects.I
        return

    def __eq__(self, other):
        other = sympify(other)
        if other is self: return True
        return False

    def __hash__(self):
        return hash(self.__class__)
