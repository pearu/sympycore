"""
Extended number instance is defined as

  Algebra({infinity: <U1 instance>}, head=TERMS)

"""
#
# Created: February 2008 by Pearu Peterson
#

from ..utils import str_SYMBOL, TERMS
from numbers import realtypes, complextypes, numbertypes, Complex

class Infinity(object):
    """ Infinity represents the limiting process in the definition
    of directional infinity:

      oo(c) =  lim   r * c
             r -> oo

    where c is a complex number defining direction of approaching
    infinity.

    +oo = oo(1)
    -oo = oo(-1)
    zoo = oo(None)
    undefined = oo(0)
    """

    _instance = None
    def __new__(cls):
        obj = cls._instance
        if obj is not None:
            return obj
        cls._instance = obj = object.__new__(cls)
        return obj

    def to_str_data(self, sort=True):
        return str_SYMBOL, 'oo'

    @staticmethod
    def canonize_TERMS_dict(pairs, cls):
        try:
            del pairs[cls.one]
        except KeyError:
            pass
        c = pairs[infinity]
        if isinstance(c, (int, long)):
            if c>0:
                pairs[infinity] = 1
            if c<0:
                pairs[infinity] = -1

    def get_oo(self, algebra_cls):
        obj = object.__new__(algebra_cls)
        obj.data = {self: U1(1)}
        obj.head = TERMS
        return obj

    def get_moo(self, algebra_cls):
        obj = object.__new__(algebra_cls)
        obj.data = {self: U1(-1)}
        obj.head = TERMS
        return obj

    def get_zoo(self, algebra_cls):
        obj = object.__new__(algebra_cls)
        obj.data = {self: U1(None)}
        obj.head = TERMS
        return obj

    def get_undefined(self, algebra_cls):
        obj = object.__new__(algebra_cls)
        obj.data = {self: U1(0)}
        obj.head = TERMS
        return obj

    def __mul__(self, other):
        if self is other:
            return self
        return NotImplemented

    def has_active(self):
        return False

infinity = Infinity()

class U1(object):
    """ A U(1) number.

    U1(value) represents a scaled value of a unit circle point in complex plain.
      (infinity * U1(value) is directional infinity)
    U1(None) represents the whole circle (infinity * U1(None) is projective infinity).
    U1(0) represents the origin of the complex plane (infinity * U1(0) is undefined).
    """

    def __new__(cls, value):
        obj = object.__new__(cls)
        if isinstance(value, realtypes):
            if value > 0:
                value = 1
            elif value < 0:
                value = -1
            else:
                value = 0
        elif isinstance(value, complextypes):
            re, im = value.real, value.imag
            if not re:
                if im > 0:
                    value = Complex(0, 1)
                elif im < 0:
                    value = Complex(0, -1)
                else:
                    value = 0
            else:
                value = value / abs(value)
        elif value is None:
            pass
        else:
            raise TypeError("%s(%r)" % (cls.__name__, value))
        obj.value = value
        return obj

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self.value)

    def __str__(self):
        if self.is_circle:
            return 'Z'
        if self.is_origin:
            return '0'
        return str(self.value)

    def __nonzero__(self):
        return True

    def __eq__(self, other):
        if isinstance(other, U1):
            return self.value == other.value
        return False

    def __hash__(self):
        return hash((U1, self.value))
    
    @property
    def is_circle(self):
        return self.value is None
    @property
    def is_origin(self):
        return self.value==0

    def __pos__(self):
        return self

    def __neg__(self):
        if self.value:
            return U1(-self.value)
        return self

    def __add__(self, other):
        if self.is_origin:
            return self
        if isinstance(other, numbertypes):
            if not other:
                return self
            other = U1(other)
        if isinstance(other, U1):
            if self.is_circle or not other.value:
                return U1(0)
            return U1(self.value + other.value)
        return NotImplemented

    __radd__ = __add__

    def __sub__(self, other):
        return self + (-other)

    def __rsub__(self, other):
        return U1(other) - self

    def __mul__(self, other):
        if self.is_origin:
            return self
        if isinstance(other, numbertypes):
            other = U1(other)
        if isinstance(other, U1):
            if other.is_origin:
                return other
            if self.is_circle or other.is_circle:
                return U1(None)
            return U1(self.value * other.value)
        return NotImplemented        

    __rmul__ = __mul__
