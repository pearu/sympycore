
import types
import itertools

from .utils import memoizer_immutable_args, singleton
from .sexpr import SYMBOLIC, ARITHMETIC

__all__ = ['BasicType', 'Basic', 'Atom', 'Composite', 'BasicWild',
           'Tuple',
           'classes', 'objects', 'sort_sequence']

class Holder:
    """ Holds (name, value) pairs via Holder instance attributes.
    The set of pairs is extendable via setting
      <Holder instance>.<name> = <value>
    """
    def __init__(self, descr):
        self._descr = descr
        self._counter = 0
    def __str__(self):
        return self._descr % (self.__dict__)

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, str(self))
    
    def __setattr__(self, name, obj):
        if not self.__dict__.has_key(name) and self.__dict__.has_key('_counter'):
            self._counter += 1
        self.__dict__[name] = obj

    def iterNameValue(self):
        for k,v in self.__dict__.iteritems():
            if k.startswith('_'):
                continue
            yield k,v

classes = Holder('Sympy Basic subclass holder (%(_counter)s classes)')
objects = Holder('Sympy predefined objects holder (%(_counter)s objects)')

class BasicType(type):
    """ Metaclass for Basic classes.
    """
    def __new__(typ, name, bases, attrdict):
        # create Class:
        cls = type.__new__(typ, name, bases, attrdict)

        setattr(classes, cls.__name__, cls)

        # _dummy_class attribute is used by the BasicSymbol.as_dummy() method
        if bases[0].__name__=='BasicDummySymbol' or name=='BasicDummySymbol':
            cls.__bases__[-1]._dummy_class = cls 

        # _symbol_cls is needed in BasicLambda.__hash__ method
        if name=='BasicSymbol':
            Basic._symbol_cls = cls
        elif bases[-1].__name__=='BasicSymbol' and len(bases)>1:
            bases[0]._symbol_cls = cls

        return cls

class Basic(object):

    __metaclass__ = BasicType

    Lambda_precedence = 1
    Add_precedence = 40
    Mul_precedence = 50
    Pow_precedence = 60
    Apply_precedence = 70
    Item_precedence = 75
    Atom_precedence = 1000

    predefined_objects = {} # used by parser.

    repr_level = 1

    def __repr__(self):
        if Basic.repr_level == 0:
            return self.torepr()
        if Basic.repr_level == 1:
            return self.tostr()
        # XXX: Catch the invalid value of repr_level at the moment of setting it.
        raise ValueError, "bad value for Basic.repr_level" #pragma NO COVER

    def __str__(self):
        return self.tostr()

    def tostr(self, level=0):
        return self.torepr()

    def torepr(self):
        return '<%s instance at %s>' % (self.__class__.__name__, hex(id(self)))

    # This implementation of __eq__ method is suitable for singleton instances.
    # Derived classes should redefine this __eq__ method (and also __hash__ and
    # compare methods accordingly) when necessary.
    def __eq__(self, other):
        # redefinitions of __eq__ method should start with the following two lines:
        if isinstance(other, sympify_types1):
            other = sympify(other)
        #
        return self is other

    def __ne__(self, other):
        return not (self == other)

    # All Basic instances must be immutable.
    def __hash__(self):
        # This is generic __hash__ method. Only composite classes that
        # do not derive from builtin types should redefine the __hash__
        # method. Caching hash value is recommended.
        r = getattr(self, '_hashvalue', None)
        if r is None:
            hashfunc = self.__class__.__base__.__hash__
            if hashfunc==self.__class__.__hash__:
                hashfunc = object.__hash__
            self._hashvalue = r = hashfunc(self)
        return r

    # Comparison is only needed for a nice ordering of operants in the string
    # representation of commutative operations. The compare method below
    # is used by the sort_sequence function.
    # Only numeric classes such as Number and MathematicalSymbol may (should)
    # define __lt__ and __le__ methods.
    def compare(self, other):
        # the sort_sequence function should guarantee the success of
        # the following assert:
        assert other.__class__ is self.__class__,`self, other`
        return cmp(self, other)

    def __nonzero__(self):
        # don't redefine __nonzero__ except for numeric classes.
        return False

    def try_replace(self, old, new):
        return

    def replace(self, old, new):
        """ Replace subexpression old with expression new and return result.
        """
        if self==old:
            return new
        obj = self.try_replace(sympify(old), sympify(new))
        if obj is not None:
            return obj
        return self

    subs = replace

    def replace_dict(self, old_new_dict):
        r = self
        for old,new in old_new_dict.items():
            r = r.replace(old,new)
            if not isinstance(r, Basic): break
        return r

    def atoms(self, type=None):
        """Returns the atoms that form current object.

        Example:
        >>> from sympy import *
        >>> x = Symbol('x')
        >>> y = Symbol('y')
        >>> (x+y**2+ 2*x*y).atoms()
        set([2, x, y])

        You can also filter the results by a given type(s) of object
        >>> (x+y+2+y**2*sin(x)).atoms(type=Symbol)
        set([x, y])

        >>> (x+y+2+y**2*sin(x)).atoms(type=Number)
        set([2])

        >>> (x+y+2+y**2*sin(x)).atoms(type=(Symbol, Number))
        set([2, x, y])
        """
        result = set()
        if type is not None and not isinstance(type, (object.__class__, tuple)):
            type = sympify(type).__class__
        if isinstance(self, classes.Atom):
            if type is None or isinstance(self, type):
                result.add(self)
        else:
            for obj in self:
                result = result.union(obj.atoms(type=type))
        return result


    def has(self, *patterns):
        """ Return True if self has any of the patterns.
        """
        if len(patterns)>1:
            for p in patterns:
                if self.has(p):
                    return True
            return False
        elif not patterns:
            return True
        p = sympify(patterns[0])
        if isinstance(p,Basic) and isinstance(p, classes.Atom) and not isinstance(p, classes.BasicWild):
            return p in self.atoms(p.__class__)
        if self.match(p) is not None:
            return True
        return False

    def match(self, pattern):
        """
        Pattern matching.

        Wild symbols match all.

        Return None when expression (self) does not match
        with pattern. Otherwise return a dictionary such that

          pattern.subs_dict(self.match(pattern)) == self

        Don't redefine this method, redefine matches(..) method instead.
        """
        pattern = sympify(pattern)
        if isinstance(pattern, bool):
            return
        return pattern.matches(self, {})

    def matches(pattern, expr, repl_dict={}, evaluate=False):
        """
        Helper method for match().
        """
        # check if pattern has already a match:
        v = repl_dict.get(pattern, None)
        if v is not None:
            if v==expr:
                return repl_dict
            return
        # match exactly
        if pattern==expr:
            return repl_dict

    def clone(self):
        """ Return recreated composite object.
        """
        raise NotImplementedError('%s.clone() method' % (self.__class__.__name__)) #pragma NO COVER

    def count_ops(self, symbolic=True):
        """ Compute the number of operations in an expression.

        By default the result will be in a form of a sum of function
        instances. When symbolic is False then the number of
        operations is returned where
        - function call counts for 1 operation,
        - operations like Mul, Add count for n-1 operations where n is
          the number of operants,
        - the number of operations in function arguments and operation
          operants are recursively added to the count.
        """
        return 0

    # XXX: The following methods need a revision:
    def refine(self, *assumptions):
        if assumptions:
            __assumptions__ = Basic.Assumptions(*assumptions)
        return self.clone()

    def visit(self, func, parent=None): # workinprogress
        """ Visit expression tree.
        """
        if isinstance(self, classes.Composite):
            if isinstance(self, dict):
                for key, value in self.iteritems():
                    item = self.__class__((key, value))
                    for it in (key, value):
                        if isinstance(it, classes.Composite):
                            for r in it.visit(func, self):
                                yield func(it, r)
                        else:
                            yield func(item, it)
            else:
                for item in self:
                    if isinstance(item, classes.Composite):
                        for r in item.visit(func, self):
                            yield func(item, r)
                    else:
                        yield func(self, item)
        yield func(parent, self)

    def as_sexpr(self, context=ARITHMETIC):
        """ Return expression as a tuple representing S-expression
        for a given context:
          sexpr.ARITHMETIC, sexpr.LOGICAL_SYMBOLIC, sexpr.LOGICAL_SET
        """
        return (SYMBOLIC, self)


class Atom(Basic):

    def torepr(self):
        return '%s()' % (self.__class__.__name__)

    @property
    def precedence(self):
        return Basic.Atom_precedence

class Composite(Basic):

    def torepr(self):
        return '%s(%s)' % (self.__class__.__name__,', '.join(map(repr, self)))

    def __eq__(self, other):
        if self.__class__ != other.__class__:
            return False
        if len(self)!=len(other):
            return False
        for l, r in itertools.izip(self, other):
            if not (l==r):
                return False
        return True

    def compare(self, other):
        c = cmp(self.count_ops(symbolic=False), self.count_ops(symbolic=False))
        if c:
            return c
        c = cmp(len(self), len(other))
        if c:
            return c
        return cmp(self, other)

    _hashvalue = None

    def __hash__(self):
        # the self.__class__.__new__ method should set self._hashvalue = None
        if self._hashvalue is None:
            self._hashvalue = hash((self.__class__.__name__,)+tuple(self))
        return self._hashvalue

    def try_replace(self, old, new):
        """ Replace subexpression old with expression new and return result.
        """
        if self==old:
            return new
        flag = True
        l = []
        for item in self:
            new_item = item.replace(old, new)
            if flag and new_item == item:
                new_item = item
            else:
                flag = False
            l.append(new_item)
        if flag:
            return self
        return self.__class__(*l)

class Tuple(Composite, tuple):
    """ Holds a tuple of Basic objects.
    """
    def __new__(cls, *args):
        return tuple.__new__(cls, map(sympify, args))


class BasicWild(Basic):
    """ Base class for wild symbols and functions.
    
    """
    predicate = lambda self, expr: True

    def matches(pattern, expr, repl_dict={}, evaluate=False):
        if isinstance(expr, classes.BasicWild):
            # wilds do not match other wilds
            return
        if isinstance(pattern, type):
            if not isinstance(expr, type):
                # wild functions will not match non-functions
                return
        elif isinstance(expr, type):
            # wild symbols will not match functions
            return
        # check if pattern has already a match
        v = repl_dict.get(pattern, None)
        if v is not None:
            if v==expr: return repl_dict
            return

        # wild matches if pattern.predicate(expr) returns True
        if pattern.predicate(expr):
            repl_dict = repl_dict.copy()
            repl_dict[pattern] = expr
            return repl_dict


from .sympify import sympify, sympify_types
Basic.sympify = staticmethod(sympify)
sympify_types1 = sympify_types[1:]

from .sorting import sort_sequence
