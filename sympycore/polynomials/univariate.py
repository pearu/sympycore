#
# Author: Fredrik Johansson
# Created: January 2008
""" Provides UnivariatePolynomial class.
"""
__docformat__ = "restructuredtext"
__all__ = ['UnivariatePolynomial']

from ..basealgebra.primitive import PrimitiveAlgebra, ADD, POW, MUL, NUMBER, SYMBOL
from ..basealgebra import BasicAlgebra
from ..arithmetic.numbers import div

class UnivariatePolynomial(BasicAlgebra):
    """ Represents (dense) univariate polynomial.
    """

    def __new__(cls, coefs=[], symbol='x', coerce_input=True):
        obj = object.__new__(cls)
        coefs = coefs or [0]
        if coerce_input:
            obj.coefs = tuple(map(cls.convert_coef, coefs))
        else:
            obj.coefs = tuple(coefs)
        obj.symbol = symbol
        while obj.coefs and not obj.coefs[-1]:
            obj.coefs = obj.coefs[:-1]
        obj.degree = len(obj.coefs) - 1
        return obj

    def __nonzero__(self):
        return bool(self.coefs)

    @classmethod
    def convert_coef(cls, x):
        # permit anything by default
        return x

    def as_primitive(self):
        P = PrimitiveAlgebra
        if self.degree == -1:
            return P((NUMBER, 0))
        t = []
        x = P((SYMBOL, self.symbol))
        for exp, coef in enumerate(self.coefs):
            if coef == 0:
                continue
            scoef = P((NUMBER, coef))
            if exp == 0:
                monomial = scoef
            else:
                monomial = x
                if exp != 1: monomial = monomial ** P((NUMBER, exp))
                if coef != 1: monomial = scoef * monomial
            t.append(monomial)
        return PrimitiveAlgebra((ADD, tuple(t)), head=ADD)

    @property
    def tree(self):
        return self.as_primitive().tree

    def __repr__(self):
        return str(self.as_primitive())

    __str__ = __repr__

    def __hash__(self):
        return hash((self.coefs, self.symbol))

    def __eq__(self, other):
        if not isinstance(other, UnivariatePolynomial):
            return NotImplemented
        return self.symbol == other.symbol and self.coefs == other.coefs

    def __call__(self, x):
        if isinstance(x, UnivariatePolynomial):
            p = self.__class__([])
            xp = self.__class__([1])
            for i, c in enumerate(self.coefs):
                p += c * xp
                xp *= x
            return p
        else:
            y = self.__class__.convert_coef(0)
            for c in reversed(self.coefs):
                y = y*x+c
            return y

    def __neg__(self):
        return self.__class__([-c for c in self.coefs], self.symbol, False)

    def __add__(self, other):
        if not isinstance(other, UnivariatePolynomial):
            other = self.__class__([other], self.symbol)
        if self.symbol != other.symbol:
            return NotImplemented
        coefs = [a+b for (a, b) in zip(self.coefs, other.coefs)]
        if self.degree >= other.degree:
            coefs += self.coefs[other.degree+1:]
        else:
            coefs += other.coefs[self.degree+1:]
        return self.__class__(coefs, self.symbol, False)

    __radd__ = __add__

    def __sub__(self, other):
        return self + (-other)

    def __rsub__(self, other):
        return (-self) + other

    def __mul__(self, other):
        if not isinstance(other, UnivariatePolynomial):
            try:
                other = self.convert_coef(other)
                coefs = [other*c for c in self.coefs]
                return self.__class__(coefs, self.symbol, False)
            except:
                pass
            return NotImplemented
        if self.symbol != other.symbol:
            return NotImplemented
        p = [self.convert_coef(0)] * (len(self.coefs)+len(other.coefs))
        for i, c in enumerate(self.coefs):
            for j, d in enumerate(other.coefs):
                p[i+j] += c*d
        return self.__class__(p, self.symbol, False)

    __rmul__ = __mul__

    def __pow__(self, n):
        # TODO: Miller's algorithm
        assert isinstance(n, int) and n >= 0
        if n == 0: return self.__class__([1])
        if n == 1: return self
        if n & 1 == 0: return (self*self)**(n//2)
        if n & 1 == 1: return self*((self*self)**(n//2))

    def __divmod__(self, other):
        if isinstance(other, UnivariatePolynomial):
            if self.symbol != other.symbol:
                return NotImplemented
            if other.degree < 0:
                raise ZeroDivisionError, "polynomial division"
            n = self.degree
            nv = other.degree
            u = self.coefs
            v = other.coefs
            r = list(u)
            q = [0] * (len(r)+1)
            for k in range(n-nv, -1, -1):
                q[k] = div(r[nv+k], v[nv])
                for j in range(nv+k-1, k-1, -1):
                    r[j] -= q[k]*v[j-k]
            for j in range(nv, n+1, 1):
                r[j] = 0
            return self.__class__(q), self.__class__(r)
        else:
            if other == 0:
                raise ZeroDivisionError, "polynomial division"
            rec = div(1, other)
            q = self.__class__([c*rec for c in self.coefs], self.symbol)
            r = self.__class__(self.symbol)
            return q, r

    def __div__(self, other):
        return divmod(self, other)[0]

    __truediv__ = __div__

    def __mod__(self, other):
        return divmod(self, other)[1]

    def diff(self):
        return self.__class__([c*(k+1) for k, c in enumerate(self.coefs[1:])],
            self.symbol, False)


poly = UnivariatePolynomial

