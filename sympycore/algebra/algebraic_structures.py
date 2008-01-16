
from ..core import Basic, classes, objects, sympify, BasicType

class AlgebraicStructure(Basic):
    """ Represents an element of an algebraic structure.
    Subclasses will define operations between elements if any.
    """

    @classmethod
    def convert_exponent(cls, obj):
        return int(obj)

    def as_primitve(self):
        raise NotImplementedError('%s must define as_primitive method'\
                                  % (type(self).__name__))

    def __str__(self):
        return str(self.as_primitive())

class BasicAlgebra(AlgebraicStructure):
    """ Collects implementation specific methods of algebra classes.
    
    They must be all compatible with PrimitiveAlgebra class via
    defining as_primitive method.

    The recommended way to construct + and * operation results is to
    define Add, Mul, Pow static methods which are used by default
    __add__, __mul__ etc methods.
    """
    @classmethod
    def convert(cls, obj, typeerror=True):
        algebra_class = cls.algebra_class
        if isinstance(obj, algebra_class):
            return obj
        if isinstance(obj, cls.algebra_numbers):
            return cls(obj, head=NUMBER)
        if isinstance(obj, (str, unicode)):
            obj = PrimitiveAlgebra(obj)
        if isinstance(obj, PrimitiveAlgebra):
            return obj.as_algebra(cls.algebra_class)
        if isinstance(obj, BasicAlgebra):
            return obj.as_primitive().as_algebra(cls.algebra_class)
        if typeerror:
            raise TypeError('%s.convert(<%s object>)' % (cls.__name__, type(obj)))
        else:
            return NotImplemented
        return obj

    def as_algebra(self, cls, source=None):
        """
        """
        # XXX: cache primitive algebras
        if cls is classes.PrimitiveAlgebra:
            return self.as_primitive()
        return self.as_primitive().as_algebra(cls, source=self)

    @classmethod
    def Symbol(cls, obj):
        raise NotImplementedError('%s must define classmethod Symbol' % (cls.__name__))

    @classmethod
    def Number(cls, num, denom=None):
        raise NotImplementedError('%s must define classmethod Number' % (cls.__name__))

    @classmethod
    def Add(cls, seq):
        raise NotImplementedError('%s must define classmethod Add' % (cls.__name__))

    @classmethod
    def Mul(cls, seq):
        raise NotImplementedError('%s must define classmethod Mul' % (cls.__name__))

    @classmethod
    def Pow(cls, base, exponent):
        raise NotImplementedError('%s must define classmethod Pow' % (cls.__name__))

    def __pos__(self):
        return self

    def __neg__(self):
        return self.Mul([self, -1])

    #XXX: need to deal with other algebras where self is a number, should return NotImplemented
    def __add__(self, other):
        other = self.convert(other)
        return self.Add([self, other])

    def __radd__(self, other):
        other = self.convert(other)
        return self.Add([other, self])

    def __sub__(self, other):
        other = self.convert(other)
        return self + (-other)

    def __rsub__(self, other):
        other = self.convert(other)
        return other + (-self)

    def __mul__(self, other):
        other = self.convert(other)
        return self.Mul([self, other])

    def __rmul__(self, other):
        other = self.convert(other)
        return self.Mul([other, self])

    def __div__(self, other):
        other = self.convert(other)
        return self.Mul([self, self.Pow(other,-1)])

    def __rdiv__(self, other):
        other = self.convert(other)
        return self.Mul([other, self.Pow(self,-1)])

    def __pow__(self, other):
        other = self.convert_exponent(other)
        return self.Pow(self, other)

    def __rpow__(self, other):
        other = self.convert(other)
        return self.Pow(other,  self.convert_exponent(self))

    __truediv__ = __div__
    __rtruediv__ = __rdiv__

    def match(self, pattern, *wildcards):
        """
        Pattern matching.

        Return None when expression (self) does not match
        with pattern. Otherwise return a dictionary such that

          pattern.subs_dict(self.match(pattern, *wildcards)) == self

        Don't redefine this method, redefine matches(..) method instead.

        See:
          http://wiki.sympy.org/wiki/Generic_interface#Pattern_matching
        """
        pattern = self.convert(pattern)
        wild_expressions = []
        wild_predicates = []
        for w in wildcards:
            if type(w) in [list, tuple]:
                assert len(w)==2,`w`
                expr, func = w
            else:
                expr, func = w, True
            wild_expressions.append(self.convert(expr))
            wild_predicates.append(func)
        return pattern.matches(self, {}, wild_expressions, wild_predicates)

    def matches(pattern, expr, repl_dict={}, wild_expressions=[], wild_predicates=[]):
        # check if pattern has a match and return it provided that
        # the match matches with expr:
        v = repl_dict.get(pattern)
        if v is not None:
            if v==expr:
                return repl_dict
            return
        # check if pattern matches with expr:
        if pattern==expr:
            return repl_dict
        # check if pattern is a wild expression
        if pattern in wild_expressions:
            if expr in wild_expressions:
                # wilds do not match other wilds
                return
            # wild pattern matches with expr only if predicate(expr) returns True
            predicate = wild_predicates[wild_expressions.index(pattern)]
            if (isinstance(predicate, bool) and predicate) or predicate(expr):
                repl_dict = repl_dict.copy()
                repl_dict[pattern] = expr
                return repl_dict
        return

from .primitive import PrimitiveAlgebra, NUMBER

class StructureGenerator(BasicType):
    
    def __new__(cls, parameters, **kwargs):
        name = '%s(%s, %s)' % (cls.__name__, ', '.join(map(str, parameters)), kwargs)
        bases = (AlgebraicStructure,)
        attrdict = dict(parameters = parameters, **kwargs)
        cls = type.__new__(cls, name, bases, attrdict)
        return cls

class PolynomialGenerator(StructureGenerator):

    def __new__(cls, symbols, coeff_structure=None):
        if coeff_structure is None:
            coeff_structure = classes.IntegerRing
        return StructureGenerator.__new__(cls, symbols,
                                          coeff_structure=coeff_structure)

##############################################################
# These are ideas:

class CommutativeRing(AlgebraicStructure):
    """ Represents an element of a commutative ring and defines binary
    operations +, *, -.
    """

class CommutativeAlgebra(AlgebraicStructure):
    """ Represents an element of a commutative algebra and defines
    binary operations +, *, -, /, **.
    """

class PolynomialAlgebra(AlgebraicStructure):
    """ Represents a polynomial.
    """

class PolynomialAlgebra(AlgebraicStructure):
    """ Represents a polynomial function.
    """

    def __new__(cls, obj, symbols, coefficient_symbols=[]):
        o = object.__new__(cls)
        o.coefficient_symbols = coefficient_symbols
        if len(symbols)==1:
            o.data = (UnivariatePolynomialAlgebra(obj), symbols)
        else:
            o.data = (MultivariatePolynomialAlgebra(obj), symbols)
        return o

