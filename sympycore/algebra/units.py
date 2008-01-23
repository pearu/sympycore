from ..core import classes

from .primitive import NUMBER
from .std_commutative_algebra import Calculus, algebra_numbers
from .pairs import CommutativeRingWithPairs, newinstance

class Unit(CommutativeRingWithPairs):
    """ Represents an algebra of physical units.

    Elements of the units algebra are unit symbols.
    Coefficients of the units algebra are Calculus instances.
    """
    @classmethod
    def convert_coefficient(cls, obj, typeerror=True):
        """ Convert obj to coefficient algebra.
        """
        if isinstance(obj, algebra_numbers):
            obj = newinstance(Calculus, NUMBER, obj)
        if isinstance(obj, Calculus):
            return newinstance(cls, NUMBER, obj)
        if typeerror:
            raise TypeError('%s.convert_coefficient: failed to convert %s instance'\
                            ' to coefficient algebra, expected int|long object'\
                            % (cls.__name__, obj.__class__.__name__))
        else:
            return NotImplemented        

    def as_algebra(self, cls):
        """ Convert algebra to another algebra.
        """
        if cls is classes.PrimitiveAlgebra:
            return self.as_primitive()
        if cls is Calculus:
            return NotImplemented
        return self.as_primitive().as_algebra(cls)

meter = Unit.Symbol('m')
kilogram = Unit.Symbol('kg')
second = Unit.Symbol('s')

ten = Calculus.Number(10)
yotta = ten**24
zetta = ten**21
exa   = ten**18
peta  = ten**15
tera  = ten**12
giga  = ten**9
mega  = ten**6
kilo  = ten**3
deca  = ten**1
deci  = ten**-1
centi = ten**-2
milli = ten**-3
micro = ten**-6
nano  = ten**-9
pico  = ten**-12
femto = ten**-15
atto  = ten**-18
zepto = ten**-21
yocto = ten**-24
