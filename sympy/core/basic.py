
import types
import itertools

from .utils import memoizer_immutable_args, DualProperty, singleton, DualMethod, UniversalMethod

__all__ = ['BasicType', 'Basic', 'Atom', 'Composite', 'BasicWild',
           'classes', 'objects']

ordering_of_classes = [
    'Number','MathematicalSymbol','BasicSymbol','Atom',
    'BasicFunction','Callable',
    'Composite',
    'Basic',
    ]

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
        # set obj.is_Class attributes such that
        #   isinstance(obj, Class)==obj.is_Class
        # holds:
        attrdict['is_'+name] = True

        # create Class:
        cls = type.__new__(typ, name, bases, attrdict)

        # set Basic.Class attributes:
        if name!='Basic':
            def is_cls(self):
                # Uncommenting the following statement makes <expr>.is_<Class>
                # to be 3x faster. However, there is almost no change in the
                # timing of unittests. So, we don't use it as it just increases
                # memory consumption.
                #setattr(self, 'is_'+name, False)
                return False
            def is_cls_type(cl):
                return isinstance(cl, cls)
            #setattr(Basic, cls.__name__, cls)
            setattr(classes, cls.__name__, cls)
            setattr(Basic, 'is_' + name,
                    DualProperty(is_cls, is_cls_type))

        if getattr(cls, 'is_BasicDummySymbol', None):
            # _dummy_class attribute is used by the BasicSymbol.as_dummy() method
            if bases[0].__name__=='BasicDummySymbol' or name=='BasicDummySymbol':
                cls.__bases__[-1]._dummy_class = cls 

        return cls


@singleton
def _get_class_index(cls):
    clsbase = None
    clsindex = -len(ordering_of_classes)
    for i in range(len(ordering_of_classes)):
        basename = ordering_of_classes[i]
        base = getattr(classes, basename, None)
        if base is None:
            base = getattr(types, basename, object)
        if issubclass(cls, base):
            if clsbase is None:
                clsbase, clsindex = base, i
            else:
                if issubclass(base, clsbase):
                    clsbase,clsindex = base, i #pragma NO COVER
    return clsindex


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
    # Derived classes should redefine this __eq__ method.
    def __eq__(self, other):
        # redefinitions of __eq__ method should start with the following two lines:
        if isinstance(other, sympify_types1):
            other = sympify(other)
        #
        return self is other

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

    # Comparison is only needed for nicer ordering of operants in the string
    # representation of commutative operations.
    # Only numeric classes such as Number and MathematicalSymbol may (should)
    # redefine __lt__ and __le__ methods.
    def __lt__(self, other):
        # redefinitions of __lt__ method should start with the following two
        # lines:
        if isinstance(other, sympify_types1):
            other = sympify(other)
        #
        if isinstance(other, Basic):
            # Assuming that self or other is not a numeric class.
            # If they are numeric classes then compare only their values
            # (even when they are different types) and skip the following three lines.
            i1,i2 = _get_class_index(self.__class__), _get_class_index(other.__class__)
            if i1 != i2:
                return i1 < i2
        if self==other:
            return False
        return id(self) < id(other)

    def __le__(self, other):
        # Before redefining __le__ method, read the comments in __lt__ method. 
        if isinstance(other, sympify_types1):
            other = sympify(other)
        #
        if isinstance(other, Basic):
            i1,i2 = _get_class_index(self.__class__), _get_class_index(other.__class__)
            if i1 != i2:
                return i1 < i2
        #
        return id(self) <= id(other)

    def __ne__(self, other):
        return not self == other

    def __ge__(self, other):
        return not self < other

    def __gt__(self, other):
        return not self <= other

    def __nonzero__(self):
        # don't redefine __nonzero__ except for numeric classes.
        return False

    def __cmp__(self, other):
        if self==other: return 0
        if self < other: return -1
        return 1

    def replace(self, old, new):
        """ Replace subexpression old with expression new and return result.
        """
        if self==sympify(old):
            return sympify(new)
        return self

    def replace_dict(self, old_new_dict):
        r = self
        for old,new in old_new_dict.items():
            r = r.replace(old,new)
            if not isinstance(r, Basic): break
        return r

    # Do we need replace_list??
    #def replace_list(self, expressions, values):
    #    r = self
    #    for e,b in zip(expressions, values):
    #        r = r.replace(e,b)
    #        if not isinstance(r, Basic): break
    #    return r

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
        if self.is_Atom:
            if type is None or isinstance(self, type):
                result.add(self)
        elif isinstance(self, dict):
            for k,v in self.iteritems():
                result = result.union(k.atoms(type=type))
                result = result.union(v.atoms(type=type))
        else:
            for obj in self:
                result = result.union(obj.atoms(type=type))
        return result

    def visit(self, func, parent=None): # workinprogress
        """ Visit expression tree.
        """
        if self.is_Composite:
            if isinstance(self, dict):
                for key, value in self.iteritems():
                    item = self.__class__((key, value))
                    for it in (key, value):
                        if it.is_Composite:
                            for r in it.visit(func, self):
                                yield func(it, r)
                        else:
                            yield func(item, it)
            else:
                for item in self:
                    if item.is_Composite:
                        for r in item.visit(func, self):
                            yield func(item, r)
                    else:
                        yield func(self, item)
        yield func(parent, self)

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
        if isinstance(p,Basic) and p.is_Atom and not p.is_BasicWild:
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

    def expand(self, *args, **hints):
        """Expand an expression based on different hints. Currently
           supported hints are basic, power, complex, trig and func.
        """
        return self

    # XXX: The following methods need a revision:
    def split(self, op, *args, **kwargs):
        return [self]

    def refine(self, *assumptions):
        if assumptions:
            __assumptions__ = Basic.Assumptions(*assumptions)
        return self.clone()


class Atom(Basic):

    canonical = evalf = lambda self: self

    def torepr(self):
        return '%s()' % (self.__class__.__name__)

    @property
    def precedence(self):
        return Basic.Atom_precedence

class Composite(Basic):

    def torepr(self):
        return '%s(%s)' % (self.__class__.__name__,', '.join(map(repr, self)))

    def instance_compare(self, other):
        c = cmp(len(self), len(other))
        if c: return c
        for l, r in itertools.izip(self, other):
            c = l.compare(r)
            if c: return c
        return 0

class BasicWild(Basic):
    """ Base class for wild symbols and functions.
    
    """
    predicate = lambda self, expr: True

    def matches(pattern, expr, repl_dict={}, evaluate=False):
        if expr.is_BasicWild:
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
