#
# Created January 2008 by Pearu Peterson
#
""" Provides Calculus class.
"""
__docformat__ = "restructuredtext"
__all__ = ['Calculus', 'I']

from ..core import classes, defined_functions
from ..utils import TERMS, str_PRODUCT, FACTORS, SYMBOL, NUMBER
from ..basealgebra import Algebra, Verbatim
from ..basealgebra.pairs import CollectingField

from ..arithmetic.numbers import normalized_fraction, mpq, mpf, mpc, mpqc, try_power

from ..arithmetic import mpmath, setdps
from ..arithmetic.evalf import evalf

algebra_numbers = (int, long, mpq, mpqc, mpf, mpc)
convertible_numbers = algebra_numbers + (float, complex)

float_one = mpf('1.0')

class Calculus(CollectingField):
    """ Represents an element of a symbolic algebra.

    The set of a symbolic algebra is a set of expressions.
    """

    _hash = None

    coefftypes = algebra_numbers
    coefftypes_set = frozenset(coefftypes)
    exptypes = algebra_numbers

    def as_algebra(self, cls):
        """ Convert algebra to another algebra.
        """
        if cls is Verbatim:
            return self.as_verbatim()
        if cls is classes.Unit:
            return cls(NUMBER, self)
        if issubclass(cls, PolynomialRing):
            return self.as_polynom(cls)
        return self.as_verbatim().as_algebra(cls)

    @classmethod
    def get_predefined_symbols(cls, name):
        if name=='I':
            return I
        return getattr(defined_functions, name, None)
    
    @classmethod
    def convert_coefficient(cls, obj, typeerror=True):
        """ Convert obj to coefficient algebra.
        """
        if isinstance(obj, float):
            return mpf(obj)
        if isinstance(obj, complex):
            return mpc(obj.real, obj.imag)
        if isinstance(obj, algebra_numbers):
            return obj
        if isinstance(obj, cls):
            head, data = obj.pair
            if head is NUMBER:
                return data
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
        if isinstance(obj, float):
            return mpf(obj)
        if isinstance(obj, complex):
            return mpc(obj.real, obj.imag)

        # parse algebra expression from string:
        if isinstance(obj, (str, unicode, Verbatim)):
            return Verbatim.convert(obj).as_algebra(cls)

        # convert from another algebra:
        if isinstance(obj, Algebra):
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
            return cls(NUMBER, num)
        return cls(NUMBER, normalized_fraction(num, denom))

    @classmethod
    def Log(cls, arg, base=None):
        log = defined_functions.log
        if base is None:
            return log(arg)
        return log(arg)/log(base)

    @classmethod
    def Exp(cls, arg):
        return defined_functions.exp(arg)

    @classmethod
    def Mod(cls, x, y):
        return defined_functions.mod(x, y)

    def evalf(self, n=None):
        if n:
            setdps(n)
        head, data = self.pair
        if head is NUMBER:
            return self.Number(data * float_one)
        if head is SYMBOL:
            r = getattr(data, 'evalf', lambda p: NotImplemented)(n)
            if r is not NotImplemented:
                return self.Number(r)
            return self
        if callable(head):
            v = self.args[0].evalf(n)
            h, d = v.pair
            if h is NUMBER:
                return self.Number(getattr(mpmath, self.func.__name__)(d))
            else:
                return head(v)
        convert = self.convert
        return self.func(*[convert(a).evalf(n) for a in self.args])

    def get_direction(self):
        head, data = self.pair
        if head is NUMBER:
            if isinstance(data, (int, long)):
                return data
            return getattr(data, 'get_direction', lambda : NotImplemented)()
        if head is TERMS:
            if len(data)==1:
                t, c = data.items()[0]
                r = t.get_direction()
                if r is not NotImplemented:
                    return r * c
        if head is FACTORS:
            direction = 1
            cls = type(self)
            for t,c in self.data.iteritems():
                d = t.get_direction()
                if d is NotImplemented:
                    return d
                if not isinstance(c, (int, long)):
                    return NotImplemented
                d = self.Pow(cls.convert(d), c).get_direction()
                if d is NotImplemented:
                    return d
                direction *= d
            return direction
        return getattr(data, 'get_direction', lambda : NotImplemented)()

    @property
    def is_bounded(self):
        head, data = self.pair
        if head is NUMBER:
            if isinstance(data, (int, long)):
                return True
            return getattr(data, 'is_bounded', None)
        if head is SYMBOL:
            return getattr(data, 'is_bounded', None)
        if head is TERMS:
            for t, c in data.iteritems():
                b = t.is_bounded
                if not b:
                    return b
                if isinstance(c, (int, long)):
                    continue
                b = getattr(c, 'is_bounded', None)
                if not b:
                    return b
            return True
        return

    def as_polynom(self, ring_cls=None):
        """ Convert expression to an element of polynomial ring.
        
        If the polynomial ring is not given then it will be created.

        For example,

          >>> x,y,z = map(Symbol,'xyz')
          >>> (x+2*y+3*z).as_polynom() + y*z
          PolynomialRing[(x, y, z), Calculus]('2*x + y*z + y + 3*z')
          >>> P = PolynomialRing[x,y]
          >>> (x+2*y+3*z).as_polynom(P) + y*z
          PolynomialRing[(x, y), Calculus]('x + (2 + z)*y + 3*z')

        """
        if ring_cls is None:
            data, variables = self.to_polynomial_data()
            return PolynomialRing[tuple(variables)].convert(data)
        else:
            data, variables = self.to_polynomial_data(ring_cls.variables, True)
            return ring_cls.convert(data)

    def __divmod__(self, other):
        if isinstance(other, Calculus):
            lhs = self.as_polynom()
            rhs = other.as_polynom(type(lhs))
            return divmod(lhs, rhs)
        return NotImplemented

    def __float__(self):
        head, data = self.pair
        if head is NUMBER:
            return float(data)
        head, data = self.evalf().pair
        if head is NUMBER:
            return float(data)
        raise TypeError('Cannot convert %r to float' % (self))

    def __or__(self, other):
        if type(other) is tuple:
            return self.subs(*other)
        return self.subs(other)

classes.Calculus = Calculus

# as a result, x<y will return Logic(LT, (x, y)):
Calculus.enable_symbolic_comparison('inequality')

one = Calculus.Number(1)
zero = Calculus.Number(0)
Calculus.one = one
Calculus.zero = zero

I = Calculus.Number(mpqc(0,1))

from ..polynomials.algebra import PolynomialRing, AdditiveTuple
