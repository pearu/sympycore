
from ..utils import str_PRODUCT, NUMBER, TERMS, FACTORS
from ..arithmetic import Infinity
from .algebra import A, newinstance

class CalculusInfinity(Infinity):

    def __new__(cls, direction):
        if isinstance(direction, A):
            head, data = direction.head, direction.data
            if head is NUMBER:
                return cls(data)
            elif head is TERMS:
                if len(data)==1:
                    t, c = data.items()[0]
                    if c > 0:
                        return cls(t)
            r = direction.get_direction()
            if r is not NotImplemented:
                return cls(r)
        return Infinity.__new__(cls, direction)

    def to_str_data(self, sort=True):
        return str_PRODUCT, str(self)

    def _get_symbols_data(self):
        return set()

    def subs(self, *args):
        d = self.data
        if isinstance(d, A):
            return type(self)(d.subs(*args))
        return self

    @classmethod
    def IsUnbounded(cls, x):
        if isinstance(x, A):
            head = x.head
            if head is NUMBER:
                return cls.IsUnbounded(x.data)
            f = x.is_bounded
            if f or f is not None:
                return A.convert(not f)
        if isinstance(x, cls):
            return A.one
        r = Infinity.IsUnbounded(x)
        if r is not NotImplemented:
            return A.convert(r)
        x = A.convert(x)
        return newinstance(A, cls.IsUnbounded, x)

    @classmethod
    def EqualArg(cls, x, y):
        if isinstance(x, A):
            d = x.get_direction()
            if d is not NotImplemented:
                return cls.EqualArg(d, y)
        if isinstance(y, A):
            d = y.get_direction()
            if d is not NotImplemented:
                return cls.EqualArg(x, d)
            if isinstance(x, A):
                xy = x / y
                if xy.head is NUMBER:
                    return A.convert(xy.data > 0)

        r = Infinity.EqualArg(x, y)
        if r is not NotImplemented:
            return A.convert(r)
        x = A.convert(x)
        y = A.convert(y)
        return newinstance(A, cls.EqualArg, (x, y))

    @classmethod
    def IsPositive(cls, x):
        if isinstance(x, A):
            if x.head is NUMBER:
                return cls.IsPositive(x.data)
        r = Infinity.IsPositive(x)
        if r is not NotImplemented:
            return A.convert(r)
        x = A.convert(x)
        return newinstance(A, cls.IsPositive, x)

    def __pow__(self, other):
        if isinstance(other, A):
            head, data = other.head, other.data
            if head is NUMBER:
                other = data
        r = Infinity.__pow__(self, other)
        if r is not NotImplemented:
            if isinstance(r, type(self)):
                return r
            return A.convert(r)
        x = A.convert(other)
        return newinstance(A, FACTORS, {self:x})

    def __rpow__(self, other):
        if isinstance(other, A):
            head, data = other.head, other.data
            if head is NUMBER:
                other = data
        r = Infinity.__rpow__(self, other)
        if r is not NotImplemented:
            if isinstance(r, type(self)):
                return r
            return A.convert(r)
        x = A.convert(other)
        return newinstance(A, FACTORS, {x:self})

oo = CalculusInfinity(1)
moo = CalculusInfinity(-1)
undefined = CalculusInfinity(0)
zoo = CalculusInfinity(undefined)

A.oo = oo
A.zoo = zoo
A.undefined = undefined
A.Infinity = CalculusInfinity
