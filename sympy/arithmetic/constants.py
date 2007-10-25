
from ..core import Atom, Basic, sympify
from ..core.utils import singleton
from .methods import ArithmeticMethods

class NumberSymbol(ArithmeticMethods, Atom):

    @singleton
    def __new__(cls):
        return object.__new__(cls)

    def __eq__(self, other):
        other = sympify(other)
        if other is self: return True
        return False

class Exp1(NumberSymbol):

    def tostr(self, level=0):
        return 'E'

    def evalf(self, precision=None):
        return Basic.Float(1, precision).evalf_exp()

class Pi(NumberSymbol):

    def tostr(self, level=0):
        return "pi"

    def evalf(self, precision=None):
        return Basic.Float.evalf_pi(precision)

class GoldenRatio(NumberSymbol):

    def tostr(self, level=0):
        return 'GoldenRatio'

    def evalf(self, precision=None):
        return (Basic.Float(5).evalf_sqrt(precision)+1)/2

class EulerGamma(NumberSymbol):

    def tostr(self, level=0):
        return 'EulerGamma'

    def evalf(self, precision=None):
        return Basic.Float.evalf_gamma(precision)

class NaN(NumberSymbol):

    def tostr(self, level=0):
        return 'nan'

    def try_power(self, other):
        if other.is_zero:
            return Basic.one
        return self

class Infinity(NumberSymbol):

    def tostr(self, level=0):
        return 'oo'

    def try_power(self, other):
        if other.is_NaN:
            return other
        if other.is_Number:
            if other.is_zero:
                return Basic.one
            if other.is_one:
                return
            if other.is_positive:
                return self
            if other.is_negative:
                return Basic.zero
        if other.is_Infinity:
            return self
        if other==-self:
            return Basic.zero


class ComplexInfinity(NumberSymbol):

    def tostr(self, level=0):
        return 'zoo'

    def try_power(self, other):
        if other.is_NaN:
            return other
        if other.is_Number:
            if other.is_zero:
                return Basic.one
            if other.is_positive:
                return self
            if other.is_negative:
                return Basic.zero

class ImaginaryUnit(ArithmeticMethods, Atom):

    @singleton
    def __new__(cls):
        return object.__new__(cls)

    def tostr(self, level=0):
        return 'I'

    def try_power(self, other):
        if other.is_Integer:
            if other.is_one:
                # nothing to evaluate
                return
            e = other.p % 4
            if e==0: return Basic.one
            if e==1: return Basic.I
            if e==2: return -Basic.one
            return -Basic.I
        return

    def __eq__(self, other):
        other = sympify(other)
        if other is self: return True
        return False
