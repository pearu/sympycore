
from ..core import Basic, classes

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

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, str(self))

    def inspect(self):
        """ Show the internal tree structure of the object.
        """
        print self.as_tree()
        return

    def as_tree(self, tab='', level=0):
        return self.as_primitive().as_tree(tab,level)

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
            obj = classes.PrimitiveAlgebra(obj)

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
        if isinstance(obj, (int, long, cls)):
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
        raise NotImplementedError('%s must define as_primitive method' #pragma NO COVER
                                  % (self.__class__.__name__))         #pragma NO COVER

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

    @classmethod
    def get_predefined_symbols(cls, name):
        return

    @property
    def func(self):
        """ Returns a callable such that self.func(*self.args) == self.
        """
        raise NotImplementedError('%s must define property func'      #pragma NO COVER
                                  % (cls.__name__))                   #pragma NO COVER

    @property
    def args(self):
        """ Returns a sequence such that self.func(*self.args) == self.
        """
        raise NotImplementedError('%s must define property args'      #pragma NO COVER
                                  % (cls.__name__))                   #pragma NO COVER

    @classmethod
    def Symbol(cls, obj):
        """ Construct algebra symbol directly from obj.
        """
        raise NotImplementedError('%s must define classmethod Symbol' #pragma NO COVER
                                  % (cls.__name__))                   #pragma NO COVER

    @classmethod
    def Number(cls, num, denom=None):
        """ Construct algebra number directly from obj.
        """
        raise NotImplementedError('%s must define classmethod Number' #pragma NO COVER
                                  % (cls.__name__))                   #pragma NO COVER

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
        pattern = self.convert(pattern)
        expr = self.convert(expr)
        if self==pattern:
            return expr
        args = []
        cls = type(self)
        for a in self.args:
            if isinstance(a, cls):
                a = a.subs(pattern, expr, wildcards=wildcards)
            args.append(a)
        return self.func(*args)

from .primitive import SYMBOL
