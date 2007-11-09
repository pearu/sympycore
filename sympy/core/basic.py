
import types
from .utils import memoizer_immutable_args, DualProperty, singleton, DualMethod, UniversalMethod

__all__ = ['BasicType', 'Basic', 'Atom', 'Composite', 'BasicWild']

ordering_of_classes = [
    'Number','NumberSymbol','ImaginaryUnit','BasicSymbol','Atom',
    'BasicFunction','Callable',
    'Composite',
    'Basic',
    ]


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
            setattr(Basic, cls.__name__, cls)
            setattr(Basic, 'is_' + name,
                    DualProperty(is_cls, is_cls_type))
        return cls

@singleton
def _get_class_index(cls):
    clsbase = None
    clsindex = -len(ordering_of_classes)
    for i in range(len(ordering_of_classes)):
        basename = ordering_of_classes[i]
        base = getattr(Basic, basename, None)
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

    @staticmethod
    def static_compare(obj1, obj2):
        if isinstance(obj1, Basic):
            return obj1.compare(obj2)
        if isinstance(obj2, Basic):
            return -obj2.compare(obj1)
        return cmp(obj1, obj2)

    @UniversalMethod
    def compare(obj, other):
        """
        Return -1,0,1 if the object is smaller, equal, or greater than other
        in some sense (not in mathematical sense in most cases).
        If the object is of different type from other then their classes
        are ordered according to sorted_classes list.
        
        This method is needed only for sorting. We cannot use __cmp__
        because of the duality of Callable and __lt__ methods can
        be defined only for a subset of Basic objects.
        """
        if obj is other: return 0
        if isinstance(obj, type):
            # obj is BasicType instance
            if isinstance(other, type):
                if isinstance(other, BasicType):
                    c = cmp(_get_class_index(obj),_get_class_index(other))
                    if c: return c
                    # obj and other are subclasses of the same Basic class
                    # but not necessarily the same classes.
                    return cmp(obj.__name__, other.__name__)
                # use Python defined ordering for builtin types
                return cmp(obj, other)
            if isinstance(other, Basic):
                # instances are smaller than types
                return 1
            return cmp(obj, other)
        if isinstance(other, type):
            # instances are smaller than types
            return -1
        if not isinstance(other, Basic):
            return cmp(obj, other)
        c = obj.__class__.compare(other.__class__)
        if c: return c
        if isinstance(obj, sympify_types1):
            # convert Basic object to an instance of builtin type
            cls = obj.__class__.__base__
            return cmp(cls(obj), cls(other))
        if obj.is_Composite:
            # XXX: this will create lists which is a waste, use iterators instead
            st = obj[:]
            ot = other[:]
            c = cmp(len(st), len(ot))
            if c: return c
            for l,r in zip(st,ot):
                c = l.compare(r)
                if c: return c
            return 0
        return cmp(obj, other)

    def __eq__(self, other):
        # redefine __eq__ and __hash__ in parallel, also compare.
        return self is other

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        h = id(self)
        self.__hash__ = h.__hash__
        return h

    def __nonzero__(self):
        # don't redefine __nonzero__ except for Number types.
        return False

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
            type = Basic.sympify(type).__class__
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
        p = Basic.sympify(patterns[0])
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
        pattern = Basic.sympify(pattern)
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
