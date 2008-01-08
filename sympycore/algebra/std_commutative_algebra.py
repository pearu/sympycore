
from .pairs import CommutativePairs
from .algebraic_structures import AlgebraicStructure

NUMBER = intern('N')
SYMBOLIC = intern('S')
TERMS = intern('+')
FACTORS = intern('*')

class StandardCommutativeAlgebra(AlgebraicStructure):
    """ Represents an element of a symbolic algebra. The set of a
    symbolic algebra is a set of expressions. There are four kinds of
    expressions: Symbolic, SymbolicNumber, SymbolicTerms,
    SymbolicFactors.

    StandardCommutativeAlgebra basically models the structure of SymPy.
    """

    def __new__(cls, obj, kind=None):
        if isinstance(obj, cls):
            return obj
        if kind is None:
            if isinstance(obj, cls):
                # XXX: need another way to specify coefficent and exponent algebras
                kind = NUMBER
            elif isinstance(obj, (int, long, float, complex)):
                obj = sympify(obj)
                kind = NUMBER
            else:
                kind = SYMBOLIC
        if kind is SYMBOLIC:
            return Symbolic(obj)
        if kind is NUMBER:
            return SymbolicNumber(obj)
        if kind is TERMS:
            return SymbolicTerms(obj)
        if kind is FACTORS:
            return SymbolicFactors(obj)
        return NotImplementedError(`cls, obj, kind`)

    @staticmethod
    def Add(seq):
        terms = SymbolicTerms({})
        for term in seq:
            term = StandardCommutativeAlgebra(term)
            kind = term.kind
            if kind is SYMBOLIC:
                terms._add_value(term, 1, 0)
            elif kind is NUMBER:
                terms._add_value(1, term.data, 0)
            elif kind is TERMS:
                terms._add_values(term, 1, 0)
            elif kind is FACTORS:
                terms._add_value(term, 1, 0)
            else:
                raise TypeError(`term, kind`)
        return terms # XXX: canonize

    @staticmethod
    def Mul(seq):
        factors = SymbolicFactors({})
        number = 1
        for factor in seq:
            factor = StandardCommutativeAlgebra(factor)
            kind = factor.kind
            if kind is SYMBOLIC:
                factors._add_value(factor, 1, 0)
            elif kind is NUMBER:
                number = number * factor.data
            elif kind is TERMS:
                factors._add_value(factor, 1, 0)
            elif kind is FACTORS:
                factors._add_values(factor, 1, 0)
            else:
                raise TypeError(`factor, kind`)
        if number==1:
            return factors # XXX: canonize
        return SymbolicTerms({factors:number})

    @staticmethod
    def Pow(base, exp):
        return SymbolicFactors({base:exp})

    def __neg__(self):
        return self.Mul([self, -1])

    def __add__(self, other):
        return self.Add([self, other])

    def __sub__(self, other):
        return self + (-other)

    def __mul__(self, other):
        return self.Mul([self, other])

    def __div__(self, other):
        return self.Mul([self, self.Pow(other,-1)])

    def __repr__(self):
        return '%s(%r)' % (type(self).__name__, self.data)
    
class Symbolic(StandardCommutativeAlgebra): # rename to Symbol?

    kind = SYMBOLIC
    
    def __new__(cls, obj):
        o = object.__new__(cls)
        o.data = obj
        return o

    def __str__(self):
        return str(self.data)

class SymbolicNumber(StandardCommutativeAlgebra): # rename to Number?

    kind = NUMBER
    def __new__(cls, obj):
        o = object.__new__(cls)
        o.data = obj
        return o

    def __str__(self):
        return str(self.data)

class SymbolicTerms(CommutativePairs, StandardCommutativeAlgebra):

    kind = TERMS

    __new__ = CommutativePairs.__new__

    def as_PrimitiveAlgebra(self):
        l = []
        for t,c in self:
            if c==1:
                l.append(PrimitiveAlgebra(t))
            elif t==1:
                l.append(PrimitiveAlgebra(c))
            else:
                l.append(PrimitiveAlgebra(t) * PrimitiveAlgebra(c))
        return PrimitiveAlgebra(('+',)+tuple(l))

class SymbolicFactors(CommutativePairs, StandardCommutativeAlgebra):
    
    kind = FACTORS

    __new__ = CommutativePairs.__new__

    def as_PrimitiveAlgebra(self):
        l = []
        for t,c in self:
            if c==1:
                l.append(PrimitiveAlgebra(t))
            else:
                l.append(PrimitiveAlgebra(t) ** PrimitiveAlgebra(c))
        return PrimitiveAlgebra(('*',)+tuple(l))
