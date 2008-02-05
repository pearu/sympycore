#
# Author: Pearu Peterson
# Created: February 2008
#

from ..core import BasicType, classes
from ..utils import SYMBOL, NUMBER, ADD, MUL, POW
from ..basealgebra.ring import CommutativeRing
from ..basealgebra import PrimitiveAlgebra

class PolynomialRingFactory(BasicType):
    """ Factory of polynomial rings with symbols and coefficient ring.
    """
    def __new__(typ, name, bases, attrdict):
        if not attrdict.has_key('ring'):
            attrdict['ring'] = classes.Calculus
        if not attrdict.has_key('variables'):
            attrdict['variables'] = ()
            attrdict['nvars'] = 0
        cls = type.__new__(typ, name, bases, attrdict)
        cls.zero = cls.Number(0)
        cls.one = cls.Number(1)
        return cls

    def __eq__(self, other):
        if isinstance(other, PolynomialRingFactory):
            return self.ring==other.ring and self.variables==other.variables
        return False

    def __ne__(self, other):
        return not self==other

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

        r = None #cache.get((variables, ring))
        if r is None:
            name = '%s[%s, %s]' % (self.__name__, tuple(map(str, variables)), ring.__name__)
            r = PolynomialRingFactory(name,
                                      (self,),
                                      dict(nvars=nvars, ring = ring,
                                           variables = variables))
            #cache[variables, ring] = r
        return r

    def is_subring(self, other):
        """ Check if self contains other as a subring, i.e. whether
        the other instances can be converted to self instances.
        """
        if not isinstance(other, PolynomialRingFactory):
            return False
        if self.ring != other.ring:
            return False
        return set(other.variables).issubset(self.variables)

def newinstance(cls, data):
    obj = object.__new__(cls)
    obj.data = data
    return obj


class AdditiveTuple(tuple):
    """ A tuple that can be added element-wise.

    Properties:
      AdditiveTuple(obj) -> obj
      AdditiveTuple([obj]) -> obj
      AdditiveTuple([obj1, obj2]) + [r1,r2] -> AdditiveTuple([obj1+r1, obj2+r2])
    """

    def __new__(cls, arg):
        if isinstance(arg, (tuple, list, set)):
            if len(arg)==1:
                return arg[0]
            return tuple.__new__(cls, arg)
        return arg

    def __add__(self, other):
        return self.__class__([self[i] + other[i] for i in xrange(len(self))])


class PolynomialRing(CommutativeRing):
    """ Base class to polynomial rings that holds polynomial information
    using pairs (<exponents>: <coefficient>) stored in Python dictionary.
    """

    __metaclass__ = PolynomialRingFactory

    def __new__(cls, data):
        if not isinstance(data, dict):
            return cls.convert(data)
        return newinstance(cls, data)

    def __eq__(self, other):
        return other.__class__ is self.__class__ and self.data == other.data

    @classmethod
    def Symbol(cls, obj):
        """ Return symbol element of a polynomial ring. The result
        may be an instance of super polynomial ring.

        r = PolynomialRing['x']
        r.Symbol('x') -> r({1:1})
        r.Symbol('y') -> PolynomialRing['x','y']({(0,1):1})
        """
        try:
            i = list(cls.variables).index(obj)
        except ValueError:
            i = None
        if i is None:
            cls = PolynomialRing[cls.variables+(obj,), cls.ring]
            i = list(cls.variables).index(obj)
        l = [0]*cls.nvars
        l[i] = 1
        return newinstance(cls, {AdditiveTuple(l):1})

    @classmethod
    def Number(cls, obj):
        """ Return number element of a polynomial ring.

        r = PolynomialRing['x']
        r.Number(2) -> r({0:2})
        """
        if obj:
            return newinstance(cls, {AdditiveTuple((0,)*cls.nvars): obj})
        return newinstance(cls, {})

    @classmethod
    def Add(cls, *seq):
        r = cls({})
        for t in seq:
            tcls = t.__class__
            if cls==tcls:
                iadd_POLY_POLY(r, t, cls)
            elif cls.is_subring(tcls):
                t = t.as_algebra(cls)
                assert cls==t.__class__,`cls,t`
                iadd_POLY_POLY(r, t, cls)
            elif tcls.is_subring(cls):
                cls = tcls
                r = r.as_algebra(cls)
                iadd_POLY_POLY(r, t, cls)
            elif cls.ring==tcls.ring:
                cls = PolynomialRing[cls.variables+tcls.variables, cls.ring]
                r = r.as_algebra(cls)
                t = t.as_algebra(cls)
                iadd_POLY_POLY(r, t, cls)
            else:
                raise NotImplementedError(`r, t`)
        if not r.data:
            return cls.Number(0)
        return r

    @classmethod
    def Mul(cls, *seq):
        r = cls.one
        for t in seq:
            tcls = t.__class__
            if cls==tcls:
                r = mul_POLY_POLY(r, t, cls)
            elif cls.is_subring(tcls):
                t = t.as_algebra(cls)
                assert cls==t.__class__,`cls,t`
                r = mul_POLY_POLY(r, t, cls)
            elif tcls.is_subring(cls):
                cls = tcls
                r = r.as_algebra(cls)
                r = mul_POLY_POLY(r, t, cls)
            elif cls.ring==tcls.ring:
                cls = PolynomialRing[cls.variables+tcls.variables, cls.ring]
                r = r.as_algebra(cls)
                t = t.as_algebra(cls)
                r = mul_POLY_POLY(r, t, cls)
            else:
                raise NotImplementedError(`r, t`)
        if not r.data:
            return cls.Number(1)
        return r

    @classmethod
    def convert_coefficient(cls, obj, typeerror=True):
        r = cls.ring.convert_coefficient(obj, typeerror=False)
        if r is not None:
            return r
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
        for exps in sorted(data.keys(), reverse=True):
            coeff = data[exps]
            if coeff==1:
                factors = []
            else:
                factors = [PrimitiveAlgebra(coeff)]
            if not isinstance(exps, tuple):
                exps = exps,
            for s,e in zip(symbols, exps):
                if e:
                    if e==1:
                        factors.append(s)
                    else:
                        factors.append(s**e)
            if not factors:
                terms.append(PrimitiveAlgebra(coeff))
            elif len(factors)==1:
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
                    if not isinstance(e, tuple):
                        e = e,
                    for i,j in enumerate(indices):
                        new_e[j] = e[i]
                    data[AdditiveTuple(new_e)] = c
                return new_cls(data)
        return NotImplemented

    def __neg__(self):
        return newinstance(self.__class__,dict([(e,-c) for e, c in self.data.iteritems()]))
        
    def __add__(self, other):
        cls = self.__class__
        other_cls = other.__class__
        if cls is other_cls:
            return add_POLY_POLY(self, other, cls)
        other = self.convert(other)
        if other is NotImplemented:
            return other
        other_cls = other.__class__
        if cls is other_cls:
            return add_POLY_POLY(self, other, cls)
        elif self.nvars < other.nvars:
            return other + self
        return NotImplemented

    def __mul__(self, other):
        cls = self.__class__
        other_cls = other.__class__
        if cls is other_cls:
            return mul_POLY_POLY(self, other, cls)
        other = self.convert_coefficient(other, typeerror=False)
        if other is not NotImplemented:
            return mul_POLY_COEFF(self, other, cls)
        other = self.convert(other, typeerror=False)
        if other is NotImplemented:
            return other
        other_cls = other.__class__
        if cls is other_cls:
            return mul_POLY_POLY(self, other, cls)
        elif self.nvars < other.nvars:
            return other * self
        return NotImplemented

    __rmul__ = __mul__

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

def iadd_POLY_POLY(lhs, rhs, cls):
    d = lhs.data
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
    

def mul_POLY_POLY(lhs, rhs, cls):
    r = object.__new__(cls)
    r.data = d = {}
    for exps1, coeff1 in lhs.data.iteritems():
        for exps2, coeff2 in rhs.data.iteritems():
            exps = exps1 + exps2
            coeff = coeff1 * coeff2
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

def mul_POLY_COEFF(lhs, rhs, cls):
    r = object.__new__(cls)
    r.data = d = {}
    for exps, coeff in lhs.data.iteritems():
        b = d.get(exps)
        if b is None:
            d[exps] = coeff * rhs
        else:
            c = b + coeff * rhs
            if c:
                d[exps] = c
            else:
                del d[exps]
    return r
