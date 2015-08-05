
__all__ = ['Singleton', 'ImaginaryUnit', 'Exp1', 'Pi']

from base import Symbolic, Constant
from base import RelationalMethods, FunctionalMethods, ArithmeticMethods

class Singleton(Symbolic):
    """ Singleton object.
    """

    ###########################################################################
    #
    # Constructor methods
    #

    def __new__(cls,*args,**kws):
        obj = Singleton.__dict__.get(cls.__name__)
        if obj is None:
            obj = Symbolic.__new__(cls,*args,**kws)
            setattr(Singleton, cls.__name__, obj)
        return obj

    def init(self): return

    def astuple(self): return (self.__class__.__name__,)

    ###########################################################################
    #
    # Transformation methods
    #

    def calc_expanded(self): return self

    ###########################################################################
    #
    # Comparison methods
    #

    def is_equal(self, other):
        return self is other

#
# End of Singleton class
#
################################################################################

class ConstantSingleton(Singleton, Constant):

    pass

#
# End of ConstantSingleton class
#
################################################################################


class Exp1(RelationalMethods, ArithmeticMethods,
           ConstantSingleton):
    """ Represents exp(1).
    """

    ############################################################################
    #
    # Informational methods
    #
    
    def get_precedence(self): return 0

    def is_positive(self): return True
    def is_negative(self): return False

    ###########################################################################
    #
    # Transformation methods
    #

    def tostr(self, level=0):
        return 'E'

    def _todecimal(self):
        return decimal_math.e()

#
# End of Exp1 class
#
################################################################################

class Pi(RelationalMethods, ArithmeticMethods, ConstantSingleton):
    """ Represents Pi.
    """

    ############################################################################
    #
    # Informational methods
    #

    def get_precedence(self): return 0

    def is_positive(self): return True
    def is_negative(self): return False

    ###########################################################################
    #
    # Transformation methods
    #

    def tostr(self, level=0):
        return 'Pi'

    def _todecimal(self):
        return decimal_math.pi()

#
# End of Pi class
#
################################################################################

class ImaginaryUnit(ArithmeticMethods,  RelationalMethods,
                    ConstantSingleton):
    """ Represents imaginary unit I = sqrt(-1).
    """

    ###########################################################################
    #
    # Constructor methods
    #

    def eval_power(base, exponent):
        """
        base is I = sqrt(-1)
        exponent is symbolic object but not equal to 0, 1

        I ** r -> (-1)**(r/2) -> exp(r/2 * Pi * I) -> sin(Pi*r/2) + cos(Pi*r/2) * I, r is decimal
        I ** 0 mod 4 -> 1
        I ** 1 mod 4 -> I
        I ** 2 mod 4 -> -1
        I ** 3 mod 4 -> -I
        """
        if isinstance(exponent, Number):
            if isinstance(exponent, Decimal):
                a = decimal_math.pi() * exponent.num / 2
                return Decimal(decimal_math.sin(a) + decimal_math.cos(a) * ImaginaryUnit())
            if isinstance(exponent, Integer):
                e = exponent.numer % 4
                if e==0: return One()
                if e==1: return ImaginaryUnit()
                if e==2: return NegativeOne()
                return NegativeImaginaryUnit()
            return NegativeOne() ** (Half() * other)
        return

    ############################################################################
    #
    # Informational methods
    #

    def get_precedence(self): return 0

    def is_positive(self): return False
    def is_negative(self): return False

    ###########################################################################
    #
    # Transformation methods
    #

    def tostr(self, level=0):
        return 'I'

    ############################################################################
    #
    # Arithmetic operations
    #

    def __neg__(self): return NegativeImaginaryUnit()

    def __mul__(self, other):
        if isinstance(other, ImaginaryUnit): return NegativeOne()
        if isinstance(other, NegativeImaginaryUnit): return One()
        return Symbolic.Mul(self, other)

#
# End of ImaginaryUnit class
#
################################################################################


class NegativeImaginaryUnit(ArithmeticMethods, RelationalMethods,
                            ConstantSingleton):
    """ -I
    """

    ############################################################################
    #
    # Informational methods
    #
    
    def get_precedence(self): return 30

    def is_positive(self): return False
    def is_negative(self): return False

    ###########################################################################
    #
    # Transformation methods
    #

    def tostr(self, level=0):
        precedence = self.get_precedence()
        if precedence<=level:
            return '(-I)'
        return '-I'

    ############################################################################
    #
    # Arithmetic operations
    #

    def __neg__(self): return ImaginaryUnit()
    def __mul__(self, other): return -((-self) * other)

#
# End of NegativeImaginaryUnit class
#
################################################################################


Symbolic.singleton_classes['E'] = Exp1
Symbolic.singleton_classes['Pi'] = Pi
Symbolic.singleton_classes['I'] = ImaginaryUnit

Symbolic.Singleton = Singleton
Symbolic.ImaginaryUnit = ImaginaryUnit
Symbolic.NegativeImaginaryUnit = NegativeImaginaryUnit
Symbolic.Exp1 = Exp1
Symbolic.Pi = Pi
