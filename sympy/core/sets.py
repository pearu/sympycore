
from utils import memoizer_immutable_args
from basic import Basic, Composite, sympify
from methods import ImmutableSetMeths
from symbol import BasicSymbol
from function import Function, FunctionSignature
from predicate import Element, Subset


class BasicSet(Basic):
    """ Defines generic methods for set classes.
    """
    @property
    def superset(self):
        """ Return container set.
        """
        raise NotImplementedError('%s.superset property' % (self.__class__.__name__))

    @property
    def domain(self):
        """ Return one of the predefined sets that includes self.
        """
        assert isinstance(self, SetSymbol),`self`
        return self

    def try_contains(self, other):
        """ Check if other is an element of self.
        If the result is undefined, return None.
        """
        return

    def try_includes(self, other):
        """ Check if other is a subset of self.
        If the result is undefined, return None.
        """
        return

    def contains(self, other):
        """ Convenience method to construct Element(other, self) instance.
        """
        return Element(sympify(other), self)

    def is_subset_of(self, other):
        """ Check if self is a subset of other.
        """
        return

    def try_complementary(self, superset):
        """ Return a complementary set of self in the container field
        (as returned by the superset property).
        """
        return
    def try_positive(self):
        return
    def try_negative(self):
        return
    def try_shifted(self, shift):
        return
    def try_divisible(self, divisor):
        return
    def try_minus(self, other):
        return
    def try_union(self, other):
        return
    def try_intersection(self, other):
        return

    def __invert__(self):
        """ Convinience method to construct a complementary set.
        """
        return Complementary(self, self.superset)
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

    def try_supremum(self):
        """ Return supremum of a set.
        """
        return
    def try_infimum(self):
        """ Return infimum of a set.
        """
        return
    @property
    def is_unbounded_left(self):
        m = Basic.Min(self)
        if m.is_Number: return False
        if m==-Basic.oo: return True
        return

    @property
    def is_unbounded_right(self):
        m = Basic.Max(self)
        if m.is_Number: return False
        if m==Basic.oo: return True
        return


class Set(ImmutableSetMeths, BasicSet, Composite, set):
    """ A set object with elements.
    """

    def __new__(cls, *args):
        if not args: return Empty
        obj = set.__new__(cls)
        args = map(sympify,args)
        set.update(obj, args)
        return obj

    def __init__(self, *args, **kws):
        # avoid calling default set.__init__.
        pass

    def try_contains(self, other):
        return set.__contains__(self, other)
    def try_supremum(self):
        return Basic.Max(*self)
    def try_infimum(self):
        return Basic.Min(*self)

    @property
    def domain(self):
        # XXX: need a way to deterimine the domain of a symbolic expression
        raise NotImplementedError('%s.domain property' % (self.__class__.__name__))

    @property
    def superset(self):
        return self


class SetSymbol(BasicSet, BasicSymbol):
    """ Set symbol.
    """


class SetFunction(BasicSet, Function):
    """ Base class for Set functions.
    """

    #__new__ = Function.__new__ # avoid caching until Set is truelly immutable

    @property
    def domain(self):
        return self[0].domain

    @property
    def superset(self):
        return self[0]


set_classes = (SetSymbol, SetFunction, Set)


class Complementary(SetFunction):
    """ Complementary set of a set S within F.

    x in Complementary(S, F) <=> x in F & x not in S
    x in F & x not in Complementary(S, F) <=> x in S
    """
    signature = FunctionSignature((set_classes,set_classes), set_classes)

    @property
    def domain(self):
        return self[1].domain

    @property
    def superset(self):
        return self[1]

    @property
    def set(self):
        return self[0]
    def __new__(cls, set, superset=None):
        if superset is None:
            superset = set.superset
        return Function.__new__(cls, set, superset)
    
    @classmethod
    def canonize(cls, (set, superset)):
        if set==superset:
            return Empty
        if superset.is_Field and set.superset!=superset:
            return Union(Complementary(set, set.superset), Complementary(set.superset, superset))
        return set.try_complementary(superset)
    def try_complementary(self, superset):
        if self.superset==superset:
            return self.set
        if superset.is_subset_of(self.superset) and self.set.is_subset_of(superset):
            return self.set
    def try_contains(self, other):
        set = self.args[0]
        field = self.superset
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
    def try_infimum(self):
        return Basic.Min(self.superset)
    def try_supremum(self):
        return Basic.Max(self.superset)    



class Positive(SetFunction):
    """ Set of positive values in a set S.

    x in Positive(S) <=> x>0 and x in S
    """

    @classmethod
    def canonize(cls, (set,)):
        return set.try_positive()
    def try_positive(self):
        return self
    def try_negative(self):
        return Empty
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
    def try_infimum(self):
        m = 0
        if self.domain==Integers:
            m = 1
        return Basic.Max(Basic.Min(self[0]), m)
    def try_supremum(self):
        m = 0
        if self.domain==Integers:
            m = 1
        return Basic.Max(Basic.Max(self[0]), m)


class Negative(SetFunction):
    """ Set of negative values in a set S.

    x in Negative(S) <=> x<0 and x in S
    """
    @classmethod
    def canonize(cls, (set,)):
        return set.try_negative()
    def try_negative(self):
        return self
    def try_positive(self):
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
    def try_infimum(self):
        m = 0
        if self.domain==Integers:
            m = -1
        return Basic.Min(Basic.Min(self[0]), m)
    def try_supremum(self):
        m = 0
        if self.domain==Integers:
            m = -1
        return Basic.Min(Basic.Max(self[0]), m)


class Shifted(SetFunction):
    """ Set of shifted values in S.

    x in Shifted(S, s) <=> x-s in S
    """
    signature = FunctionSignature((set_classes,Basic), set_classes)
    @property
    def shift(self):
        return self[1]

    @classmethod
    def canonize(cls, (set, shift)):
        if shift==0: return set
        if set.is_EmptySet: return set
        return set.try_shifted(shift)

    def try_shifted(self, shift):
        return Shifted(self[0], self.shift+shift)
    def try_contains(self, other):
        set, shift = self.args
        r = set.contains(other-shift)
        if isinstance(r, bool):
            return r
    def try_supremum(self):
        r = self[0].try_supremum()
        if r is not None:
            return r + self[1]
    def try_infimum(self):
        r = self[0].try_infimum()
        if r is not None:
            return r + self[1]


class Divisible(SetFunction):
    """ Set of values in S that divide by divisor.

    x in Divisible(S, d) <=> x in S & x/d in S
    """
    signature = FunctionSignature((set_classes,Basic), set_classes)

    @property
    def superset(self):
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
        if Complementary(self)==other:
            return False
    def try_infimum(self):
        set,divisor = self.args
        return Basic.Min(set) / divisor
    def try_supremum(self):
        set,divisor = self.args
        return Basic.Max(set) / divisor


class Union(SetFunction):
    """ Union of sets.
    """
    signature = FunctionSignature([set_classes], set_classes)

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
                f = s.superset
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
                if s.is_BasicRange:
                    s2 = s.try_union(s1)
                    if s2 is not None:
                        new_sets.remove(s)
                        new_sets.remove(s1)
                        new_sets.add(s2)
                        return cls(*new_sets)
        if flag:
            return cls(*new_sets)
        sets.sort(Basic.compare)
        return

    def try_contains(self, other):
        l = []
        for set in self.args:
            r = set.contains(other)
            if isinstance(r, bool):
                if r:
                    return True
            else:
                l.append(set)
        if not l:
            return False
        if len(l)<len(self.args):
            return Element(other, Union(*l))

    @property
    def superset(self):
        return self

    @property
    def domain(self):
        return Union(*[s.domain for s in self.args])


class Intersection(SetFunction):
    """ Intersection of sets.
    """
    signature = FunctionSignature([set_classes], set_classes)
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
                if s.is_BasicRange:
                    s2 = s.try_intersection(s1)
                    if s2 is not None:
                        new_sets.remove(s)
                        new_sets.remove(s1)
                        new_sets.add(s2)
                        return cls(*new_sets)
        if flag:
            return cls(*new_sets)
        sets.sort(Basic.compare)
        return      

    @property
    def superset(self):
        return self

    @property
    def domain(self):
        return Union(*[s.domain for s in self.args])


class Minus(SetFunction):
    """ Set minus.
    """
    signature = FunctionSignature((set_classes, set_classes), set_classes)
    @classmethod
    def canonize(cls, (lhs, rhs)):
        if rhs.is_subset_of(lhs) and rhs.superset==lhs:
            return Complementary(rhs, lhs)
        if rhs.is_subset_of(lhs) is False:
            return lhs
        return lhs.try_minus(rhs)

class UniversalSet(SetSymbol):
    """ A set of all sets.
    """
    is_empty = False
    @memoizer_immutable_args('UniversalSet.__new__')
    def __new__(cls):
        return str.__new__(cls, 'UNIVERSALSET')
    @property
    def superset(self):
        return self
    @property
    def domain(self):
        return self
    def is_subset_of(self, other):
        return self==other
    def try_contains(self, other):
        return True
    def try_complementary(self, superset):
        return Empty
    def try_shifted(self, shift):
        return self
    def try_positive(self):
        return Positive(Reals)
    def try_negative(self):
        return Negative(Reals)


class EmptySet(SetSymbol):
    is_empty = True
    @memoizer_immutable_args('EmptySet.__new__')
    def __new__(cls):
        return str.__new__(cls, 'EMPTYSET')
    def try_contains(self, other): return False
    def is_subset_of(self, other):
        return True
    @property
    def superset(self):
        return Universal
    @property
    def domain(self):
        return self
    def try_complementary(self, superset):
        return superset
    def try_shifted(self, shift):
        return self
    def try_positive(self):
        return self
    def try_negative(self):
        return self

Basic.is_empty = None


class Field(SetSymbol):
    """ Represents abstract field.
    """


class ComplexSet(Field):
    """ Represents a field of complex numbers.
    """

    @memoizer_immutable_args('ComplexSet.__new__')
    def __new__(cls):
        return str.__new__(cls, 'Complexes')
    def try_contains(self, other):
        if other.is_Number:
            return True
        if other.is_ImaginaryUnit:
            return True
    @property
    def superset(self): return Universal
    def try_positive(self):
        return Positive(Reals)
    def try_negative(self):
        return Negative(Reals)
    def try_includes(self, set):
        if isinstance(set.domain, (RealSet, RationalSet, IntegerSet, PrimeSet)):
            return True
        if isinstance(set, UniversalSet):
            return False

class RealSet(Field):
    """ Represents a field of real numbers.
    """

    @memoizer_immutable_args('RealSet.__new__')
    def __new__(cls):
        return str.__new__(cls, 'Reals')

    @property
    def superset(self):
        return Complexes 
    def try_contains(self, other):
        if other.is_Number:
            if other.is_Real:
                return True
            return False
    def try_supremum(self):
        return Basic.oo
    def try_infimum(self):
        return -Basic.oo
    def try_positive(self):
        return Basic.OORange(0, Basic.oo, self)
    def try_negative(self):
        return Basic.OORange(-Basic.oo, 0, self)
    def try_includes(self, set):
        if isinstance(set.domain, (RationalSet, IntegerSet, PrimeSet)):
            return True
        if isinstance(set, ComplexSet):
            return False


class RationalSet(Field):
    """ Field of rational numbers.
    """
    @memoizer_immutable_args('RationalSet.__new__')
    def __new__(cls):
        return str.__new__(cls, 'Rationals')
    @property
    def superset(self):
        return Reals
    def try_contains(self, other):
        if other.is_Number:
            if other.is_Rational:
                return True
            return False
    def try_supremum(self):
        return Basic.oo
    def try_infimum(self):
        return -Basic.oo
    def try_positive(self):
        return Basic.OORange(0, Basic.oo, self)
    def try_negative(self):
        return Basic.OORange(-Basic.oo, 0, self)
    def try_includes(self, set):
        if isinstance(set.domain, (IntegerSet, PrimeSet)):
            return True
        if isinstance(set, (ComplexSet, RealSet)):
            return False


class IntegerSet(SetSymbol):
    """ Field of integers.
    """
    @memoizer_immutable_args('IntegerSet.__new__')
    def __new__(cls):
        return str.__new__(cls, 'Integers')

    @property
    def superset(self):
        return Rationals
    @property
    def domain(self):
        return self
    def try_contains(self, other):
        if other.is_Number:
            if other.is_Integer:
                return True
            return False
    def try_supremum(self):
        return Basic.oo
    def try_infimum(self):
        return -Basic.oo
    def try_positive(self):
        return Basic.OORange(0, Basic.oo, self)
    def try_negative(self):
        return Basic.OORange(-Basic.oo, 0, self)
    def try_includes(self, set):
        if isinstance(set.domain, PrimeSet):
            return True
        if isinstance(set, (ComplexSet, RealSet, RationalSet)):
            return False


class PrimeSet(SetSymbol):
    """ Set of positive prime numbers.
    """
    @memoizer_immutable_args('PrimeSet.__new__')
    def __new__(cls):
        return str.__new__(cls, 'Primes')
    @property
    def superset(self):
        return self
    @property
    def domain(self):
        return Integers
    def try_contains(self, other):
        if other.is_Number:
            if other.is_Integer and other.is_positive:
                from ntheory.primetest import isprime
                return isprime(other)
            return False
    def try_supremum(self):
        return Basic.oo
    def try_infimum(self):
        return Basic.Number(2)
    def try_positive(self):
        return self
    def try_negative(self):
        return Empty


SetFunction.signature = FunctionSignature((set_classes,), set_classes)
Element.signature = FunctionSignature((Basic,set_classes), (bool,))
Subset.signature = FunctionSignature((set_classes,set_classes), (bool,))

Complexes = ComplexSet()
Reals = RealSet()
Rationals = RationalSet()
Integers = IntegerSet()
Primes = PrimeSet()
Evens = Divisible(Integers,2)
Evens.__doc__ = ' Set of even integers.'
Odds = Complementary(Evens, Integers)
Odds.__doc__ = ' Set of odd integers.'
Empty = EmptySet()
Universal = UniversalSet()
