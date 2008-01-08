
class UnivariatePolynomial:

    def __init__(self, coefs=[], symbol='x'):
        coefs = coefs or [0]
        self.coefs = tuple(map(self.coerce_coef, coefs))
        self.symbol = symbol
        while self.coefs and not self.coefs[-1]:
            self.coefs = self.coefs[:-1]
        self.degree = len(self.coefs) - 1

    @classmethod
    def coerce_coef(cls, x):
        # permit anything by default
        return x

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
            return NotImplemented
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


poly = UnivariatePolynomial

x = poly([0, 1])
