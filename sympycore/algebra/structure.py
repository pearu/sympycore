
from ..core import Basic, classes, objects, sympify
from ..core.utils import singleton

class AlgebraicStructure(object):
    """ Defines base class for symbolic algebra structures.
    """

    @singleton
    def __new__(cls):
        return object.__new__(cls)

    @classmethod
    def coerce_term(cls, obj):
        """ Coerce obj to be used as an operant to + operation.

        Returns a pair (<kind>, <obj>) where <kind> is either TERMS,
        FACTORS, NUMBER, or ELEMENT and <obj> is coerced version
        of obj to be used as + operant.

        If <kind> is NUMBER then <obj> is treated as
          Terms([(<one>, <obj>)], structure=..)
        If <kind> is ELEMENT then <obj> is treated as
          Terms([(<obj>, 1)], structure=..)

        Here <one> is a identity element of an algebraic structure
        with respect to * operation.
        """
        raise NotImplementedError('%s coerce_term method' % cls)

    @classmethod
    def coerce_factor(cls, obj):
        """ Coerce obj to be used as an operant to * operation.

        Returns a pair (<kind>, <obj>) where <kind> is either TERMS,
        FACTORS, NUMBER, or ELEMENT and <obj> is coerced version
        of obj to be used as * operant.

        If <kind> is NUMBER then the caller should return
          Terms([(self, <obj>)], structure=..)
        If <kind> is ELEMENT then <obj> is treated as
          Factors([(<obj>, 1)], structure=..)

        """        
        raise NotImplementedError('%s coerce_factor method' % cls)

class SymbolicAlgebra(AlgebraicStructure):
    """ Defines commutative symbolic algebra (E, +, *, -, /, **, N, E)
    where E is a set of symbolic expressions and N is a set of numbers
    (Number instances).
    """

    @classmethod
    def coerce_term(cls, obj):
        obj = sympify(obj)
        if isinstance(obj, CommutativePairs):
            if type(obj.structure) is cls:
                return obj.kind, obj
            elif isinstance(obj.structure, cls):
                return NUMBER, obj
            # right-hand side method should be called as obj
            # is a NUMBER of rhs algebra structure.
            # XXX: what if rhs algebra structure has the same conclusion?
            return NotImplemented, obj
        if isinstance(obj, classes.Number):
            return NUMBER, obj
        return ELEMENT, obj
    
    coerce_factor = coerce_term

class NCSymbolicAlgebra(AlgebraicStructure):
    """ Defines noncommutative symbolic algebra (E, +, *, -, /, **, N, E)
    where E is a set of symbolic expressions and N is a set of numbers
    (Number instances or commutative elements).
    """

    @classmethod
    def coerce_term(cls, obj):
        obj = sympify(obj)
        if isinstance(obj, Pairs):
            if type(obj.structure) is cls:
                return obj.kind, obj
            elif isinstance(obj.structure, (cls, CommutativePairs):
                return NUMBER, obj
            # right-hand side method should be called as obj
            # is a NUMBER of rhs algebra structure.
            # XXX: what if rhs algebra structure has the same conclusion?
            return NotImplemented, obj
        if isinstance(obj, classes.Number):
            return NUMBER, obj
        # XXX: if obj is commutative, it should be treated as NUMBER
        return ELEMENT, obj
    
    coerce_factor = coerce_term

class Pairs:
    """ Base class for holding pairs (by default non-commutative).
    """
    def __init__(self, pairs):
        self._pairs = pairs
        self._hash = None

    @property
    def pairs(self):
        """ Return pairs as a tuple.
        """
        pairs = self._pairs
        if not isinstance(pairs, tuple):
            self._pairs = pairs = tuple(pairs)
        return pairs

    def iterator(self):
        pairs = self._pairs
        if isinstance(pairs, iterator_types):
            self._pairs = pairs = tuple(pairs)
            return pairs
        return iter(pairs)

    def length(self):
        """ Return the number of pairs.
        """
        pairs = self._pairs
        if isinstance(pairs, iterator_types):
            self._pairs = pairs = tuple(pairs)
            return len(pairs)
        return len(pairs)

class CommutativePairs(Pairs):

    @property
    def pairs(self):
        """ Return pairs as mutable dictionary.
        """
        pairs = self._pairs
        if not isinstance(pairs, dict):
            self._pairs = pairs = dict(pairs)
        return pairs

    def iterator(self):
        pairs = self._pairs
        if isinstance(pairs, iterator_types):
            self._pairs = pairs = dict(pairs)
            return pairs.iteritems()
        elif isinstance(pairs, dict):
            return pairs.iteritems()
        return iter(pairs)

    def length(self):
        """ Return the number of pairs.
        """
        pairs = self._pairs
        if isinstance(pairs, iterator_types):
            self._pairs = pairs = dict(pairs)
            return len(pairs)
        return len(pairs)
