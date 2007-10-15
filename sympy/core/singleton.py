
from utils import memoizer_immutable_args
from basic import Atom, Basic, sympify
from methods import ArithMeths#, RelationalMeths

class NumberSymbol(ArithMeths, Atom):

    @memoizer_immutable_args('NumberSymbol.__new__')
    def __new__(cls):
        return object.__new__(cls)

    def __eq__(self, other):
        other = sympify(other)
        if other is self: return True
        return False

class ImaginaryUnit(ArithMeths, Atom):

    @memoizer_immutable_args('ImaginaryUnit.__new__')
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

class Exp1(NumberSymbol):

    def tostr(self, level=0):
        return 'E'

    def evalf(self):
        return Basic.exp(Float(1))

class Pi(NumberSymbol):

    def tostr(self, level=0):
        return "pi"



class GoldenRatio(NumberSymbol):

    def tostr(self, level=0):
        return 'GoldenRatio'

class EulerGamma(NumberSymbol):

    def tostr(self, level=0):
        return 'EulerGamma'

class Catalan(NumberSymbol):

    def tostr(self, level=0):
        return 'Catalan'


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

I = ImaginaryUnit()
nan = NaN()
oo = Infinity()
zoo = ComplexInfinity()
E = Exp1()
pi = Pi()

Basic.nan = nan
Basic.oo = oo
Basic.zoo = zoo
Basic.E = E
Basic.I = I
Basic.pi = pi

Basic.predefined_objects.update(
    pi = pi,
    nan = nan,
    oo = oo,
    zoo = zoo,
    E = E,
    I = I,
    )
