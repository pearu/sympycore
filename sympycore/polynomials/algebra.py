
from ..core import BasicType, classes
from ..utils import SYMBOL, NUMBER, ADD, MUL, POW
from ..basealgebra.ring import CommutativeRing
from ..basealgebra import PrimitiveAlgebra

class PolynomialRingGenerator(BasicType):
    """ Generator of polynomial rings:

    PolynomialRing[<n>, <ring>] - represents <n>-variate polynomial
    over coefficient <ring>.
    """
    def __new__(typ, name, bases, attrdict):
        if not attrdict.has_key('ring'):
            attrdict['ring'] = classes.Calculus
        if not attrdict.has_key('variables'):
            attrdict['variables'] = ()
            attrdict['nvars'] = 0
        cls = type.__new__(typ, name, bases, attrdict)
        return cls

    def __getitem__(self, ring_info, cache={}):
        """ Return a new polynomial ring class:

        PolynomialRing[<seq of variables>, <coefficient ring>]

        PolynomialRing[<n>, <coefficient ring>] is
              PolynomialRing[['X%s'%i for i in range(<n>)], <coefficient ring>]

        PolynomialRing[<variable info>] is
              PolynomialRing[<variable info>, Calculus]
        """
        if isinstance(ring_info, (int, long)):
            nvars = ring_info
            assert nvars>=0,`nvars`
            variables = ['X%s'%i for i in range(nvars)]
            ring = classes.Calculus
        elif isinstance(ring_info, tuple) and isinstance(ring_info[-1], type):
            if len(ring_info)==2:
                var_info, ring = ring_info
                if isinstance(var_info,(int, long)):
                    nvars = var_info
                    assert nvars>=0,`nvars`
                    variables = ['X%s'%i for i in range(nvars)]
                elif isinstance(var_info,(tuple, list, set)):
                    variables = var_info
                elif isinstance(var_info, str):
                    variables = var_info,
                else:
                    raise TypeError(`ring_info`)
            else:
                variables = ring_info[:-1]
                ring = ring_info[-1]
        elif isinstance(ring_info, (tuple, list, set)):
            variables = ring_info
            ring = classes.Calculus
        elif isinstance(ring_info, str):
            variables = ring_info,
            ring = classes.Calculus        
        else:
            raise TypeError(`ring_info`)
        variables = tuple(sorted(variables))
        nvars = len(variables)

        r = cache.get((variables, ring))
        if r is None:
            name = '%s[%s, %s]' % (self.__name__, tuple(map(str, variables)), ring.__name__)
            r = PolynomialRingGenerator(name,
                                        (self,),
                                        dict(nvars=nvars, ring = ring,
                                             variables = variables))
            cache[variables, ring] = r
        return r

def newinstance(cls, data):
    obj = object.__new__(cls)
    obj.data = data
    return obj


class PolynomialRing(CommutativeRing):
    """ Base class to polynomial rings.
    """

    __metaclass__ = PolynomialRingGenerator

    def __new__(cls, data, head=None):
        if head is None and isinstance(data, dict):
            pass
        elif head is SYMBOL:
            l = []
            try:
                i = list(cls.variables).index(data)
            except ValueError:
                i = None
            if i is None:
                cls = PolynomialRing[cls.variables+(data,), cls.ring]
                i = list(cls.variables).index(data)
            l = [0]*cls.nvars
            l[i] = 1
            data = {tuple(l):1}
        else:
            assert head is None,`head`
            return cls.convert(data)
        return newinstance(cls, data)

    def __eq__(self, other):
        return other.__class__ is self.__class__ and self.data == other.data

    @classmethod
    def Number(cls, obj):
        return newinstance(cls, {(0,)*cls.nvars: obj})

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
        symbols = [PrimitiveAlgebra(v) for v in self.variables]
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
            if cls.variables == target_cls.variables:
                data = dict([(e,target_ring.convert(c)) for e,c in self.data.iteritems()])
                return target_cls(data)
            if cls.ring == target_ring:
                new_cls = PolynomialRing[set(cls.variables + target_cls.variables), target_ring]
                new_variables = list(new_cls.variables)
                indices = [new_variables.index(v) for v in cls.variables]
                data = {}
                n = new_cls.nvars
                for e,c in self.data.iteritems():
                    new_e = [0] * n
                    for i,j in enumerate(indices):
                        new_e[j] = e[i]
                    data[tuple(new_e)] = c
                return new_cls(data)
        return NotImplemented

    def __neg__(self):
        return newinstance(self.__class__,dict([(e,-c) for e, c in self.data.iteritems()]))
        
    def __add__(self, other):
        cls = self.__class__
        other_cls = other.__class__
        if cls is other_cls:
            return add_POLY_POLY(self, other, cls)
        if not isinstance(other, PolynomialRing):
            other = self.convert(other)
            if other is NotImplemented:
                return other
            other_cls = other.__class__
        if cls is other_cls:
            return add_POLY_POLY(self, other, cls)
        elif self.nvars < other.nvars:
            return other + self
        return NotImplemented

def add_POLY_POLY(lhs, rhs, cls):
    d = dict(lhs.data)
    r = object.__new__(cls)
    r.data = d
    for exps, coeff in rhs.data.iteritems():
        b = d.get(exps)
        if b is None:
            d[exps] = coeff
        else:
            c = b + coeff
            if c:
                d[exps] = c
            else:
                del d[exps]
    return r

def mul_POLY_2(lhs, cls):
    d = {}
    r = object.__new__(cls)
    r.data = d
    for exps, coeff in lhs.data.iteritems():
        d[exps] = coeff*2
    return r
