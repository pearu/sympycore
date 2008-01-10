
from ..core import sympify, classes
from .pairs import CommutativePairs
from .algebraic_structures import BasicAlgebra
from .primitive import PrimitiveAlgebra, SYMBOL, NUMBER, ADD, MUL


class StandardCommutativeAlgebra(BasicAlgebra):
    """ Represents an element of a symbolic algebra. The set of a
    symbolic algebra is a set of expressions. There are four kinds of
    expressions: Symbolic, SymbolicNumber, SymbolicTerms,
    SymbolicFactors.

    StandardCommutativeAlgebra basically models the structure of SymPy.
    """

    def __new__(cls, obj, kind=None):
        if isinstance(obj, StandardCommutativeAlgebra):
            return obj
        if kind is None:
            if isinstance(obj, (str, unicode)):
                obj = PrimitiveAlgebra(obj)
            if isinstance(obj, PrimitiveAlgebra):
                return obj.as_algebra(cls)
            if isinstance(obj, BasicAlgebra):
                # XXX: need another way to specify coefficent and exponent algebras
                kind = NUMBER
            elif isinstance(obj, classes.Number):
                kind = NUMBER
            elif isinstance(obj, (int, long, float, complex)):
                obj = sympify(obj)
                kind = NUMBER
            else:
                kind = SYMBOL
        if kind is SYMBOL:
            return Symbolic(obj)
        if kind is NUMBER:
            return SymbolicNumber(obj)
        if kind is ADD:
            return SymbolicTerms(obj)
        if kind is MUL:
            return SymbolicFactors(obj)
        return NotImplementedError(`cls, obj, kind`)

    @staticmethod
    def convert(obj):
        return StandardCommutativeAlgebra(obj)

    @staticmethod
    def Add(seq):
        terms = SymbolicTerms({})
        for term in seq:
            term = StandardCommutativeAlgebra(term)
            kind = term.kind
            if kind is SYMBOL:
                terms._add_value(term, 1, 0)
            elif kind is NUMBER:
                terms._add_value(1, term.data, 0)
            elif kind is ADD:
                terms._add_values(term, 1, 0)
            elif kind is MUL:
                terms._add_value(term, 1, 0)
            else:
                raise TypeError(`term, kind`)
        return terms.canonize()

    @staticmethod
    def Mul(seq):
        factors = SymbolicFactors({})
        number = 1
        for factor in seq:
            factor = StandardCommutativeAlgebra(factor)
            kind = factor.kind
            if kind is SYMBOL:
                factors._add_value(factor, 1, 0)
            elif kind is NUMBER:
                number = number * factor.data
            elif kind is ADD:
                factors._add_value(factor, 1, 0)
            elif kind is MUL:
                factors._add_values(factor, 1, 0)
            else:
                raise TypeError(`factor, kind`)
        factors = factors.canonize()
        if number==1:
            return factors
        if factors==1:
            return number
        kind = factors.kind
        if kind is NUMBER:
            return self.convert(factors.data * number)
        if kind is ADD:
            r = SymbolicTerms(iter(factors))
            r._multiply_values(number, 1, 0)
            return r.canonize()
        return SymbolicTerms({factors:number})

    @staticmethod
    def Pow(base, exp):
        return SymbolicFactors({base:exp})

    def __repr__(self):
        return '%s(%r)' % (type(self).__name__, self.data)

    def canonize(self):
        return self
    
class Symbolic(StandardCommutativeAlgebra): # rename to Symbol?

    kind = SYMBOL
    
    def __new__(cls, obj):
        o = object.__new__(cls)
        o.data = obj
        return o

    def __str__(self):
        return str(self.data)

    def as_primitive(self):
        return PrimitiveAlgebra((SYMBOL, self.data))

    def __eq__(self, other):
        other = StandardCommutativeAlgebra(other)
        if self.kind != other.kind:
            return False
        return self.data == other.data

    def __hash__(self):
        return hash((type(self), self.data))

    def __mul__(self, other):
        other = self.convert(other)
        kind = other.kind
        if kind is NUMBER:
            return SymbolicTerms({self:other.data})
        if kind is SYMBOL:
            if self.data == other.data:
                return SymbolicTerms({self:2})
            return SymbolicTerms({self:1, other:1})
        if kind is ADD:
            r = SymbolicTerms(other)
            r._add_value(self, 1, 0)
            return r.canonize()
        if kind is MUL:
            return SymbolicTerms({self:other.data})
        raise NotImplementedError('%s * %s' % (self, other))

class SymbolicNumber(StandardCommutativeAlgebra): # rename to Number?

    kind = NUMBER

    def __new__(cls, obj):
        o = object.__new__(cls)
        o.data = obj
        return o

    def __str__(self):
        return str(self.data)

    def as_primitive(self):
        return PrimitiveAlgebra((NUMBER, self.data))

    def __eq__(self, other):
        other = self.convert(other)
        if self.kind != other.kind:
            return False
        return self.data == other.data

    def __hash__(self):
        # XXX: cache hash
        return hash((type(self), self.data))

    def __mul__(self, other):
        other = self.convert(other)
        kind = other.kind
        if kind is NUMBER:
            return SymboliNumber(self.data * other.data)
        if kind is SYMBOL:
            return SymbolicTerms({other:self.data})
        if kind is ADD:
            r = SymbolicTerms(other)
            r._add_value(1, self.data, 0)
            return r # XXX: canonize
        if kind is MUL:
            return SymbolicTerms({other:self.data})
        raise NotImplementedError('%s * %s' % (self, other))
        
class SymbolicTerms(CommutativePairs, StandardCommutativeAlgebra):

    kind = ADD

    __new__ = CommutativePairs.__new__
    __str__ = BasicAlgebra.__str__
    
    def as_primitive(self):
        l = []
        for t,c in self:
            t = PrimitiveAlgebra(t)
            if c==1:
                l.append(t)
            elif t==1:
                l.append(PrimitiveAlgebra(c))
            else:
                l.append(t * c)
        if len(l)==1:
            return l[0]
        return PrimitiveAlgebra((ADD,tuple(l)))

    def canonize(self):
        pairs = self.pairs
        if not pairs:
            return SymbolicNumber(0)
        if len(pairs)==1:
            t, c = pairs.items()[0]
            if c==1:
                return t
            if t==1:
                return c
        return self

class SymbolicFactors(CommutativePairs, StandardCommutativeAlgebra):
    
    kind = MUL

    __new__ = CommutativePairs.__new__
    __str__ = BasicAlgebra.__str__

    def as_primitive(self):
        l = []
        for t,c in self:
            t = PrimitiveAlgebra(t)
            if c==1:
                l.append(t)
            else:
                l.append(t ** c)
        if len(l)==1:
            return l[0]
        return PrimitiveAlgebra((MUL,tuple(l)))

    def canonize(self):
        pairs = self.pairs
        if not pairs:
            return SymbolicNumber(1)
        if len(pairs)==1:
            t, c = pairs.items()[0]
            if c==1:
                return t
            if t==1:
                return t
        return self
