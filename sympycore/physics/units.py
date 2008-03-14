""" Provides Unit class.
"""

__docformat__ = "restructuredtext"
__all__ = [\
    'Unit', 'meter', 'kilogram', 'second', 'ten', 'yotta', 'zetta',
    'exa', 'peta', 'tera', 'giga', 'mega', 'kilo', 'deca', 'deci',
    'centi', 'milli', 'micro', 'nano', 'pico', 'femto', 'atto',
    'zepto', 'yocto' ]

from ..core import classes

from ..calculus.algebra import Calculus, algebra_numbers
from ..basealgebra.pairs import CollectingField

class Unit(CollectingField):
    """ Represents an algebra of physical units.

    Elements of the units algebra are unit symbols.
    Coefficients of the units algebra are Calculus instances.
    """

    def as_algebra(self, cls):
        """ Convert algebra to another algebra.
        """
        if cls is classes.Verbatim:
            return self.as_verbatim()
        if cls is Calculus:
            return NotImplemented
        return self.as_verbatim().as_algebra(cls)

classes.Unit = Unit

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

