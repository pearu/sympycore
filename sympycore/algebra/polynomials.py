
from .primitive import PrimitiveAlgebra, ADD, SYMBOL

from .algebraic_structures import BasicAlgebra

class UnivariatePolynomial(BasicAlgebra):

    def __new__(cls, coefs=[], symbol='x'):
        obj = object.__new__(cls)
        coefs = coefs or [0]
        obj.coefs = tuple(map(obj.coerce_coef, coefs))
        obj.symbol = symbol
        while obj.coefs and not obj.coefs[-1]:
            obj.coefs = obj.coefs[:-1]
        obj.degree = len(obj.coefs) - 1
        return obj

    @classmethod
    def coerce_coef(cls, x):
        # permit anything by default
        return x

    def as_primitive(self):
        t = []
        x = PrimitiveAlgebra((SYMBOL,self.symbol))
        for i, c in enumerate(self.coefs):
            i = PrimitiveAlgebra((NUMBER,i))
            t.append(PrimitiveAlgebra((NUMBER,c)) * x**i)
        return (ADD,tuple(t))

    @property
    def tree(self):
        return self.as_primitive().tree

    def __repr__(self):
        if self.degree == -1:
            return "0.0"
        s = []
        for i, c in enumerate(self.coefs):
            if not c: continue
            t = str(c)
            if i > 0: t += "*" + self.symbol
            if i > 1: t += ("**%i" % i)
            s.append(t)
        return " + ".join(s[::-1])

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
            y = self.__class__.coerce_coef(0)
            for c in reversed(self.coefs):
                y = y*x+c
            return y

    def __neg__(self):
        return self.__class__([-c for c in self.coefs], self.symbol)

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
        return self.__class__(coefs, self.symbol)

    __radd__ = __add__

    def __sub__(self, other):
        return self + (-other)

    def __rsub__(self, other):
        return (-self) + other

    def __mul__(self, other):
        if not isinstance(other, UnivariatePolynomial):
            try:
                other = self.coerce_coef(other)
                coefs = [other*c for c in self.coefs]
                return self.__class__(coefs, self.symbol)
            except:
                pass
            return NotImplemented
        p = [self.coerce_coef(0)] * (len(self.coefs)+len(other.coefs))
        for i, c in enumerate(self.coefs):
            for j, d in enumerate(other.coefs):
                p[i+j] += c*d
        return self.__class__(p)

    __rmul__ = __mul__

    def __pow__(self, n):
        assert isinstance(n, int) and n >= 0
        if n == 0: return self.__class__([1])
        if n == 1: return self
        if n & 1 == 0: return (self*self)**(n//2)
        if n & 1 == 1: return self*((self*self)**(n//2))

    def __divmod__(self, other):
        # XXX: should convert to rationals when coefficients are ints
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
                q[k] = r[nv+k] / v[nv]
                for j in range(nv+k-1, k-1, -1):
                    r[j] -= q[k]*v[j-k]
            for j in range(nv, n+1, 1):
                r[j] = 0
            return self.__class__(q), self.__class__(r)
        else:
            if other == 0:
                raise ZeroDivisionError, "polynomial division"
            q = self.__class__([c/other for c in self.coefs], self.symbol)
            r = self.__class__(self.symbol)
            return q, r

    def __div__(self, other):
        return divmod(self, other)[0]

    __truediv__ = __div__

    def __mod__(self, other):
        return divmod(self, other)[1]

    def diff(self):
        return self.__class__([c*(k+1) for k, c in enumerate(self.coefs[1:])],
            self.symbol)


poly = UnivariatePolynomial

x = poly([0, 1])
