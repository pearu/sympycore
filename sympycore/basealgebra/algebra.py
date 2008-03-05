""" Provides BasicAlgebra class.
"""

__docformat__ = "restructuredtext"
__all__ = ['Algebra']

from ..core import classes, Expr

class Algebra(Expr):
    """ Represents an element of an algebraic structure.

    This class collects implementation specific methods of algebra
    classes.
    
    For implemented algebras, see:

      Verbatim
      CommutativeRingWithPairs
    
    New algebras may need to redefine the following methods::
    
      __new__(cls, ...)
      convert(cls, obj, typeerror=True)
      convert_coefficient(cls, obj, typeerror=True)
      convert_exponent(cls, obj, typeerror=True)
      as_verbatim(self)
      as_algebra(self, cls)

    and the following properties::

      args(self)
      func(self)

    """
    #__slots__ = ['_str_value']

    _str_value = None

    coefftypes = (int, long)
    exptypes = (int, long)

    def __str__(self):
        s = self._str_value
        if s is None:
            s = self._str_value = str(self.as_verbatim())
        return s

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, str(self))

    def __eq__(self, other):
        if type(other) is type(self):
            return self.pair == other.pair
        return False

    def __nonzero__(self):
        return not not self.data

    def as_tree(self, tab='', level=0):
        return self.as_verbatim().as_tree(tab,level)

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
        if isinstance(obj, (str, unicode, Verbatim)):
            return Verbatim.convert(obj).as_algebra(cls)

        # check if obj belongs to coefficient algebra
        r = cls.convert_coefficient(obj, typeerror=False)
        if r is not NotImplemented:
            return cls.Number(r)

        # as a last resort, convert from another algebra:
        if isinstance(obj, Algebra):
            return obj.as_algebra(cls)

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
        if isinstance(obj, cls.exptypes) or isinstance(obj, cls):
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
        if isinstance(obj, cls.coefftypes):
            return obj
        if typeerror:
            raise TypeError('%s.convert_coefficient: failed to convert %s instance'\
                            ' to coefficient algebra, expected int|long object'\
                            % (cls.__name__, obj.__class__.__name__))
        else:
            return NotImplemented

    def as_verbatim(self):
        raise NotImplementedError('%s must define as_verbatim method' #pragma NO COVER
                                  % (self.__class__.__name__))         #pragma NO COVER

    def as_algebra(self, cls):
        """ Convert algebra to another algebra.

        This method uses default conversation via verbatim algebra that
        might not be the most efficient. For efficiency, algebras should
        redefine this method to implement direct conversation.
        """
        # todo: cache verbatim algebras
        if cls is classes.Verbatim:
            return self.as_verbatim()
        return self.as_verbatim().as_algebra(cls)

    @classmethod
    def get_predefined_symbols(cls, name):
        return

    @property
    def func(self):
        """ Returns a callable such that ``self.func(*self.args) == self``.
        """
        raise NotImplementedError('%s must define property func'      #pragma NO COVER
                                  % (cls.__name__))                   #pragma NO COVER

    @property
    def args(self):
        """ Returns a sequence such that ``self.func(*self.args) == self``.
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

    @property
    def symbols(self):
        """ Return a set of atomic subexpressions in a symbolic object.
        """
        symbols = self._symbols
        if symbols is None:
            args = self.args
            if args:
                symbols = set()
                for arg in args:
                    symbols |= arg.symbols
            else:
                symbols = set([self])
            self._symbols = symbols
        return symbols

    def has(self, obj):
        """ Return True if self contains atomic expression obj.
        """
        convert = self.convert
        return convert(obj) in self.symbols

    def match(self, pattern, *wildcards):
        """
        Pattern matching.

        Return None when expression (self) does not match with
        pattern. Otherwise return a dictionary such that

        ::

          pattern.subs_dict(self.match(pattern, *wildcards)) == self

        Don't redefine this method, redefine ``matches(..)`` method instead.

        :See:
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
            wild_expressions.append(s)
            wild_predicates.append(func)
        if wild_expressions:
            wild_info = (wild_expressions, wild_predicates)
        else:
            wild_info = None
        return pattern.matches(self, {}, wild_info)

    def matches(pattern, expr, repl_dict={}, wild_info=None):
        # check if pattern has a match and return it provided that
        # the match matches with expr:
        v = repl_dict.get(pattern)
        if v is not None:
            if v==expr:
                return repl_dict
            return
        # check if pattern matches with expr:
        if pattern==expr:
            if wild_info and expr in wild_info[0]:
                return
            return repl_dict
        if wild_info:
            wild_expressions, wild_predicates = wild_info
            # check if pattern is a wild expression
            if pattern in wild_expressions:
                if expr in wild_expressions:
                    # wilds do not match other wilds
                    return
                if expr.symbols.intersection(pattern.symbols):
                    # wild does not match expressions containing wild expressions
                    return
                # wild pattern matches with expr only if predicate(expr) returns True
                predicate = wild_predicates[wild_expressions.index(pattern)]
                if (isinstance(predicate, bool) and predicate) or predicate(expr):
                    repl_dict = repl_dict.copy()
                    repl_dict[pattern] = expr
                    return repl_dict
            pattern_symbols = pattern.symbols
            for w in wild_expressions:
                if w in pattern_symbols:
                    # _matches implements implementation specific matches,
                    # pattern should contain wild symbols, otherwise
                    # _matches would always return None
                    return pattern._matches(expr, repl_dict, wild_info)
        return

    @classmethod
    def _matches_seq(cls, pattern_seq, expr_seq, repl_dict, wild_info):
        n = len(pattern_seq)
        m = len(expr_seq)
        if n!=m:
            return
        elif n==0:
            return repl_dict
        elif n==1:
            p = pattern_seq[0]
            if isinstance(p, cls):
                return p.matches(expr_seq[0], repl_dict, wild_info)
            if p==expr_seq[0]:
                return repl_dict
            return
        def matches(pattern, expr):
            if isinstance(pattern, cls):
                return pattern.matches(expr, repl_dict, wild_info)
            if pattern==expr:
                return repl_dict
            return
        def subs(expr, l):
            if isinstance(expr, cls):
                return expr.subs(l)
            return expr
        for i in xrange(n):
            p = pattern_seq[i]
            e = expr_seq[i]
            r = matches(p, e)
            if r is not None:
                new_pattern_seq = [subs(pattern_seq[j],r.items()) for j in xrange(n) if j!=i]
                new_expr_seq = [expr_seq[j] for j in xrange(n) if j!=i]
                r1 = cls._matches_seq(new_pattern_seq, new_expr_seq, r, wild_info)
                if r1 is not None:
                    return r1
        return

    def _matches(pattern, expr, repl_dict, wild_info):
        if pattern.func == expr.func:
            return pattern._matches_seq(pattern.args, expr.args, repl_dict, wild_info)
        return

    def subs(self, subexpr, newexpr=None):
        """ Substitute a sub-expression with new expression.
        
        There are two usage forms::
        
          obj.subs(subexpr, newexpr)
          obj.subs([(subexpr1, newexpr1), (subexpr2, newexpr2), ..])
        
        """
        convert = self.convert
        if newexpr is None:
            r = self
            for s,n in subexpr:
                r = r._subs(convert(s), convert(n))
            return r
        return self._subs(convert(subexpr), convert(newexpr))

    def _subs(self, subexpr, newexpr):
        raise NotImplementedError('%s must define _subs method'     #pragma NO COVER
                                  % (self.__class__.__name__))      #pragma NO COVER


from .verbatim import Verbatim
