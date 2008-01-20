
from ..core import Basic

class BasicAlgebra(Basic):
    """ Represents an element of an algebraic structure.

    This class collects implementation specific methods of algebra classes.
    
    For implemented algebras, see:
      PrimitiveAlgebra
      CommutativeRingWithPairs
    
    New algebras may need to redefine the following methods:
      __new__(cls, ...)
      convert(cls, obj, typeerror=True)
      convert_coefficient(cls, obj, typeerror=True)
      convert_exponent(cls, obj, typeerror=True)
      as_primitive(self)
      as_algebra(self, cls)
      Symbol(cls, obj), Number(cls, obj), Add(cls, *seq), Mul(cls, *seq),
      Pow(cls, base, exponent), Terms(cls, *seq), Factors(cls, *seq)
      as_Add_args(self), as_Mul_args(self), as_Pow_args(self),
      as_Terms_args(self), as_Factors_args(self)
      properties: args(self). func(self)
    """

    @classmethod
    def redirect_operation(cls, *args, **kws):
        """ Default implementation of redirect_operation method
        used as a callback when RedirectOperation exception is raised.
        """
        callername = kws['redirect_operation']
        return getattr(cls, callername)(*args,
                                        **dict(redirect_operation='ignore_redirection'))

    def __str__(self):
        return str(self.as_primitive())

    def as_tree(self, tab=''):
        return self.as_primitive().as_tree(tab)

    @classmethod
    def convert(cls, obj, typeerror=True):
        """ Convert obj to algebra element.

        Set typeerror=False when calling from operation methods like __add__,
        __mul__, etc.
        """
        # check if obj is already algebra element:
        if isinstance(obj, cls):
            return obj

        # parse algebra expression from string:
        if isinstance(obj, (str, unicode)):
            obj = PrimitiveAlgebra(obj)

        # convert from another algebra:
        if isinstance(obj, BasicAlgebra):
            return obj.as_algebra(cls)

        # as a last resort, check if obj belongs to coefficient algebra
        r = cls.convert_coefficient(obj, typeerror=False)
        if r is not NotImplemented:
            return cls.Number(r)

        if typeerror:
            raise TypeError('%s.convert: failed to convert %s instance'\
                            ' to algebra'\
                            % (cls.__name__, obj.__class__.__name__))
        else:
            return NotImplemented

    @classmethod
    def convert_exponent(cls, obj, typeerror=True):
        """ Convert obj to exponent algebra.
        """
        if isinstance(obj, (int, long)):
            return obj
        if typeerror:
            raise TypeError('%s.convert_exponent: failed to convert %s instance'\
                            ' to exponent algebra, expected int|long object'\
                            % (cls.__name__, obj.__class__.__name__))
        else:
            return NotImplemented

    @classmethod
    def convert_coefficient(cls, obj, typeerror=True):
        """ Convert obj to coefficient algebra.
        """
        if isinstance(obj, (int, long)):
            return obj
        if typeerror:
            raise TypeError('%s.convert_coefficient: failed to convert %s instance'\
                            ' to coefficient algebra, expected int|long object'\
                            % (cls.__name__, obj.__class__.__name__))
        else:
            return NotImplemented

    def as_primitve(self):
        raise NotImplementedError('%s must define as_primitive method'\
                                  % (self.__class__.__name__))

    def as_algebra(self, cls):
        """ Convert algebra to another algebra.

        This method uses default conversation via primitive algebra that
        might not be the most efficient. For efficiency, algebras should
        redefine this method to implement direct conversation.
        """
        # todo: cache primitive algebras
        if cls is classes.PrimitiveAlgebra:
            return self.as_primitive()
        return self.as_primitive().as_algebra(cls)

    @property
    def func(self):
        """ Returns a callable such that self.func(*self.args) == self.
        """
        raise NotImplementedError('%s must define property func' % (cls.__name__))

    @property
    def args(self):
        """ Returns a sequence such that self.func(*self.args) == self.
        """
        raise NotImplementedError('%s must define property args' % (cls.__name__))

    @classmethod
    def Symbol(cls, obj):
        """ Construct algebra symbol directly from obj.
        """
        raise NotImplementedError('%s must define classmethod Symbol' % (cls.__name__))

    @classmethod
    def Number(cls, num, denom=None):
        """ Construct algebra number directly from obj.
        """
        raise NotImplementedError('%s must define classmethod Number' % (cls.__name__))

    @classmethod
    def Add(cls, *seq):
        """ Compute sum over seq containing algebra elements.
        """
        raise NotImplementedError('%s must define classmethod Add' % (cls.__name__))

    @classmethod
    def Mul(cls, *seq):
        """ Compute product over seq containing algebra elements.
        """
        raise NotImplementedError('%s must define classmethod Mul' % (cls.__name__))

    @classmethod
    def Pow(cls, base, exponent):
        """ Compute power from base and exponent.
        Argument base must be an algebra element and exponent must be
        an element of exponent algebra.
        """
        raise NotImplementedError('%s must define classmethod Pow' % (cls.__name__))

    @classmethod
    def Terms(cls, *seq):
        """ Compute sum over seq containing pairs (element, coefficient).
        elements must belong to algebra.
        coefficients must belong to the coefficient algebra.
        """
        raise NotImplementedError('%s must define classmethod Terms' % (cls.__name__))

    @classmethod
    def Factors(cls, *seq):
        """ Compute product over seq containing pairs (element, exponent).
        elements must belong to algebra.
        exponents must belong to the exponent algebra.
        """
        raise NotImplementedError('%s must define classmethod Factors'
                                  % (self.__class__.__name__))

    def as_Add_args(self):
        """ Return a sequence such that Add(*self.as_Add_args()) == self
        """
        raise NotImplementedError('%s must define method as_Add_args'
                                  % (self.__class__.__name__))
    
    def as_Mul_args(self):
        """ Return a sequence such that Mul(*self.as_Mul_args()) == self
        """
        raise NotImplementedError('%s must define method as_Mul_args'
                                  % (self.__class__.__name__))
    
    def as_Pow_args(self):
        """ Return a 2-tuple such that Pow(*self.as_Pow_args()) == self
        """
        raise NotImplementedError('%s must define method as_Pow_args' \
                                  % (self.__class__.__name__))

    def as_Terms_args(self):
        """ Return a sequence such that Terms(*self.as_Terms_args()) == self
        """
        raise NotImplementedError('%s must define method as_Terms_args' \
                                  % (self.__class__.__name__))

    def as_Factors_args(self):
        """ Return a sequence such that Factors(*self.as_Factors_args()) == self
        """
        raise NotImplementedError('%s must define method as_Factors_args' \
                                  % (self.__class__.__name__))

    def __pos__(self):
        return self

    def __neg__(self):
        return self.Mul(self, self.convert(-1))

    def __add__(self, other):
        other = self.convert(other, False)
        if other is NotImplemented:
            return NotImplemented
        return self.Add(self, other)

    def __radd__(self, other):
        other = self.convert(other, False)
        if other is NotImplemented:
            return NotImplemented
        return self.Add(other, self)

    def __sub__(self, other):
        other = self.convert(other, False)
        if other is NotImplemented:
            return NotImplemented
        return self + (-other)

    def __rsub__(self, other):
        other = self.convert(other, False)
        if other is NotImplemented:
            return NotImplemented
        return other + (-self)

    def __mul__(self, other):
        other = self.convert(other, False)
        if other is NotImplemented:
            return NotImplemented
        return self.Mul(self, other)

    def __rmul__(self, other):
        other = self.convert(other, False)
        if other is NotImplemented:
            return NotImplemented
        return self.Mul(other, self)

    def __div__(self, other):
        other = self.convert(other, False)
        if other is NotImplemented:
            return NotImplemented
        return self.Mul(self, other ** (-1))

    def __rdiv__(self, other):
        other = self.convert(other, False)
        if other is NotImplemented:
            return NotImplemented
        return self.Mul(other, self ** (-1))

    def __truediv__(self, other):
        other = self.convert(other, False)
        if other is NotImplemented:
            return NotImplemented
        return self.Mul(self, other ** (-1))

    def __rtruediv__(self, other):
        other = self.convert(other, False)
        if other is NotImplemented:
            return NotImplemented
        return self.Mul(other, self ** (-1))

    def __pow__(self, other):
        other = self.convert_exponent(other, False)
        if other is NotImplemented:
            return NotImplemented
        return self.Pow(self, other)

    def __rpow__(self, other):
        other = self.convert(other, False)
        if other is NotImplemented:
            return NotImplemented
        return self.Pow(other,  self.convert_exponent(self))

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
                s, func = w
            else:
                s, func = w, True
            s = self.convert(s)
            assert s.head==SYMBOL,`s`
            wild_expressions.append(s)
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

    def subs(self, pattern, expr=None, wildcards=[]):
        """ Substitute subexpressions matching pattern with expr.
        
        There are two usage forms:
          obj.subs(pattern, expr, wildcards=[..])
          obj.subs([(pattern1, expr1), (pattern2, expr2), ..], wildcards=[..])
        """
        if expr is None:
            r = self
            for item in pattern:
                r = r.subs(item[0], item[1], wildcards=wildcards)
            return r
        if self.match(pattern, *wildcards) is not None:
            return self.convert(expr)
        expr = self.convert(expr)
        args = [a.subs(pattern, expr, wildcards=wildcards) for a in self.args]
        return self.func(*args)

class CommutativeRing:

    pass

from .primitive import PrimitiveAlgebra, NUMBER, SYMBOL


## class StructureGenerator(BasicType):
    
##     def __new__(cls, parameters, **kwargs):
##         name = '%s(%s, %s)' % (cls.__name__, ', '.join(map(str, parameters)), kwargs)
##         bases = (AlgebraicStructure,)
##         attrdict = dict(parameters = parameters, **kwargs)
##         cls = type.__new__(cls, name, bases, attrdict)
##         return cls

## class PolynomialGenerator(StructureGenerator):

##     def __new__(cls, symbols, coeff_structure=None):
##         if coeff_structure is None:
##             coeff_structure = classes.IntegerRing
##         return StructureGenerator.__new__(cls, symbols,
##                                           coeff_structure=coeff_structure)

## ##############################################################
## # These are ideas:

## class CommutativeRing(AlgebraicStructure):
##     """ Represents an element of a commutative ring and defines binary
##     operations +, *, -.
##     """

## class CommutativeAlgebra(AlgebraicStructure):
##     """ Represents an element of a commutative algebra and defines
##     binary operations +, *, -, /, **.
##     """

## class PolynomialAlgebra(AlgebraicStructure):
##     """ Represents a polynomial.
##     """

## class PolynomialAlgebra(AlgebraicStructure):
##     """ Represents a polynomial function.
##     """

##     def __new__(cls, obj, symbols, coefficient_symbols=[]):
##         o = object.__new__(cls)
##         o.coefficient_symbols = coefficient_symbols
##         if len(symbols)==1:
##             o.data = (UnivariatePolynomialAlgebra(obj), symbols)
##         else:
##             o.data = (MultivariatePolynomialAlgebra(obj), symbols)
##         return o

