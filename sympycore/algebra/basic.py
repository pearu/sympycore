# Author: Pearu Peterson
# Created: January 2008

from ..core import Basic, classes, objects
from ..core.sexpr import ELEMENT, NUMBER, TERMS, FACTORS

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
    E.g. x ** 3 means x * x * x. The exponent must be integer.

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

      (<AlgebraicExpression instance>, <integer exponent>).

    Commutativity and noncommutativity properties are defined in how
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

    Fractional powers are represented as powers of a minimal root
    (that has exponent with a numerator equal to 1) where the root
    expression is considered as an element of an algebra. E.g.
    x**(2/3) is equal to (x**(1/3)) ** 2 and is represented as

      AlgebraicExpression(FACTORS,
                      [(AlgebraicExpression(ELEMENT, x**(1/3)), 2)])

    where y=x**(1/3) is a solution of x==y**3 with respect to y and is
    represented as

      Root(x, 3).

    Symbolic powers are considered as elements of an algebra.
    E.g x**y is represented as
    
      AlgebraicExpression(ELEMENT, x**y)

    where x**y is represented as Power(x, y).

    More examples:
     x**(2/3*y) is represented as

      AlgebraicExpression(FACTORS,
                         [(AlgebraicExpression(ELEMENT, Power(x,1/3*y)) , 2)] )

     x**(2/3*y + 4/5) is rewritten as (x**(1/3*y+2/5), 2)

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

      <Number>.as_ae(AlgebraicExpression) -> AlgebraicExpression(TERMS,[(one, <Number>)])

      <Symbol>.as_ae(AlgebraicExpression) -> AlgebraicExpression(TERMS,[(s, 1)])
        where s = AlgebraicExpression(ELEMENT, <Symbol>)

      <Power(2,5/3)>.as_ae(AlgebraicExpression) -> AlgebraicExpression(FACTORS,[(s, 5)])
        where s = AlgebraicExpression(ELEMENT, <Power(2,1/3)>)
    """

    def __init__(self, kind, data):
        self.kind = kind
        self.data = data
        
    def __add__(self, other):
        k1, k2 = self.kind, other.kind
        d1, d2 = self.data, other.data
        if k1 is ELEMENT and k2 is ELEMENT:
            if d1==d2:
                return AlgebraicExpression(FACTORS, [(self, 2)])
            return AlgebraicExpression(TERMS, [(self, 1), (other, 1)])
        raise NotImplementedError('%s + %s' % (self, other))

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

class AlgebraicNumberExpression(AlgebraicExpression):
    """ Represents algebraic numbers.

    Here elements of the algebra are minimal roots of numbers, numbers,
    and results of operations + and *. E.g. 2**(4/3) is represented as

      AlgebraicNumberExpression(FACTORS,
        [(AlgebraicNumberExpression(ELEMENT, Root(2,3)), 4)])
    """
