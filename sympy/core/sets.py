
from utils import memoizer_immutable_args
from basic import Basic, Composite, sympify
from symbol import BasicSymbol
from function import Function, FunctionSignature
from predicate import Predicate


class SetMethods:
    """ Defines generic methods for Set classes.
    """

    def try_contains(self, other):
        """ Check if other is an element of self.
        If the result is undefined, return None.
        """
        return

    def contains(self, other):
        """ Convenience method to construct Element(other, self) instance.
        """
        return Element(sympify(other), self)

    def is_subset_of(self, other):
        return

    def try_complementary(self):
        """ Return a complementary set of self in the container field
        (as returned by container_field method).
        """
        return

    def container_field(self):
        """ Return minimal field containing self.
        """
        raise NotImplementedError('%s.container_field() method' \
                                  % (self.__class__.__name__))

    def __invert__(self):
        """ Convinience method to construct a complementary set.
        """
        return Complementary(self)

    def __pos__(self):
        """ Convenience method to construct a subset of only positive quantities.
        """
        return Positive(self)

    def __neg__(self):
        """ Convenience method to construct a subset of only negative quantities.
        """
        return Negative(self)

    def __add__(self, other):
        """ Convinience method to construct a shifted set by other.
        """
        return Shifted(self, other)
    __radd__ = __add__
    def __sub__(self, other):
        return Shifted(self, -other)
    def __rsub__(self, other):
        return Shifted(-self, other)
    
    def __mul__(self, other):
        """ Convinience method to construct a set that elements divide by other.
        """
        return Divisible(self, other)
    __rmul__ = __mul__

    @property
    def target_set(self):
        return self

class Set(SetMethods, Composite, set):
    """ Set.
    """

    def __new__(cls, *args):
        if not args: return Empty
        obj = set.__new__(cls)
        obj.update(map(sympify,args))
        return obj

    def __init__(self, *args, **kws):
        # avoid calling default set.__init__.
        pass

    def try_contains(self, other):
        return set.__contains__(self, other)

class SetSymbol(SetMethods, BasicSymbol):
    """ Set symbol.
    """

class SetFunction(SetMethods, Function):
    """ Base class for Set functions.
    """
    
    def __new__(cls, *args):
        return Function.__new__(cls, *args)    

    @property
    def target_set(self):
        return self[0].target_set

set_values = (SetSymbol, SetFunction, Set)

SetFunction.signature = FunctionSignature((set_values,), set_values)

class Element(Predicate):
    """ Predicate 'is element of a set'.
    """
    signature = FunctionSignature((Basic,set_values), (bool,))

    def __new__(cls, *args):
        return Function.__new__(cls, *args)

    @classmethod
    def canonize(cls, (obj, setobj)):
        return setobj.try_contains(obj)

    def __nonzero__(self):
        return False


class Complementary(SetFunction):
    """ Complementary set of a set S within F.

    x in Complementary(S) <=> x in F & x not in S
    x in F & x not in Complementary(S) <=> x in S
    """
    
    @classmethod
    def canonize(cls, (set,)):
        if set.is_Complementary:
            return set[0]
        return set.try_complementary()

    def container_field(self):
        return self.args[0].container_field()

    def try_contains(self, other):
        set = self.args[0]
        field = self.container_field()
        r = field.contains(other)
        if isinstance(r, bool):
            if r:
                r = set.contains(other)
                if isinstance(r, bool):
                    r = not r
            if isinstance(r, bool):
                return r

    def is_subset_of(self, other):
        set = self.args[0]
        if set.is_subset_of(other):
            return True
        if set==other:
            return False

class Positive(SetFunction):
    """ Set of positive values in a set S.

    x in Positive(S) <=> x>0 and x in S
    """

    @classmethod
    def canonize(cls, (set,)):
        if set.is_Positive:
            return set[0]
        if set.is_Negative: return Empty

    def try_contains(self, other):
        set = self.args[0]
        r = set.contains(other)
        if isinstance(r, bool):
            if r:
                r = other.is_positive
            if isinstance(r, bool):
                return r

    def is_subset_of(self, other):
        set = self.args[0]
        if set==other:
            return True

class Negative(SetFunction):
    """ Set of negative values in a set S.

    x in Negative(S) <=> x<0 and x in S
    """
    @classmethod
    def canonize(cls, (set,)):
        if set.is_Negative:
            return set[0]
        if set.is_Positive:
            return Empty

    def try_contains(self, other):
        set = self.args[0]
        r = set.contains(other)
        if isinstance(r, bool):
            if r:
                r = other.is_negative
            if isinstance(r, bool):
                return r

    def is_subset_of(self, other):
        set = self.args[0]
        if set==other:
            return True

class Shifted(SetFunction):
    """ Set of shifted values in S.

    x in Shifted(S, s) <=> x-s in S
    """
    signature = FunctionSignature((set_values,Basic), set_values)

    @classmethod
    def canonize(cls, (set, shift)):
        if shift==0: return set
        if set.is_Field: return set
        return

    def try_contains(self, other):
        set, shift = self.args
        r = set.contains(other-shift)
        if isinstance(r, bool):
            return r

class Divisible(SetFunction):
    """ Set of values in S that divide by divisor.

    x in Divisible(S, d) <=> x in S & x/d in S
    """
    signature = FunctionSignature((set_values,Basic), set_values)
    def container_field(self):
        return self.args[0]

    @classmethod
    def canonize(cls, (set, divisor)):
        if divisor==1: return set
        if set.is_RealSet and divisor.is_Real:
            return set
        if set.is_RationalSet and divisor.is_Rational:
            return set
        return

    def try_contains(self, other):
        set, divisor = self.args
        r = set.contains(other)
        if isinstance(r, bool):
            if r:
                r = set.contains(other/divisor)
            if isinstance(r, bool):
                return r

    def is_subset_of(self, other):
        set = self.args[0]
        if set==other:
            return True
        if other.is_Complementary and other.args[0]==self:
            return False


class Union(SetFunction):
    signature = FunctionSignature([set_values], set_values)

    @classmethod
    def canonize(cls, sets):
        if len(sets)==0: return Empty
        if len(sets)==1: return sets[0]
        new_sets = set()
        flag = False
        for s in sets:
            if s.is_Union:
                new_sets = new_sets.union(s.args)
                flag = True
            elif s.is_empty:
                flag = True
            else:
                n = len(new_sets)
                new_sets.add(s)
                if n==len(new_sets):
                    flag = True
        for s in new_sets:
            c = Complementary(s)
            if c in new_sets:
                f = s.container_field()
                if f is not None:
                    new_sets.remove(s)
                    new_sets.remove(c)
                    new_sets.add(f)
                    return cls(*new_sets)
            for s1 in new_sets:
                if s is s1: continue
                if s.is_subset_of(s1):
                    new_sets.remove(s)
                    return cls(*new_sets)                    
        # check for complementary sets
        if flag:
            return cls(*new_sets)
        sets.sort(Basic.compare)
        return

class Intersection(SetFunction):
    signature = FunctionSignature([set_values], set_values)
    @classmethod
    def canonize(cls, sets):
        if len(sets)==0: return ~Empty
        if len(sets)==1: return sets[0]
        new_sets = set()
        flag = False
        for s in sets:
            if s.is_Intersection:
                new_sets = new_sets.union(s.args)
                flag = True
            elif s.is_empty:
                return s
            else:
                n = len(new_sets)
                new_sets.add(s)
                if n==len(new_sets):
                    flag = True
        for s in new_sets:
            c = Complementary(s)
            if c in new_sets:
                return Empty
            for s1 in new_sets:
                if s is s1: continue
                if s.is_subset_of(s1):
                    new_sets.remove(s1)
                    return cls(*new_sets)
                    
        if flag:
            return cls(*new_sets)
        sets.sort(Basic.compare)
        return      

class Minus(SetFunction):
    signature = FunctionSignature((set_values, set_values), set_values)
    @classmethod
    def canonize(cls, (lhs, rhs)):
        if lhs.is_Field:
            if rhs.is_subset_of(lhs) and rhs.container_field()==lhs:
                return Complementary(rhs)
        if rhs.is_subset_of(lhs) is False:
            return lhs

class EmptySet(SetSymbol):
    is_empty = True
    @memoizer_immutable_args('EmptySet.__new__')
    def __new__(cls): return str.__new__(cls, 'EMPTY')
    def try_contains(self, other): return False

Basic.is_empty = None

class Field(SetSymbol):
    """ Represents abstract field.
    """

    @memoizer_immutable_args('Field.__new__')
    def __new__(cls): return str.__new__(cls, 'F')


class ComplexSet(Field):
    """ Represents a field of complex numbers.
    """

    @memoizer_immutable_args('ComplexSet.__new__')
    def __new__(cls): return str.__new__(cls, 'C')

    def try_contains(self, other):
        if other.is_Number:
            return True
        if other.is_ImaginaryUnit:
            return True

class RealSet(Field):
    """ Represents a field of real numbers.
    """

    @memoizer_immutable_args('RealSet.__new__')
    def __new__(cls): return str.__new__(cls, 'R')

    def container_field(self): return Complexes 

    def try_contains(self, other):
        if other.is_Number:
            if other.is_Real:
                return True
            return False
    def try_complementary(self): return RealCSet()

class RealCSet(SetSymbol):
    """ Set of complex numbers with nonzero real part.
    """
    @memoizer_immutable_args('RealCSet.__new__')
    def __new__(cls): return str.__new__(cls, 'R^C')
    def container_field(self): return Complexes
    def try_contains(self, other):
        if other.is_Number:
            return False
    def try_complementary(self): return Reals

class RationalSet(Field):
    """ Field of rational numbers.
    """
    @memoizer_immutable_args('RationalSet.__new__')
    def __new__(cls): return str.__new__(cls, 'Q')
    def container_field(self): return Reals

    def try_contains(self, other):
        if other.is_Number:
            if other.is_Rational:
                return True
            return False
    def try_complementary(self): return Irrationals

class RationalCSet(SetSymbol):
    """ Set of irrational numbers.
    """
    @memoizer_immutable_args('RationalCSet.__new__')
    def __new__(cls): return str.__new__(cls, 'Q^C')
    def container_field(self): return Reals

    def try_contains(self, other):
        if other.is_Number:
            if other.is_Rational:
                return False
    def try_complementary(self): return Rationals

IrrationalSet = RationalCSet

class IntegerSet(Field):
    """ Field of integers.
    """
    @memoizer_immutable_args('IntegerSet.__new__')
    def __new__(cls): return str.__new__(cls, 'Z')

    @property
    def container_field(self): return Rationals
    def try_contains(self, other):
        if other.is_Number:
            if other.is_Integer:
                return True
            return False
    def try_complementary(self): return Fractions

class IntegerCSet(SetSymbol):
    """ Set of nontrivial fractions.
    """
    @memoizer_immutable_args('IntegerCSet.__new__')
    def __new__(cls): return str.__new__(cls, 'Z^C')

    @property
    def container_field(self): return Rationals
    def try_contains(self, other):
        if other.is_Number:
            if other.is_Fraction:
                return True
            return False
    def try_complementary(self): return Integers

FractionSet = IntegerCSet

class PrimeSet(SetSymbol):
    """ Represents a set of positive prime numbers.
    """
    @memoizer_immutable_args('PrimeSet.__new__')
    def __new__(cls): return str.__new__(cls, 'P')
    def container_field(self): return Integers
    def try_contains(self, other):
        if other.is_Number:
            if other.is_Integer and other.is_positive:
                raise NotImplementedError('need prime test')
            return False

Complexes = ComplexSet()
Reals = RealSet()
Rationals = RationalSet()
Irrationals = IrrationalSet()
Integers = IntegerSet()
Fractions = FractionSet()
Primes = PrimeSet()
Evens = Divisible(Integers,2)
Odds = Complementary(Evens)
Empty = EmptySet()
