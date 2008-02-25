#
# Created January 2008 by Pearu Peterson
#

from ..core import classes
from ..utils import TERMS, str_PRODUCT
from ..basealgebra import BasicAlgebra
from ..basealgebra.primitive import PrimitiveAlgebra, SYMBOL, NUMBER, ADD, MUL

from ..basealgebra.pairs import CommutativeRingWithPairs, newinstance

from ..arithmetic.numbers import FractionTuple, normalized_fraction, Float, Complex, \
    try_power

from ..arithmetic.evalf import evalf


algebra_numbers = (int, long, FractionTuple, Float, Complex)

class Calculus(CommutativeRingWithPairs):
    """ Represents an element of a symbolic algebra. The set of a
    symbolic algebra is a set of expressions. There are four kinds of
    expressions: Symbolic, SymbolicNumber, SymbolicTerms,
    SymbolicFactors.

    Calculus basically models the structure of SymPy.
    """

    __slots__ = ['head', 'data', '_hash', 'one', 'zero']
    _hash = None

    coefftypes = (int, long, FractionTuple, Complex, Float)
    exptypes = (int, long, FractionTuple, Complex, Float)

    def as_algebra(self, cls):
        """ Convert algebra to another algebra.
        """
        if cls is classes.PrimitiveAlgebra:
            return self.as_primitive()
        if cls is classes.Unit:
            return newinstance(cls, NUMBER, self)
        if issubclass(cls, PolynomialRing):
            return self.as_polynom(cls)
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
                if self.one==t:
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
    def convert_coefficient(cls, obj, typeerror=True):
        """ Convert obj to coefficient algebra.
        """
        if isinstance(obj, float):
            return Float(obj)
        if isinstance(obj, complex):
            return Complex(Float(obj.real), Float(obj.imag))
        if isinstance(obj, algebra_numbers):
            return obj
        if isinstance(obj, cls) and obj.head is NUMBER:
            return obj.data
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
            return Float(obj)
        if isinstance(obj, complex):
            return Complex(Float(obj.real), Float(obj.imag))
        if isinstance(obj, algebra_numbers):
            return obj

        # parse algebra expression from string:
        if isinstance(obj, (str, unicode, PrimitiveAlgebra)):
            return PrimitiveAlgebra(obj).as_algebra(cls)

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
        return cls(normalized_fraction(num, denom), head=NUMBER)

    @classmethod
    def Symbol(cls, obj):
        return cls(obj, head=SYMBOL)

    @classmethod
    def Log(cls, arg, base=None):
        log = cls.defined_functions['log']
        if base is None:
            return log(arg)
        return log(arg)/log(base)

    @classmethod
    def Exp(cls, arg):
        return cls.defined_functions['exp'](arg)

    @classmethod
    def Sign(cls, arg):
        sign = cls.defined_functions['sign']
        return sign(arg)

    @classmethod
    def npower(cls, base, exp):
        num, sym = try_power(base, exp)
        if not sym:
            return newinstance(cls, NUMBER, num)
        d = dict([(newinstance(cls, NUMBER, b), e) for b, e in sym])
        return newinstance(cls, MUL, d) * num

    def evalf(self, n=15):
        head = self.head
        if head is NUMBER:
            return self.Number(evalf(self.data, n))
        if head is SYMBOL:
            r = getattr(self.data, 'evalf', lambda p: NotImplemented )(n)
            if r is not NotImplemented:
                return self.Number(r)
            return self
        convert = self.convert
        return self.func(*[convert(a).evalf(n) for a in self.args])

    def to_Float(self, n=15):
        f = self.evalf(n)
        if f.is_Number:
            return f.data
        return NotImplemented

    def get_direction(self):
        head = self.head
        if head is NUMBER:
            value = self.data
            if isinstance(value, (int, long)):
                return value
            return getattr(value, 'get_direction', lambda : NotImplemented)()
        if head is TERMS:
            data = self.data
            if len(data)==1:
                t, c = data.items()[0]
                r = t.get_direction()
                if r is not NotImplemented:
                    return r * c
        if head is MUL:
            direction = 1
            for t,c in self.data.iteritems():
                d = t.get_direction()
                if d is NotImplemented:
                    return d
                if not isinstance(c, (int, long)):
                    return NotImplemented
                d = self.npower(d, c).get_direction()
                if d is NotImplemented:
                    return d
                direction *= d
            return direction
        return getattr(self.data, 'get_direction', lambda : NotImplemented)()

    @property
    def is_bounded(self):
        head = self.head
        if head is NUMBER:
            value = self.data
            if isinstance(value, (int, long)):
                return True
            return getattr(value, 'is_bounded', None)
        if head is SYMBOL:
            return getattr(self.data, 'is_bounded', None)
        if head is ADD:
            for t, c in self.data.iteritems():
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

    def __eq__(self, other):
        if self is other:
            return True
        if other.__class__ is self.__class__:
            return self.head == other.head and self.data == other.data
        if self.head is NUMBER and isinstance(other, algebra_numbers):
            return self.data == other
        return False

    def __lt__(self, other):
        other = self.convert(other)
        if self.head is NUMBER and other.head is NUMBER:
            return self.data < other.data
        return Lt(self, other)

    def __le__(self, other):
        other = self.convert(other)
        if self.head is NUMBER and other.head is NUMBER:
            return self.data <= other.data
        return Le(self, other)

    def __gt__(self, other):
        other = self.convert(other)
        if self.head is NUMBER and other.head is NUMBER:
            return self.data > other.data
        return Gt(self, other)

    def __ge__(self, other):
        other = self.convert(other)
        if self.head is NUMBER and other.head is NUMBER:
            return self.data >= other.data
        return Ge(self, other)

    def as_polynom(self, cls=None):
        if cls is None:
            cls = PolynomialRing
        head = self.head
        if head is NUMBER:
            return cls(self)
        if head is SYMBOL:
            try:
                i = list(cls.variables).index(self)
            except ValueError:
                i = None
            if i is None:
                try:
                    i = list(cls.variables).index(self.data)
                except ValueError:
                    i = None
            if i is not None:
                l = [0]*cls.nvars
                l[i] = 1
                return cls({AdditiveTuple(l):1})                
            return cls[(self.data,), self.__class__]({1:1})
        if head is ADD:
            return cls.Add(*[t.as_polynom(cls)*c for t,c in self.data.iteritems()])
        if head is MUL:
            return cls.Mul(*[t.as_polynom(cls)**c for t,c in self.data.iteritems()])
        raise NotImplementedError(`head, self`)

    def __divmod__(self, other):
        if isinstance(other, Calculus):
            lhs = self.as_polynom()
            rhs = other.as_polynom(lhs.__class__)
            return divmod(lhs, rhs)
        return NotImplemented

class Positive:
    def __init__(self, a):
        self.a = a
    def __repr__(self):
        return "(%s) > 0" % self.a

class Nonnegative:
    def __init__(self, a):
        self.a = a
    def __repr__(self):
        return "(%s) >= 0" % self.a

def Lt(a, b): return Positive(b-a)
def Le(a, b): return Nonnegative(b-a)
def Gt(a, b): return Positive(a-b)
def Ge(a, b): return Nonnegative(a-b)

A = Calculus
one = A(1, head=NUMBER)
zero = A(0, head=NUMBER)
A.one = one
A.zero = zero

I = A(Complex(0,1), head=NUMBER)

def integrate(expr, x):
    return Calculus(expr).integrate(x)

from ..polynomials.algebra import PolynomialRing, AdditiveTuple
