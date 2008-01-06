
from ..core import Basic, classes, objects

class AlgebraicExpression(Basic):
    """ Algebraic expression represents

    - a set element of an algebra
    - a result of binary operation +
    - a result of binary operation *

    An operant of the operation + has number coefficient that
    represents a repetition of the given operant in the operation.

    An operant of the operation * has integer exponent that also
    represents a repetition of the given operant in the operation.

    Algebra contains identity element zero with respect to + operation.
    Algebra contains identity element one with respect to * operation.

    An element of an algebra is represented as

      AlgebraicExpression(SYMBOLIC, obj)
      
    where obj can be any Python object that is hashable.

    A result of the operation + is represented as

      AlgebraicExpression(TERMS, pairs)

    where pairs is a sequence or iterator containing pairs

      (<AlgebraicExpression instance>, <number coefficient>)

    A result of the operation * is represented as

      AlgebraicExpression(FACTORS, pairs)

    where pairs is a sequence or iterator containing pairs

      (<AlgebraicExpression instance>, <integer exponent>)

    A number element of an algebra is defined as

      one * <number>

    and represented as

      AlgebraicExpression(TERMS, [(one, <number>)])

    """

    def __new__(cls, kind, expr):
        obj = object.__new__(cls)
        
