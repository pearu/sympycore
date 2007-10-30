
from .parser import Expr
from .utils import memoizer_immutable_args, DualProperty

ordering_of_classes = [
    'int','long','str',
    'ImaginaryUnit','Infinity','ComplexInfinity','NaN','Exp1','Pi',
    'Integer','Fraction','Real','Float','Interval',
    'Symbol','Dummy','Wild','Boolean','DummyBoolean',
    'MutableMul', 'Mul', 'MutableAdd', 'Add',
    'FunctionClass',
    'Function',
    'Sin','Cos','Exp','Log','Tan','Cot',
    'Equality','Unequality','StrictInequality','Inequality',
    'Equal','Less',
    'Not','And','XOr','Or',
    'IsComplex','IsReal','IsImaginary','IsRational','IsIrrational',
    'IsInteger','IsFraction','IsPrime','IsComposite','IsEven','IsOdd',
    'IsZero','IsPositive','IsNonPositive',
    'Set',
    'Union','Complementary','Positive','Negative','Shifted','Divisible',
    'PrimeSet','IntegerSet','IntegerCSet','RationalSet','RationalCSet',
    'RealSet','RealCSet','ComplexSet',
    'RangeOO','RangeOC','RangeCO','RangeCC'
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

    def __cmp__(cls, other):
        if cls is other: return 0
        if not isinstance(other, type):
            if isinstance(other.__class__, Basic):
                return cmp(cls, other.__class__) or -1
            return -1
        n1 = cls.__name__
        n2 = other.__name__
        unknown = len(ordering_of_classes)+1
        try:
            i1 = ordering_of_classes.index(n1)
        except ValueError:
            if 1 or not issubclass(cls, Basic.BasicFunctionSymbol):
                print 'ordering_of_classes is missing',n1,cls
            i1 = unknown
        try:
            i2 = ordering_of_classes.index(n2)
        except ValueError:
            if 1 or not issubclass(cls, Basic.BasicFunctionSymbol):
                print 'ordering_of_classes is missing',n2,other
            i2 = unknown
        if i1 == unknown and i2 == unknown:
            return cmp(n1, n2)
        return cmp(i1,i2)


class Basic(object):

    __metaclass__ = BasicType

    Lambda_precedence = 1
    Add_precedence = 40
    Mul_precedence = 50
    Pow_precedence = 60
    Apply_precedence = 70
    Item_precedence = 75
    Atom_precedence = 1000

    @staticmethod
    def sympify(a, sympify_lists=False):
        """Converts an arbitrary expression to a type that can be used
           inside sympy. For example, it will convert python int's into
           instance of sympy.Integer, floats into intances of sympy.Float,
           etc. It is also able to coerce symbolic expressions which does
           inherit after Basic. This can be useful in cooperation with SAGE.

           It currently accepts as arguments:
               - any object defined in sympy (except maybe matrices [TODO])
               - standard numeric python types: int, long, float, Decimal
               - strings (like "0.09" or "2e-19")

           If sympify_lists is set to True then sympify will also accept
           lists, tuples and sets. It will return the same type but with
           all of the entries sympified.

           If the argument is already a type that sympy understands, it will do
           nothing but return that value. This can be used at the begining of a
           function to ensure you are working with the correct type.

           >>> from sympy import *

           >>> sympify(2).is_integer
           True
           >>> sympify(2).is_real
           True

           >>> sympify(2.0).is_real
           True
           >>> sympify("2.0").is_real
           True
           >>> sympify("2e-45").is_real
           True

        """

        if isinstance(a, Basic):
            return a
        if isinstance(a, bool):
            return a
        if isinstance(a, (int, long)):
            return Basic.Integer(a)
        if isinstance(a, float):
            return Basic.Float(a)
        if isinstance(a, complex):
            real, imag = map(Basic.sympify, (a.real, a.imag))
            ireal, iimag = int(real), int(imag)
            if ireal + iimag*1j == a:
                return ireal + iimag*Basic.I
            return real + Basic.I * imag
        if isinstance(a, (list, tuple)) and len(a) == 2:
            return Basic.Interval(*a)
        if isinstance(a, (list,tuple,set)) and sympify_lists:
            return type(a)([Basic.sympify(x, True) for x in a])
        if not isinstance(a, str):
            # At this point we were given an arbitrary expression
            # which does not inherit after Basic. This may be
            # SAGE's expression (or something alike) so take
            # its normal form via str() and try to parse it.
            a = str(a)
        try:
            return Expr(a).tosymbolic()
        except Exception, msg:
            raise ValueError("%s is NOT a valid SymPy expression: %s" % (`a`, msg))

    predefined_objects = {} # used by parser.

    repr_level = 1

    def __repr__(self):
        if Basic.repr_level == 0:
            return self.torepr()
        if Basic.repr_level == 1:
            return self.tostr()
        raise ValueError, "bad value for Basic.repr_level"

    def __str__(self):
        return self.tostr()

    def tostr(self, level=0):
        return self.torepr()

    def torepr(self):
        return '<%r instance %s>' % (self.__class__, id(self))

    def compare(self, other):
        """
        Return -1,0,1 if the object is smaller, equal, or greater than other
        (not always in mathematical sense).
        If the object is of different type from other then their classes
        are ordered according to sorted_classes list.
        """
        # all redefinitions of compare method should start with the
        # following three lines:
        if self is other: return 0
        c = cmp(self.__class__, other.__class__)
        if c: return c
        if isinstance(self, (str,int,long)):
            cls = self.__class__.__base__
            return cmp(cls(self), cls(other))
        st = self[:]
        ot = other[:]
        c = cmp(len(st), len(ot))
        if c: return c
        for l,r in zip(st,ot):
            if isinstance(l, Basic):
                c = l.compare(r)
            else:
                c = cmp(l, r)
            if c: return c
        return 0

    def __eq__(self, other):
        raise NotImplementedError('%s.__eq__(%s)' % (self.__class__.__name__, other.__class__.__name__))

    def __hash__(self):
        raise NotImplementedError('%s.__hash__()' % (self.__class__.__name__))

    def __nonzero__(self):
        # prevent using constructs like:
        #   a = Symbol('a')
        #   if a: ..
        raise AssertionError("only Relational and Number classes can define __nonzero__ method, %r" % (self.__class__))

    def replace(self, old, new):
        """ Replace subexpression old with expression new and return result.
        """
        if self==sympify(old):
            return sympify(new)
        return self

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
            for k,c in self.items():
                result = result.union(k.atoms(type=type))
                result = result.union(c.atoms(type=type))
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
            raise TypeError("has() requires at least 1 argument (got none)")
        p = Basic.sympify(patterns[0])
        if not p.is_Wild:
            return p in self.atoms(p.__class__)
        raise NotImplementedError('has: wild support')

    def clone(self):
        """ Return recreated composite object.
        """
        return self

    def expand(self, *args, **hints):
        """Expand an expression based on different hints. Currently
           supported hints are basic, power, complex, trig and func.
        """
        return self

    def split(self, op, *args, **kwargs):
        return [self]

    def refine(self, *assumptions):
        if assumptions:
            __assumptions__ = Basic.Assumptions(*assumptions)
        return self.clone()

    def replace_dict(self, old_new_dict):
        r = self
        for old,new in old_new_dict.items():
            r = r.replace(old,new)
            if not isinstance(r, Basic): break
        return r

    def replace_list(self, expressions, values):
        r = self
        for e,b in zip(expressions, values):
            r = r.replace(e,b)
            if not isinstance(r, Basic): break
        return r

# The following static methods should be used in places
# where assumptions may be required
    @staticmethod
    def is_less(lhs, rhs, assumptions=None):
        """ Return True or False if the relation 'lhs < rhs' is satisfied or not.
        For non-numeric operants assumptions model will be used.
        If the result is undefined, return None.
        """
        if lhs.is_Number and rhs.is_Number:
            return lhs < rhs
        d = rhs - lhs
        if d.is_Number:
            return d.is_positive
        if d.is_Infinity: return True
        if d==-Basic.oo: return False
        #print lhs, rhs
        #XXX: implement assumptions model
#
    @staticmethod
    def is_equal(lhs, rhs, assumptions=None):
        return lhs==rhs
    
    @staticmethod
    def is_less_equal(lhs, rhs, assumptions=None):
        if Basic.is_equal(lhs, rhs, assumptions): return True
        return Basic.is_less(lhs, rhs, assumptions)

    @staticmethod
    def is_greater(lhs, rhs, assumptions=None):
        return Basic.is_less(rhs, lhs, assumptions)

    @staticmethod
    def is_greater_equal(lhs, rhs, assumptions=None):
        return Basic.is_less_equal(rhs, lhs, assumptions)
    @staticmethod
    def is_element_of_set(lhs, rhs, assumptions=None):
        r = rhs.try_element(lhs)
        if isinstance(r, bool):
            return r
        #XXX: implement assumptions model
    @staticmethod
    def is_subset_of_set(lhs, rhs, assumptions=None):
        r = rhs.try_subset(lhs)
        if isinstance(r, bool):
            return r
        #XXX: implement assumptions model

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


sympify = Basic.sympify
Expr.register_handler(Basic)
