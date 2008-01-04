
from ..core import Atom, Basic, sympify, classes, objects
from ..core.utils import singleton
from ..core.sexpr import NANINF, IMAGUNIT, NUMBER
from .basic import BasicArithmetic

__all__ = ['MathematicalSymbol', 'MathematicalNumber',
           'EulersNumber', 'Pi', 'GoldenRation',
           'EulerConstant', 'Feigenbaum1', 'Feigenbaum2',
           'NaN', 'Infinity', 'ComplexInfinity', 'ImaginaryUnit',
           'initialize_constants', 'NegativeInfinity'
           ]

constant_classes = None # defined at the end of this file
naninf_classes = None   # defined at the end of this file

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
    NegativeInfinity()
    ComplexInfinity()
    ImaginaryUnit()
    
class MathematicalSymbol(BasicArithmetic, Atom):
    """Base class to various mathematical symbols and constants
    for which arithmetic operations are defined.
    """

    @singleton
    def __new__(cls):
        obj = object.__new__(cls)
        n = obj.tostr()
        if n=='-oo':
            setattr(objects, 'moo', obj)
        else:
            setattr(objects, n, obj)
        return obj

    def try_power(self, other):
        if isinstance(other, NaN) or isinstance(other, Infinity):
            return other
        if other==objects.moo:
            return objects.zero

    def try_derivative(self, v):
        return objects.zero

    def try_antiderivative(self, s):
        return self * s

    def __call__(self, *args):
        """ Mathematical symbol is a constant function.
        (s)(x) -> s
        """
        return self

class MathematicalNumber(MathematicalSymbol):
    """ Base class for number symbols E, Pi, etc.
    """
    def __eq__(self, other):
        return self is sympify(other)
    def __ne__(self, other):
        return self is not sympify(other)
    def __lt__(self, other):
        other = sympify(other)
        if self is other:
            return False
        if isinstance(other, classes.Number):
            r = self.get_containing_range()
            if other <= r[0]:
                return False
            if other >= r[1]:
                return True
            # XXX need to get smaller range
        return NotImplemented
    def __gt__(self, other):
        other = sympify(other)
        if self is other:
            return False
        if isinstance(other, classes.Number):
            r = self.get_containing_range()
            if other <= r[0]:
                return True
            if other >= r[1]:
                return False
            # XXX need to get smaller range
        return NotImplemented

class EulersNumber(MathematicalNumber):
    """Euler's number e=2.71828182845904523536...

    Reference:
      http://en.wikipedia.org/wiki/E_(mathematical_constant)
    """
    is_positive = True
    is_negative = False

    def tostr(self, level=0):
        return 'E'

    def evalf(self, precision=None):
        return classes.Float(1, precision).evalf_exp()

    def get_containing_range(self):
        return (2,3)

class Pi(MathematicalNumber):
    """Circular constant pi=3.14159265358979323846...

    Reference:
      http://en.wikipedia.org/wiki/Pi
    """
    is_positive = True
    is_negative = False

    def tostr(self, level=0):
        return "pi"

    def evalf(self, precision=None):
        return classes.Float.evalf_pi(precision)

    def get_containing_range(self):
        return (3,4)

class GoldenRatio(MathematicalNumber):
    """Golden ratio phi=1.6180339887498948482...

    Reference:
      http://en.wikipedia.org/wiki/Golden_ratio
    """
    is_positive = True
    is_negative = False

    def tostr(self, level=0):
        return 'phi'

    def evalf(self, precision=None):
        return (classes.Float(5).evalf_sqrt(precision)+1)/2

    def get_containing_range(self):
        return (1,2)

class EulerConstant(MathematicalNumber):
    """Euler-Masheroni constant gamma=0.5772156649015328606...

    Reference:
      http://en.wikipedia.org/wiki/Euler-Mascheroni_constant
    """
    is_positive = True
    is_negative = False

    def tostr(self, level=0):
        return 'gamma'

    def evalf(self, precision=None):
        return classes.Float.evalf_gamma(precision)

    def get_containing_range(self):
        return (0,1)

class Feigenbaum1(MathematicalNumber):
    """Feigenbaum's first constant alpha=4.66920160910299067185...
    
    Reference:
      http://en.wikipedia.org/wiki/Feigenbaum_constants
    """
    is_positive = True
    is_negative = False
    
    def tostr(self, level=0):
        return 'alpha'

    def get_containing_range(self):
        return (4,5)

class Feigenbaum2(MathematicalNumber):
    """Feigenbaum's second constant delta=2.50290787509589282228...
    
    Reference:
      http://en.wikipedia.org/wiki/Feigenbaum_constants
    """
    is_positive = True
    is_negative = False
    def tostr(self, level=0):
        return 'delta'

    def get_containing_range(self):
        return (2,3)

class NaN(MathematicalSymbol):
    """Not-a-Number nan.
    """

    def tostr(self, level=0):
        return 'nan'

    def try_power(self, other):
        if other.is_zero:
            return objects.one
        return self

    def as_sexpr(self):
        return (NUMBER, self)

    def __pos__(self):
        return self
    __neg__ = __abs__ = __pos__

    def __add__(self, other):
        other = sympify(other)
        if isinstance(other, constant_classes + naninf_classes):
            return self
        return NotImplemented
    __mul__ = __div__ = __sub__ = __add__

    def __pow__(self, other):
        other = sympify(other)
        if isinstance(other, constant_classes):
            if other is objects.zero:
                return objects.one
            return self
        return NotImplemented

    def __radd__(self, other):
        if isinstance(other, Basic):
            if isinstance(other, constant_classes + naninf_classes):
                return self
            return classes.Add(other, self)
        return sympify(other) + self
    
    def __rsub__(self, other):
        if isinstance(other, Basic):
            if isinstance(other, constant_classes + naninf_classes):
                return self
            return classes.Add(other, -self)
        return sympify(other) - self

    def __rmul__(self, other):
        if isinstance(other, Basic):
            if isinstance(other, constant_classes + naninf_classes):
                return self
            return classes.Mul(other, self)
        return sympify(other) * self

    def __rdiv__(self, other):
        if isinstance(other, Basic):
            if isinstance(other, constant_classes + naninf_classes):
                return self
            return classes.Mul(other, objects.one/self)
        return sympify(other) / self

    def __rpow__(self, other):
        if isinstance(other, Basic):
            if isinstance(other, constant_classes + naninf_classes):
                return self
            return classes.Pow(other, self)
        return sympify(other) ** self

class Infinity(MathematicalSymbol):
    """Positive infinity oo.

    Reference:
      http://en.wikipedia.org/wiki/Infinity
      http://en.wikipedia.org/wiki/Extended_real_number_line
      http://en.wikipedia.org/wiki/Real_projective_line
    """
    is_positive = True
    is_negative = False

    def tostr(self, level=0):
        return 'oo'

    def try_power(self, other):
        if isinstance(other, NaN):
            return other
        if isinstance(other, classes.Number):
            if other.is_zero:
                return objects.one
            if other.is_one:
                return
            if other.is_positive:
                return self
            if other.is_negative:
                return objects.zero
        if isinstance(other, Infinity):
            return self
        if other==-self:
            return objects.zero

    def as_sexpr(self):
        return (NUMBER, self)

    def __pos__(self):
        return self

    __abs__ = __pos__

    def __neg__(self):
        return objects.moo

    def __add__(self, other):
        other = sympify(other)
        if isinstance(other, constant_classes):
            return self
        elif isinstance(other, MathematicalSymbol):
            if other is objects.oo:
                return self
            if other is objects.moo:
                return objects.nan
            if other is objects.zoo:
                return objects.nan # oo + zoo
        return NotImplemented

    def __sub__(self, other):
        other = sympify(other)
        if isinstance(other, constant_classes):
            return self
        elif isinstance(other, MathematicalSymbol):
            if other is objects.oo:
                return objects.nan
            if other is objects.moo:
                return objects.oo
            if other is objects.zoo:
                return objects.nan # oo + zoo
        return NotImplemented

    def __mul__(self, other):
        other = sympify(other)
        if isinstance(other, constant_classes):
            if other.is_positive:
                return self
            if other.is_negative:
                return objects.moo
            return objects.nan # oo * 0
        elif isinstance(other, MathematicalSymbol):
            if other is self:
                return self
            if other is objects.moo:
                return other
            if other is objects.nan:
                return other
            if other is objects.zoo:
                return other
        return NotImplemented

    def __div__(self, other):
        other = sympify(other)
        if isinstance(other, constant_classes):
            if other.is_positive:
                return self
            if other.is_negative:
                return objects.moo
            return objects.oo # oo/0
        elif isinstance(other, MathematicalSymbol):
            if other is self:
                return objects.nan # oo/oo
            if other is objects.moo:
                return objects.nan # oo/-oo
            if other is objects.zoo:
                return objects.nan # oo/zoo
            if other is objects.nan:
                return other
        return NotImplemented

    def __pow__(self, other):
        other = sympify(other)
        if isinstance(other, constant_classes):
            if other.is_positive:
                return self
            if other.is_negative:
                return objects.zero
            if other is objects.zero:
                return objects.one # oo ** 0
        elif isinstance(other, MathematicalSymbol):
            if other is self:
                return objects.oo # oo ** oo
            if other is objects.moo:
                return objects.zero # oo ** -oo
            if other is objects.nan:
                return other
            if other is objects.zoo:
                return objects.nan # oo ** zoo
        return NotImplemented

    def __radd__(self, other):
        if isinstance(other, Basic):
            obj = self + other
            if obj is NotImplemented:
                return classes.Add(other, self)
            return obj
        return sympify(other) + self

    def __rsub__(self, other):
        return objects.moo + other

    def __rmul__(self, other):
        if isinstance(other, Basic):
            obj = self * other
            if obj is NotImplemented:
                return classes.Mul(other, self)
            return obj
        return sympify(other) * self

    def __rdiv__(self, other): # other/oo
        if isinstance(other, Basic):
            if isinstance(other, constant_classes):
                return objects.zero
            elif isinstance(other, MathematicalSymbol):
                if other is objects.oo:
                    return objects.nan # oo/oo
                if other is objects.moo:
                    return objects.nan # -oo/oo
                if other is objects.zoo:
                    return objects.nan # zoo/oo
                if other is objects.nan:
                    return other
            return classes.Mul(other, objects.one/self)
        return sympify(other) / self

    def __rpow__(self, other): # other ** oo
        if isinstance(other, Basic):
            if isinstance(other, classes.Number):
                if abs(other)<objects.one:
                    return objects.zero
                if other is objects.one:
                    return objects.one # 1**oo
                if other.is_positive:
                    return objects.oo
                return objects.nan
            elif isinstance(other, constant_classes):
                if other.is_positive:
                    if other < 1:
                        return objects.zero
                    if other > 1:
                        return objects.oo
                # XXX: check for abs(other)<1 and return 0, otherwise returns oo or nan
                raise NotImplementedError(`self, other`)
            elif isinstance(other, MathematicalSymbol):
                if other is objects.oo:
                    return objects.oo # oo ** oo
                if other is objects.moo:
                    return objects.nan # (-oo) ** oo
                if other is objects.zoo:
                    return objects.zoo # zoo ** oo
                if other is objects.nan:
                    return other
            return classes.Pow(other, self, try_pow=False)
        return sympify(other) ** self

class NegativeInfinity(MathematicalSymbol):
    """Negative infinity -oo.

    Reference:
      http://en.wikipedia.org/wiki/Infinity
      http://en.wikipedia.org/wiki/Extended_real_number_line
      http://en.wikipedia.org/wiki/Real_projective_line
    """
    is_positive = False
    is_negative = True

    def tostr(self, level=0):
        return '-oo'

    def try_power(self, other):
        #XXX: todo
        pass

    def as_sexpr(self):
        return (NUMBER, self)

    def __pos__(self):
        return self
    def __neg__(self):
        return objects.oo
    __abs__ = __neg__

    def __add__(self, other):
        other = sympify(other)
        if isinstance(other, constant_classes):
            return self
        elif isinstance(other, MathematicalSymbol):
            if other is objects.oo:
                return objects.nan
            if other is objects.moo:
                return objects.moo
            if other is objects.zoo:
                return objects.nan # -oo + zoo
        return NotImplemented    

    def __sub__(self, other):
        other = sympify(other)
        if isinstance(other, constant_classes):
            return self
        elif isinstance(other, MathematicalSymbol):
            if other is objects.oo:
                return objects.moo
            if other is objects.moo:
                return objects.nan
            if other is objects.zoo:
                return objects.nan # -oo - zoo
        return NotImplemented    

    def __mul__(self, other):
        other = sympify(other)
        if isinstance(other, constant_classes):
            if other.is_positive:
                return self
            if other.is_negative:
                return objects.oo
            return objects.nan # -oo * 0
        elif isinstance(other, MathematicalSymbol):
            if other is self:
                return objects.oo
            if other is objects.moo:
                return self
            if other is objects.nan:
                return other
            if other is objects.zoo:
                return other
        return NotImplemented

    def __div__(self, other):
        other = sympify(other)
        if isinstance(other, constant_classes):
            if other.is_positive:
                return self
            if other.is_negative:
                return objects.oo
            return objects.moo # -oo/0
        elif isinstance(other, MathematicalSymbol):
            if other is self:
                return objects.nan # -oo/oo
            if other is objects.moo:
                return objects.nan # -oo/-oo
            if other is objects.zoo:
                return objects.nan # -oo/zoo
            if other is objects.nan:
                return other
        return NotImplemented

    def __pow__(self, other):
        other = sympify(other)
        if isinstance(other, constant_classes):
            if other.is_positive:
                return objects.oo * (-objects.one) ** other
            if other.is_negative:
                return objects.zero
            if other is objects.zero:
                return objects.one # (-oo) ** 0
        elif isinstance(other, MathematicalSymbol):
            if other is self:
                return objects.nan # (-oo) ** oo
            if other is objects.moo:
                return objects.zero # (-oo) ** -oo
            if other is objects.nan:
                return other
            if other is objects.zoo:
                return objects.nan # (-oo) ** zoo
        return NotImplemented

    def __radd__(self, other):
        if isinstance(other, Basic):
            obj = self + other
            if obj is NotImplemented:
                return classes.Add(other, self)
            return obj
        return sympify(other) + self

    def __rsub__(self, other):
        return objects.oo + other

    def __rmul__(self, other):
        return - (other * objects.oo)

    def __rdiv__(self, other): # other / -oo
        return - (other/objects.oo)

    def __rpow__(self, other): # other ** -oo
        return objects.one / (other ** objects.oo)

class ComplexInfinity(MathematicalSymbol):
    """Complex infinity zoo.

    Reference:
      http://en.wikipedia.org/wiki/Riemann_sphere
    """

    def tostr(self, level=0):
        return 'zoo'

    def try_power(self, other):
        if isinstance(other, NaN):
            return other
        if isinstance(other, classes.Number):
            if other.is_zero:
                return objects.one
            if other.is_positive:
                return self
            if other.is_negative:
                return objects.zero

    def as_sexpr(self):
        return (NUMBER, self)

    def __pos__(self):
        return self
    __abs__ = __neg__ = __pos__

    def __add__(self, other):
        other = sympify(other)
        if isinstance(other, constant_classes):
            return self
        elif isinstance(other, MathematicalSymbol):
            if other is objects.oo:
                return objects.nan # zoo + oo
            if other is objects.moo:
                return objects.nan
            if other is objects.zoo:
                return objects.nan # zoo + zoo
        return NotImplemented            

    __sub__ = __add__

    def __mul__(self, other):
        other = sympify(other)
        if isinstance(other, constant_classes):
            if other is objects.zero:
                return objects.nan
            return self
        elif isinstance(other, MathematicalSymbol):
            if other is self:
                return objects.nan
            if other is objects.moo:
                return objects.nan
            if other is objects.nan:
                return other
            if other is objects.zoo:
                return objects.nan
        return NotImplemented    

    def __div__(self, other):
        other = sympify(other)
        if isinstance(other, constant_classes):
            return self
        elif isinstance(other, MathematicalSymbol):
            if other is objects.oo:
                return objects.nan # zoo/zoo
            if other is objects.moo:
                return objects.nan # zoo/-oo
            if other is objects.zoo:
                return objects.nan # zoo/zoo
            if other is objects.nan:
                return other
        return NotImplemented

    def __pow__(self, other):
        other = sympify(other)
        if isinstance(other, constant_classes):
            if other.is_positive:
                return self
            if other.is_negative:
                return objects.zero
            if other is objects.zero:
                return objects.one # zoo ** 0
        elif isinstance(other, MathematicalSymbol):
            if other is objects.oo:
                return objects.nan # zoo ** oo
            if other is objects.moo:
                return objects.zero # zoo ** -oo
            if other is objects.nan:
                return other
            if other is objects.zoo:
                return objects.nan # zoo ** zoo
        return NotImplemented

    def __radd__(self, other):
        if isinstance(other, Basic):
            obj = self + other
            if obj is NotImplemented:
                return classes.Add(other, self)
            return obj
        return sympify(other) + self

    def __rsub__(self, other):
        return self + other

    def __rmul__(self, other):
        if isinstance(other, Basic):
            obj = self * other
            if obj is NotImplemented:
                return classes.Mul(other, self)
            return obj
        return sympify(other) * self

    def __rdiv__(self, other):
        raise NotImplementedError(`self, other`)

    def __rpow__(self, other):
        raise NotImplementedError(`self, other`)

class ImaginaryUnit(MathematicalSymbol):
    """Positive imaginary unit I = Sqrt(-1).

    Reference:
      http://en.wikipedia.org/wiki/Imaginary_unit
    """

    def tostr(self, level=0):
        return 'I'

    def try_power(self, other):
        if isinstance(other, classes.Integer):
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

    def as_sexpr(self):
        return (IMAGUNIT, self)

classes.constant_classes = constant_classes = (
    classes.Number,
    MathematicalNumber)

classes.naninf_classes = naninf_classes = (
    NaN,
    Infinity,
    NegativeInfinity,
    ComplexInfinity
    )
