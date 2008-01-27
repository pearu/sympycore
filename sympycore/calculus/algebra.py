#
# Created January 2008 by Pearu Peterson
#

from ..core import classes
from ..basealgebra import BasicAlgebra
from ..basealgebra.primitive import PrimitiveAlgebra, SYMBOL, NUMBER, ADD, MUL

from ..basealgebra.pairs import CommutativeRingWithPairs, newinstance

from ..arithmetic.numbers import Fraction, Float, Complex, try_power, ExtendedNumber
from ..arithmetic.evalf import evalf

algebra_numbers = (int, long, Fraction, Float, Complex, ExtendedNumber)

class Calculus(CommutativeRingWithPairs):
    """ Represents an element of a symbolic algebra. The set of a
    symbolic algebra is a set of expressions. There are four kinds of
    expressions: Symbolic, SymbolicNumber, SymbolicTerms,
    SymbolicFactors.

    Calculus basically models the structure of SymPy.
    """

    __slots__ = ['head', 'data', '_hash', 'one', 'zero']
    _hash = None

    def as_algebra(self, cls):
        """ Convert algebra to another algebra.
        """
        if cls is classes.PrimitiveAlgebra:
            return self.as_primitive()
        if cls is classes.Unit:
            return newinstance(cls, NUMBER, self)
        return self.as_primitive().as_algebra(cls)

    defined_functions = {}

    @classmethod
    def get_predefined_symbols(cls, name):
        if name=='I':
            return I
        return cls.defined_functions.get(name)
    
    def canonize(self):
        head = self.head
        if head is ADD:
            pairs = self.data
            if not pairs:
                return self.zero
            if len(pairs)==1:
                t, c = pairs.items()[0]
                if c==1:
                    return t
                if self.one==t or (isinstance(c, ExtendedNumber) and c.is_undefined):
                    return self.convert(c)
        elif head is MUL:
            pairs = self.data
            pairs.pop(self.one, None)
            if not pairs:
                return self.one
            if len(pairs)==1:
                t, c = pairs.items()[0]
                if c==1:
                    return t
                if self.one==t:
                    return t
        return self

    @classmethod
    def redirect_operation(cls, *args, **kws):
        """
        Here should be handled operations with 'active' number
        such as extended numbers and floats.
        """
        callername = kws['redirect_operation']
        flag = True
        if callername in ['__mul__','__add__','__rmul__','__radd__']:
            lhs, rhs = args
        else:
            flag = False
        if flag:
            # handle operations with undefined:
            if rhs==undefined or lhs==undefined:
                return undefined

        # fallback to default:
        return getattr(cls, callername)(*args,
                                        **dict(redirect_operation='ignore_redirection'))

            

    @classmethod
    def convert_coefficient(cls, obj, typeerror=True):
        """ Convert obj to coefficient algebra.
        """
        if isinstance(obj, float):
            return Float(obj)
        if isinstance(obj, complex):
            return Complex(Float(obj.real), Float(obj.imag))
        if isinstance(obj, algebra_numbers):
            return obj
        if typeerror:
            raise TypeError('%s.convert_coefficient: failed to convert %s instance'\
                            ' to coefficient algebra, expected int|long object'\
                            % (cls.__name__, obj.__class__.__name__))
        else:
            return NotImplemented

    @classmethod
    def convert_exponent(cls, obj, typeerror=True):
        """ Convert obj to exponent algebra.
        """
        if isinstance(obj, cls):
            return obj
        if isinstance(obj, algebra_numbers):
            return obj
        if isinstance(obj, complex):
            return Complex(Float(obj.real), Float(obj.imag))
        if isinstance(obj, algebra_numbers):
            return obj

        # parse algebra expression from string:
        if isinstance(obj, (str, unicode)):
            obj = PrimitiveAlgebra(obj)

        # convert from another algebra:
        if isinstance(obj, BasicAlgebra):
            return obj.as_algebra(cls)
        
        if typeerror:
            raise TypeError('%s.convert_exponent: failed to convert %s instance'\
                            ' to exponent algebra, expected int|long object'\
                            % (cls.__name__, obj.__class__.__name__))
        else:
            return NotImplemented
    
    @classmethod
    def Number(cls, num, denom=None):
        if denom is None:
            return cls(num, head=NUMBER)
        return cls(Fraction(num, denom), head=NUMBER)

    @classmethod
    def Symbol(cls, obj):
        return cls(obj, head=SYMBOL)

    @classmethod
    def Log(cls, arg, base=None):
        if base is None:
            return classes.log(arg)
        return classes.log(arg)/classes.log(base)

    @classmethod
    def npower(cls, base, exp):
        num, sym = try_power(base, exp)
        if not sym:
            return newinstance(cls, NUMBER, num)
        d = dict([(newinstance(cls, NUMBER, b), e) for b, e in sym])
        return newinstance(cls, MUL, d) * num

    def evalf(self, n=15):
        return self.Number(evalf(self, n))

    def __eq__(self, other):
        if self is other:
            return True
        if other.__class__ is self.__class__:
            return self.head is other.head and self.data == other.data
        if self.head is NUMBER and isinstance(other, algebra_numbers):
            return self.data == other
        return False

A = Calculus
one = A(1, head=NUMBER)
zero = A(0, head=NUMBER)
A.one = one
A.zero = zero

I = A(Complex(0,1), head=NUMBER)
oo = A(ExtendedNumber.get_oo(), head=NUMBER)
moo = A(ExtendedNumber.get_moo(), head=NUMBER)
zoo = A(ExtendedNumber.get_zoo(), head=NUMBER)
undefined = A(ExtendedNumber.get_undefined(), head=NUMBER)

def integrate(expr, x):
    return Calculus(expr).integrate(x)
