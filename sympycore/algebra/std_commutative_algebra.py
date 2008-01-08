
from ..core import sympify
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
        return terms # XXX: canonize

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
        if number==1:
            return factors # XXX: canonize
        return SymbolicTerms({factors:number})

    @staticmethod
    def Pow(base, exp):
        return SymbolicFactors({base:exp})

    def __repr__(self):
        return '%s(%r)' % (type(self).__name__, self.data)

    
class Symbolic(StandardCommutativeAlgebra): # rename to Symbol?

    kind = SYMBOL
    
    def __new__(cls, obj):
        o = object.__new__(cls)
        o.data = obj
        return o

    def __str__(self):
        return str(self.data)

    def as_PrimitiveAlgebra(self):
        return PrimitiveAlgebra((SYMBOL, self.data))

    def __eq__(self, other):
        other = StandardCommutativeAlgebra(other)
        if self.kind != other.kind:
            return False
        return self.data == other.data

    def __hash__(self):
        return hash((type(self), self.data))

class SymbolicNumber(StandardCommutativeAlgebra): # rename to Number?

    kind = NUMBER

    def __new__(cls, obj):
        o = object.__new__(cls)
        o.data = obj
        return o

    def __str__(self):
        return str(self.data)

    def as_PrimitiveAlgebra(self):
        return PrimitiveAlgebra((NUMBER, self.data))

    def __eq__(self, other):
        other = StandardCommutativeAlgebra(other)
        if self.kind != other.kind:
            return False
        return self.data == other.data

    def __hash__(self):
        return hash((type(self), self.data))

class SymbolicTerms(CommutativePairs, StandardCommutativeAlgebra):

    kind = ADD

    __new__ = CommutativePairs.__new__
    __str__ = BasicAlgebra.__str__
    
    def as_PrimitiveAlgebra(self):
        l = []
        for t,c in self:
            t = PrimitiveAlgebra(t)
            if c==1:
                l.append(t)
            elif t==1:
                l.append(PrimitiveAlgebra(c))
            else:
                l.append(PrimitiveAlgebra(t) * PrimitiveAlgebra(c))
        return PrimitiveAlgebra((ADD,tuple(l)))

class SymbolicFactors(CommutativePairs, StandardCommutativeAlgebra):
    
    kind = MUL

    __new__ = CommutativePairs.__new__
    __str__ = BasicAlgebra.__str__

    def as_PrimitiveAlgebra(self):
        l = []
        for t,c in self:
            if c==1:
                l.append(PrimitiveAlgebra(t))
            else:
                l.append(PrimitiveAlgebra(t) ** PrimitiveAlgebra(c))
        return PrimitiveAlgebra((MUL,tuple(l)))
