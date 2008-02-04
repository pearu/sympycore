
from ..core import BasicType, classes
from ..utils import SYMBOL, NUMBER, ADD, MUL, POW
from ..basealgebra.ring import CommutativeRing
from ..basealgebra import PrimitiveAlgebra


class Polynomial(CommutativeRing):

    def __new__(cls, data, variables = None):
        if variables is None:
            raise NotImplementedError(`data`)
        obj = object.__new__(cls)
        assert isinstance(data, PolynomialRing),`data`
        obj.data = data
        obj.variables = variables
        return obj

class PolynomialRingGenerator(BasicType):
    """ Generator of polynomial rings:

    PolynomialRing[<n>, <ring>] - represents <n>-variate polynomial
    over coefficient <ring>.
    """

    def __getitem__(self, nvars, cache={}):
        if isinstance(nvars, tuple):
            nvars, ring = nvars
        else:
            ring = classes.Calculus
        r = cache.get((nvars, ring))
        if r is None:
            r = PolynomialRingGenerator('%s[%s, %s]' % (self.__name__, nvars, ring.__name__),
                                        (self,), dict(nvars=nvars, ring = ring))
            cache[nvars, ring] = r
        return r

class PolynomialRing(CommutativeRing):
    """ Base class to polynomial rings.
    """

    __metaclass__ = PolynomialRingGenerator

    def __new__(cls, data):
        assert cls is not PolynomialRing,`cls`
        obj = object.__new__(cls)
        obj.data = data
        return obj

    @classmethod
    def Number(cls, obj):
        return cls({(0,)*cls.nvars: obj})

    @classmethod
    def Add(cls, *seq):
        r = cls({})
        for t in seq:
            r += t
        return t

    @classmethod
    def convert_coefficient(cls, obj, typeerror=True):
        r = cls.ring.convert(obj, typeerror=False)
        if r is not None:
            return r

        if typeerror:
            raise TypeError('%s.convert_coefficient: failed to convert %s instance'\
                            ' to coefficient algebra, expected int|long object'\
                            % (cls.__name__, obj.__class__.__name__))
        else:
            return NotImplemented

    def as_primitive(self):
        data = self.data
        symbols = [PrimitiveAlgebra((SYMBOL,'X%s' % (i))) for i in range(self.nvars)]
        terms = []
        for exps, coeff in data.iteritems():
            factors = [PrimitiveAlgebra(coeff)]
            for s,e in zip(symbols, exps):
                if e:
                    if e==1:
                        factors.append(s)
                    else:
                        factors.append(s**e)
            if len(factors)==1:
                terms.append(factors[0])
            else:
                terms.append(PrimitiveAlgebra((MUL,tuple(factors))))
        if not terms:
            return PrimitiveAlgebra(0)
        if len(terms)==1:
            return terms[0]
        return PrimitiveAlgebra((ADD, tuple(terms)))


    def as_algebra(self, target_cls):
        cls = self.__class__
        if cls is target_cls:
            return self
        if issubclass(target_cls, PolynomialRing):
            target_ring = target_cls.ring
            if cls.nvars == target_cls.nvars:
                return target_cls(dict([(e,target_ring.convert(c)) for e,c in self.data.iteritems()]))
        return NotImplemented

    def __neg__(self):
        return self.__class__(dict([(e,-c) for e, c in self.data.iteritems()]))

    def __iadd__(self, other):
        other = self.convert(other)
        if other is NotImplemented:
            return other
        assert isinstance(other, self.__class__),`self, other`
        d = self.data
        for exps, coeff in other.data.iteritems():
            b = d.get(exps)
            if b is None:
                d[exps] = coeff
            else:
                c = b + coeff
                if c:
                    d[exps] = c
                else:
                    del d[exps]
        return self
        
    def __add__(self, other):
        other = self.convert(other)
        if other is NotImplemented:
            return other
        r = self.__class__(dict(self.data))
        r += other
        return r
