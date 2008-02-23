
from .numbers import realtypes, complextypes, Complex, numbertypes


class Infinity(object):
    """ Base class for directional infinities.

    The formal definition of directional infinity is

      Infinity(direction) == oo * U1(direction)

    where oo represents a symbol of formal limiting process limit(r, r->oo).

    Derived classes may redefine classmethods

      U1(x)          - maps complex number x to unit circle using scaling,
                       U1(0) is defined to return 0,
                       U1(oo*U1(z)) is defined to return U1(z)
      IsUnbounded(x) - returns 1 if x is unbounded expression
      IsZero(x)      - returns 1 if x is zero
      
    to add algebra support (including symbolic functions) to direction
    expression.

    The following notation is used:

      +oo = Infinity(1)
      -oo = Infinity(-1)
      undefined = Infinity(0)
      zoo = Infinity(E**Infinity(I))  (when direction algebra defines symbol E)
    
    """

    @classmethod
    def U1(cls, x):
        if isinstance(x, realtypes):
            return cmp(x, 0)
        if isinstance(x, complextypes):
            c = Complex(x.real, x.imag)
            return c / abs(c)
        if isinstance(x, cls):
            return x.data
        raise NotImplementedError('%s(%r)' % (cls.U1, x))

    @classmethod
    def IsUnbounded(cls, x):
        if isinstance(x, Infinity):
            return 1
        if isinstance(x, numbertypes):
            # XXX: handle Float nan, inf
            return 0
        raise NotImplementedError('%s(%r)' % (cls.IsUnbounded, x))

    @clasmethod
    def IsZero(cls, x):
        if not x:
            return 1
        if isinstance(x, numbertypes):
            return 0
        raise NotImplementedError('%s(%r)' % (cls.IsZero, x))

    def __new__(cls, direction):
        obj = object.__new__(cls)
        obj.data = cls.U1(direction)
        return obj

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self.data)

    def __str__(self):
        d = self.data
        if d==1:
            return 'oo'
        if d==-1:
            return '-oo'
        if d==0:
            return 'undefined'
        return '(%s)*oo' % (d)

    def __abs__(self):
        return self.__class__(abs(self.data))

    def __neg__(self):
        return self.__class__(-self.data)

    def __add__(self, other):
        """
        oo*U1(x) + oo*U1(y) -> oo*(IsZero(U1(x)-U1(y)) * U1(x))
        oo*U1(x) + y        -> oo*(IsZero(U1(x)-U1(y)*IsUnbounded(y)-U(x)*(1-IsUnboundend(y)))*U1(x))
                            -> oo*(IsZero(IsUnbounded(y)*(U1(x)-U1(y)))*U1(x))
        y + oo*U1(x)        -> oo*U1(x) + y
        """
        cls = self.__class__
        return Infinity(cls.IsZero(cls.IsUnbounded(other)*(self.data-cls.U1(other))) * self.data)

    __radd__ = __add__

    def __sub__(self, other):
        """
        oo*U1(x) - y -> oo*U1(x) + (-y)
        """
        return self + (-other)

    def __rsub__(self, other):
        """
        y - oo*U1(x) -> oo*U1(-x) + y
        """
        return (-self) + other

    def __mul__(self, other):
        """
        (oo*U1(x)) * (oo*U1(y)) -> oo*(U1(x) * U1(y)) -> oo*U1(x*y)
        (oo*U1(x)) * y          -> oo*U1(x*y)
        """
        cls = self.__class__
        if isinstance(other, Infinity):
            return cls(self.data * other.data)
        return cls(self.data * other)

    def __div__(self, other):
        """
        (oo*U1(x)) / (oo*U1(y)) -> (oo*U1(x)) * (1/(oo*U1(y))
        (oo*U1(x)) / y          -> (oo*U1(x)) * (1/y)
        """
        return self * (1/other)

    def __rdiv__(self, other):
        """
        y / oo*U1(x) -> 0
        """
        # XXX: here we could define directional zero.
        return 0

    def __pow__(self, other):
        """
        (oo*U1(x))**0  -> 1
        (oo*0)**y      -> oo*0
        (oo*U1(x))**y  -> (1/(oo*U1(x)))**(-y) if y<0
        (oo*U1(x)) ** (oo*U1(y)) -> exp(oo*U1(y) * log(oo*U1(x)))
                                 -> exp(oo*U1(y) * (oo + log(U1(x))))
                                 -> exp(oo*U1(y) + oo*(U1(y)*log(U1(x))))
                                 
        """
        if not other:
            return 1
        if not self.data:
            return self
        cls = self.__class__
        if isinstance(other, realtypes):
            if other < 0:
                return (1/self) ** (-other)
            return cls(self.data ** other)
        y = cls.U1(other)
        z = cls.U1(y * cls.Log(self.data))
        return cls.Exp(cls(y) + cls(z))

    def __rpow__(self, other):
        """
        1 ** (oo*U1(x)) -> 1
        y ** (oo*U1(x)) -> exp(oo*U1(x)*log(y))
                        -> exp(oo*U1(x*log(y)))
        """
        cls = self.__class__
        if isinstance(other, realtypes):
            if other==1:
                return 1
            elif other>1:
                z = self.data
            elif other>1:
                z = -self.data
            else:
                z = self.data * cls.Log(other)
        else:
            z = self.data * cls.Log(other)
        return cls.Exp(cls(z))
