# Author: Pearu Peterson
# Created: January 2008

__all__ = ['AlgebraicExpression', 'AlgebraicNumberExpression', 'as_ae']

from ..core import Basic, classes, objects
from ..core.sexpr import ELEMENT, NUMBER, TERMS, FACTORS

from .commutative import CommutativePairs

class AlgebraicExpression(Basic):
    """ Algebraic expression represents

    - a set element of an algebra
    - a result of binary operation +
    - a result of binary operation *
    - a number element of an algebra (see definition below)

    An operant of the operation + has a number coefficient that
    represents the repetition of the given operant in the operation.
    E.g. x * 3 means x + x + x. Number coefficient can also be
    fraction, algebraic number, or any other concept generalizing
    repetition notion.

    An operant of the operation * has integer exponent that also
    represents the repetition of the given operant in the operation.
    E.g. x ** 3 means x * x * x.

    An element of an algebra is represented as

      AlgebraicExpression(ELEMENT, obj)
      
    where obj can be any Python object that is hashable (this
    requirement is related to the implementation algorithm).

    The result of operation + is represented as

      AlgebraicExpression(TERMS, pairs)

    where pairs is a sequence or an iterator containing pairs

      (<AlgebraicExpression instance>, <number coefficient>).

    The result of operation * is represented as

      AlgebraicExpression(FACTORS, pairs)

    where pairs is a sequence or an iterator containing pairs

      (<AlgebraicExpression instance>, <exponent>).

    Commutativity and noncommutativity properties are defined via how
    the pairs is updated when performing operations. As an
    implementation example, for commutative algebras pairs can be a
    frozenset instance; for noncommutative algebras pairs can be a
    tuple instance.

    Algebra contains identity element zero with respect to + operation.

    Algebra contains identity element one with respect to * operation.

    A number element of an algebra is defined as

      one * <number>

    and is represented as

      AlgebraicExpression(NUMBER, <number>).

    The zero element of an algebra is represented as

      one * 0.

    Similarly, the one element of an algebra is represented as

      one * 1.

    Python operations + and * use the following rules when the LHS
    operant is an instance of AlgebraicExpression:
    
      - if RHS has the same class as LHS then result will be computed within
        given algebra.

      - if RHS is a subclass of the LHS class then it is considered
        as a number element of the LHS algebra.

      - if RHS is a superclass of the LHS class then the LHS is considered
        as a number element of the RHS algebra.

      - if RHS is not an AlgebraicExpression instance then it will be
        converted to one using RHS.as_ae(LHS.__class__).

    Examples:

      <Number>.as_ae(AlgebraicExpression) -> AlgebraicExpression(TERMS, [(one, <Number>)])

      <Symbol>.as_ae(AlgebraicExpression) -> AlgebraicExpression(TERMS, [(s, 1)])
        where s = AlgebraicExpression(ELEMENT, <Symbol>)

      <Power(2,5/3)>.as_ae(AlgebraicExpression) -> AlgebraicExpression(FACTORS, [(2, 5/3)])
    """

    def __init__(self, kind, data):
        self.kind = kind
        if (kind is TERMS or kind is FACTORS) and not isinstance(data, CommutativePairs):
            self.data = CommutativePairs(data)
        else:
            self.data = data

    def __repr__(self):
        return '%s(%r, %r)' % (self.__class__.__name__, self.kind, self.data)

    def __str__(self):
        k = self.kind
        d = self.data
        if k is ELEMENT:
            return str(d)
        if k is NUMBER:
            return str(d)
        if k is TERMS:
            return ' + '.join(['%s*%s' % tc for tc in d])
        if k is FACTORS:
            return ' * '.join(['%s**%s' % tc for tc in d])
        raise NotImplementedError('str(%r)')
        
    def __add__(self, other):
        cls = self.__class__
        other = as_ae(other, cls)
        k1, k2 = self.kind, other.kind
        d1, d2 = self.data, other.data
        if k1 is ELEMENT:
            if k2 is ELEMENT:
                if d1==d2:
                    return cls(TERMS, [(self, 2)])
                return cls(TERMS, [(self, 1), (other, 1)])
            if k2 is NUMBER:
                if d2==0:
                    return self
                return cls(TERMS, [(self, 1), (1, other)])
            if k2 is TERMS:
                r = cls(TERMS, other)
                r.data.sum_add_element(self, 1, 0)
                return r # XXX: canonize
            if k2 is FACTORS:
                return cls(TERMS, [(self, 1), (other, 1)])
        elif k1 is NUMBER:
            if k2 is NUMBER:
                if d2==0:
                    return self
                return cls(NUMBER, d1 + d2)
            if k2 is ELEMENT:
                return cls(TERMS, [(self, 1), (other, 1)])
            if k2 is TERMS:
                r = cls(TERMS, d2)
                r.data.sum_add_number(d1, 1, 0) ## lhs add
                return r # XXX: canonize
            if k2 is FACTORS:
                return cls(TERMS, [(self, 1), (other, 1)])
        elif k1 is TERMS:
            if k2 is NUMBER:
                if d2==0:
                    return self
                r = cls(TERMS, d1)
                r.data.sum_add_number(d2, 1, 0)
                return r # XXX: canonize
            if k2 is ELEMENT:
                r = cls(TERMS, d1)
                r.data.sum_add_element(other, 1, 0)
                return r # XXX: canonize
            if k2 is TERMS:
                r = cls(TERMS, d1)
                r.data.sum_add_sum(d2, 1, 0)
                return r # XXX: canonize
            if k2 is FACTORS:
                r = cls(TERMS, d1)
                r.data.sum_add_element(other, 1, 0)
                return r # XXX: canonize
        elif k1 is FACTORS:
            if k2 is NUMBER:
                if d2==0:
                    return self
                return cls(TERMS, [(self, 1), (other, 1)])
            if k2 is ELEMENT:
                return cls(TERMS, [(self, 1), (other, 1)])
            if k2 is TERMS:
                r = cls(TERMS, other)
                r.data.sum_add_element(self, 1, 0) ## lhs add
                return r # XXX: canonize
            if k2 is FACTORS:
                if d1==d2: # XXX fix __eq__ when d1,d2 are different sequences of pairs
                    return cls(TERMS, [(self, 2)])
                return cls(TERMS, [(self, 1), (other, 1)])
        raise NotImplementedError('%s + %s' % (self, other))

    def __mul__(self, other):
        cls = self.__class__
        other = as_ae(other, cls)
        k1, k2 = self.kind, other.kind
        d1, d2 = self.data, other.data
        if k1 is ELEMENT:
            if k2 is ELEMENT:
                if d1==d2:
                    return cls(FACTORS, [(self, 2)])
                return cls(FACTORS, [(self, 1), (other, 1)])
            if k2 is NUMBER:
                if d2==0:
                    return other
                return cls(TERMS, [(self, d2)])
            if k2 is TERMS:
                return cls(FACTORS, [(self, 1), (other,1)])
            if k2 is FACTORS:
                # XXX for commutative producs use r=cls(FACTORS, d2), then there will be no loop
                r = cls(FACTORS,[(self,1)])
                r.product_mul_product(other, 1, 0)
                return r # XXX: canonize
        elif k1 is NUMBER:
            if k2 is NUMBER:
                if d2==0:
                    return other
                return cls(NUMBER, d1 * d2)
            if k2 is ELEMENT:
                return cls(TERMS, [(other, d1)]) # XXX: commutativity
            if k2 is TERMS:
                r = cls(TERMS, d2)
                r.data.sum_multiply_number(d1, 1, 0) ## lhs multiply, fix for noncom. product
                return r # XXX: canonize
            if k2 is FACTORS:
                return cls(TERMS, [(self, 1), (other, 1)])
        elif k1 is TERMS:
            if k2 is NUMBER:
                if d2==0:
                    return other
                r = cls(TERMS, d1)
                r.data.sum_multiply_number(d2, 1, 0)
                return r # XXX: canonize
            if k2 is ELEMENT:
                return cls(FACTORS, [(self, 1), (other,1)])
            if k2 is TERMS:
                r = cls(TERMS, d1)
                r.data.sum_multiply_sum(d2, 1, 0)
                return r # XXX: canonize
            if k2 is FACTORS:
                return cls(FACTORS, [(self, 1), (other, 1)])
        elif k1 is FACTORS:
            if k2 is NUMBER:
                if d2==0:
                    return other
                return cls(FACTORS, [(self, 1), (other, 1)])
            if k2 is ELEMENT:
                r = cls(FACTORS, d1)
                r.data.product_multiply_element(other, 1, 0)
                return r # XXX: canonize
            if k2 is TERMS:
                return cls(FACTORS, [(self, 1), (other, 1)])
            if k2 is FACTORS:
                r = cls(FACTORS, d1)
                if d1==d2: # XXX fix __eq__ when d1,d2 are different sequences of pairs
                    r.data.product_power_exponent(2, 1, 0)
                    return r # XXX: canonize
                r.data.product_multiply_product(d2, 1, 0)
                return r # XXX: canonize
        raise NotImplementedError('%s * %s' % (self, other))

    def __radd__(self, other):
        return self + other # XXX: assumes commutativity

    def __rmul__(self, other):
        return self * other # XXX: assumes commutativity

    def __hash__(self):
        return hash((self.kind, self.data))

    def __eq__(self, other):
        if other.__class__ is not self.__class__:
            return False
        if self.kind is not other.kind:
            return False
        return self.data == other.data

class AlgebraicNumberExpression(AlgebraicExpression):
    """ Represents algebraic numbers.

    Here elements of the algebra are minimal roots of numbers, numbers,
    and results of operations + and *. E.g. 2**(4/3) is represented as

      AlgebraicNumberExpression(FACTORS,[(2,4/3)])
    """

def as_ae(obj, cls = AlgebraicExpression):
    """ Return obj as algebraic expression.
    """
    objcls = obj.__class__
    if objcls is cls:
        return obj
    if issubclass(objcls, cls):
        return cls(NUMBER, obj)
    if issubclass(cls, objcls):
        return obj
    if isinstance(obj, (classes.Number, int, long, float, complex)):
        return cls(NUMBER, obj)
    return cls(ELEMENT, obj)
