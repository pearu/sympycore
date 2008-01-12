
import types

from ..core import classes
from .algebraic_structures import BasicAlgebra
from .primitive import PrimitiveAlgebra, ADD, MUL, SYMBOL, NUMBER

iterator_types = (type(iter([])), type(iter(())), type(iter(frozenset())),
                  type(dict().iteritems()), types.GeneratorType)

class PairsCommutativeRing(BasicAlgebra):
    """ Contains generic methods to algebra classes that
    use Pairs.
    """
    one_c = 1   # one element of coefficient algebra
    one_e = 1   # one element of exponent algebra
    zero_c = 0  # zero element of coefficient algebra
    zero_e = 0  # zero element of exponent algebra

    def __new__(cls, obj, head=None):
        if head is None:
            return cls.convert(obj)
        return cls.element_classes[head](obj)

    @classmethod
    def Add(cls, seq):
        terms = cls.element_classes[ADD]({})
        one = cls.one
        zero_c = cls.zero_c
        one_c = cls.one_c
        a_cls = cls.convert
        for t in seq:
            t = a_cls(t)
            head = t.head
            if head is SYMBOL:
                terms._add_value(t, one_c, zero_c)
            elif head is NUMBER:
                terms._add_value(one, t.value, zero_c)
            elif head is ADD:
                terms._add_values(t, one_c, zero_c)
            elif head is MUL:
                terms._add_value(t, one_c, zero_c)
            else:
                raise TypeError(`t, head`)
        return terms.canonize()

    @classmethod
    def Mul(cls, seq):
        result = cls.element_classes[MUL]({})
        one = cls.one
        zero_e = cls.zero_e
        one_e = cls.one_e
        one_c = cls.one_c
        zero_c = cls.zero_c
        a_cls = cls.convert
        number = one_c
        for t in seq:
            t = a_cls(t)
            head = t.head
            if head is SYMBOL:
                result._add_value(t, one_e, zero_e)
            elif head is NUMBER:
                number = number * t.value
            elif head is ADD:
                result._add_value(t, one_e, zero_e)
            elif head is MUL:
                result._add_values(t, one_e, zero_e)
            else:
                raise TypeError(`t, head`)
        result = result.canonize()
        if number==one_c:
            return result
        if result==one:
            return cls.element_classes[NUMBER](number)
        head = result.head
        if head is NUMBER:
            return cls.element_classes[NUMBER](result * number)
        if head is ADD:
            r = result.copy()
            r._multiply_values(number, one_c, zero_c)
            return r.canonize()
        return cls.element_classes[ADD]({result: number})

    def __pos__(self):
        return self

    def __radd__(self, other):
        other = self.convert(other, False)
        if isinstance(other, self.algebra_class):
            return other + self
        return NotImplemented

    def __rmul__(self, other):
        other = self.convert(other, False)
        if isinstance(other, self.algebra_class):
            return other * self
        return NotImplemented

class Pairs(object):
    """ Base class for holding pairs (by default non-commutative).
    """
    def __new__(cls, pairs):
        if isinstance(pairs, cls):
            return pairs
        o = object.__new__(cls)
        o._pairs = pairs
        o._hash = None
        return o

    @property
    def pairs(self):
        """ Return pairs as a tuple.
        """
        pairs = self._pairs
        if not isinstance(pairs, tuple):
            self._pairs = pairs = tuple(pairs)
        return pairs

    def __iter__(self):
        pairs = self._pairs
        if isinstance(pairs, iterator_types):
            self._pairs = pairs = tuple(pairs)
            return pairs
        return iter(pairs)

    def length(self):
        """ Return the number of pairs.
        """
        pairs = self._pairs
        if isinstance(pairs, iterator_types):
            self._pairs = pairs = tuple(pairs)
            return len(pairs)
        return len(pairs)

    def __eq__(self, other):
        if self is other:
            return True
        if type(self) is type(other):
            return self.pairs == other.pairs
        return False

    #XXX: impl modification methods


class CommutativePairs(Pairs):
    """ Represents operands of an commutative operation.

      CommutativePairs(<pairs>)

    where <pairs> is a sequence or an iterator of pairs:

      (<expression>, <repetition>)

    Here <expression> must be hashable as internally the pairs are
    saved in Python dictionary for update efficiency.

    CommutativePairs instance is mutable until the moment its hash
    value is computed.

    The following methods are defined to modify the CommutativePairs
    instance:
      _add_value(rhs, one, zero)
        rhs must be usable as key

      _add_values(rhs, one, zero)
        rhs must be an iterable returning pairs

      _multiply_values(rhs, one, zero)
        rhs must be support multiplication with values

      _expand_multiply_values(rhs, one, zero)
        rhs must be an iterable returning pairs
        
      _add_keys(rhs, one, zero)
        rhs must support addition with keys
    """
    
    @property
    def pairs(self):
        """ Return pairs as mutable dictionary.
        """
        pairs = self._pairs
        if not isinstance(pairs, dict):
            self._pairs = pairs = dict(pairs)
        return pairs

    def copy(self):
        return type(self)(self.pairs.copy())

    def __iter__(self):
        """ Return iterator of pairs.
        """
        pairs = self._pairs
        if isinstance(pairs, iterator_types):
            self._pairs = pairs = dict(pairs)
            return pairs.iteritems()
        elif isinstance(pairs, dict):
            return pairs.iteritems()
        elif isinstance(pairs, Pairs):
            raise
            return pairs.pairs
        return iter(pairs)

    def length(self):
        """ Return the number of pairs.
        """
        pairs = self._pairs
        if isinstance(pairs, iterator_types):
            self._pairs = pairs = dict(pairs)
            return len(pairs)
        return len(pairs)

    def __hash__(self):
        h = self._hash
        if h is None:
            # Using frozenset hash algorithm to avoid creating
            # frozenset instance. It should be safe to have the
            # same hash value with the frozenset as dictionary
            # keys of self should never contain a frozenset.
            h = 1927868237
            h *= self.length()+1
            for t in self:
                h1 = hash(t)
                h ^= (h1 ^ (h1 << 16) ^ 89869747)  * 3644798167
            h = h * 69069 + 907133923
            self._hash = h
        return h

    def __eq__(self, other):
        if self is other:
            return True
        other = self.convert(other, False)
        if isinstance(other, type(self)):
            return self.pairs==other.pairs
        return False

    def __str__(self):
        return '%s([%s])' % (self.__class__.__name__,
                             ', '.join(['(%s, %s)' % tc for tc in self.pairs.iteritems()]))

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self._pairs)

    def _add_value(self, rhs, one, zero):
        if self._hash is not None:
            raise TypeError('cannot add value to immutable pairs inplace'\
                            ' (hash has been computed)')
        pairs = self.pairs
        b = pairs.get(rhs)
        if b is None:
            pairs[rhs] = one
        else:
            c = b + one
            if zero==c:
                del pairs[rhs]
            else:
                pairs[rhs] = c

    def _add_values(self, rhs, one, zero):
        if self._hash is not None:
            raise TypeError('cannot add values to immutable pairs inplace'\
                            ' (hash has been computed)')
        pairs = self.pairs
        for t,c in rhs:
            b = pairs.get(t)
            if b is None:
                pairs[t] = c
            else:
                c = b + c
                if zero==c:
                    del pairs[t]
                else:
                    pairs[t] = c

    def _add_values_mul_coeff(self, rhs, coeff, zero):
        if self._hash is not None:
            raise TypeError('cannot add values to immutable pairs inplace'\
                            ' (hash has been computed)')
        pairs = self.pairs
        for t,c in rhs:
            b = pairs.get(t)
            if b is None:
                pairs[t] = c * coeff
            else:
                c = b + c * coeff
                if zero==c:
                    del pairs[t]
                else:
                    pairs[t] = c

    def _multiply_values(self, rhs, one, zero):
        if self._hash is not None:
            raise TypeError('cannot multiply values to immutable pairs inplace'\
                            ' (hash has been computed)')
        d = {}
        for t,c in self.pairs.iteritems():
            d[t] = c * rhs
        self._pairs = d

    def _expand_multiply_values(self, rhs, one, zero):
        if self._hash is not None:
            raise TypeError('cannot expand multiply values to immutable pairs inplace'\
                            ' (hash has been computed)')
        pairs = self.pairs
        self._pairs = d = {}
        if isinstance(rhs, iterator_types):
            seq1 = rhs
            seq2 = pairs.items()
        elif len(rhs) > len(pairs):
            seq1 = pairs.iteritems()
            seq2 = rhs
        else:
            seq1 = rhs
            seq2 = pairs.items()
        for t1, c1 in seq1:
            for t2, c2 in seq2:
                t = t1 * t2
                c = c1 * c2
                #XXX: make sure that t is not a number, it can be one though
                b = d.get(t)
                if b is None:
                    d[t] = c
                else:
                    c = b + c
                    if zero==c:
                        del d[t]
                    else:
                        d[t] = c

    def _add_keys(self, rhs, one, zero):
        if self._hash is not None:
            raise TypeError('cannot add keys to immutable pairs inplace'\
                            ' (hash has been computed)')
        pairs = self.pairs        
        self._pairs = d = {}
        for t,c in pairs.items():
            d[t + rhs] = c
        self._pairs = d


class CommutativeTerms(CommutativePairs):

    head = ADD

    def canonize(self):
        pairs = self.pairs
        if not pairs:
            return self.zero
        if len(pairs)==1:
            t, c = pairs.items()[0]
            if c==1:
                return t
            if self.one==t:
                return self.convert(c)
        return self

    def as_primitive(self):
        l = []
        one_c = self.one_c
        one = self.one
        for t,c in self:
            if one_c==c:
                l.append(PrimitiveAlgebra(t))
            elif one==t:
                l.append(PrimitiveAlgebra(c))
            else:
                if c==-one_c:
                    l.append(-PrimitiveAlgebra(t))
                else:
                    l.append(PrimitiveAlgebra(c) * t)
        if len(l)==1:
            return l[0]
        r = PrimitiveAlgebra((ADD,tuple(l)))
        r.commutative_add = True
        return r

    def __add__(self, other):
        other = self.convert(other, False)
        if isinstance(other, self.algebra_class):
            head = other.head
            if head is NUMBER:
                value = other.value
                if value==0:
                    return self
                result = self.copy()
                result._add_value(self.one, value, 0)
                return result.canonize()
            if head is SYMBOL:
                result = self.copy()
                result._add_value(other, 1, 0)
                return result.canonize()
            if head is ADD:
                if self.length() < other.length():
                    result = other.copy()
                    result._add_values(self, 1, 0)
                else:
                    result = self.copy()
                    result._add_values(other, 1, 0)
                return result.canonize()
            if head is MUL:
                result = self.copy()
                result._add_value(other, 1, 0)
                return result.canonize()
            return self.Add([self, other])
        return NotImplemented

    def __mul__(self, other):
        other = self.convert(other, False)
        if isinstance(other, self.algebra_class):
            head = other.head
            if head is NUMBER:
                value = other.value
                if value==1:
                    return self
                if value==0:
                    return other
                result = self.copy()
                result._multiply_values(value, 1, 0)
                return result
            elcls = self.element_classes
            if head is SYMBOL:
                if self.length()>1:
                    return elcls[MUL]({self:1, other: 1})
                pairs = self.pairs
                t, c = pairs.items()[0]
                if t==other:
                    return elcls[ADD]({elcls[MUL]({t: 2}): c})
                return elcls[ADD]({elcls[MUL]({t: 1, other:1}): c})
            if head is ADD:
                if self.pairs==other.pairs:
                    return elcls[MUL]({self: 2})
                return elcls[MUL]({self: 1, other: 1})
            if head is MUL:
                result = other.copy()
                result._add_value(self, 1, 0)
                return result.canonize()
            return self.Mul([self, other])
        return NotImplemented

    def expand(self):
        elcls = self.element_classes
        result = elcls[ADD]({})
        one = self.one
        for t, c in self.pairs.iteritems():
            t = t.expand()
            head = t.head
            if head is NUMBER:
                result._add_value(one, t.value * c, 0)
            elif head is SYMBOL:
                result._add_value(t, c, 0)
            elif head is MUL:
                result._add_value(t, c, 0)
            elif head is ADD:
                result._add_values_mul_coeff(t.pairs.iteritems(), c, 0)
            else:
                raise TypeError(`t, head`)            
        return result.canonize()

class CommutativeFactors(CommutativePairs):

    head = MUL

    def canonize(self):
        pairs = self.pairs
        if not pairs:
            return self.one
        if len(pairs)==1:
            t, c = pairs.items()[0]
            if c==1:
                return t
            if self.one==t:
                return t
        return self

    def as_primitive(self):
        l = []
        one_c = self.one_c
        for t,c in self:
            t = PrimitiveAlgebra(t)
            if one_c==c:
                l.append(t)
            else:
                l.append(t ** c)
        if len(l)==1:
            return l[0]
        r = PrimitiveAlgebra((MUL,tuple(l)))
        r.commutative_mul = True
        return r

    def __add__(self, other):
        other = self.convert(other, False)
        if isinstance(other, self.algebra_class):
            head = other.head
            elcls = self.element_classes
            if head is NUMBER:
                value = other.value
                if value==0:
                    return self
                return elcls[ADD]({self.one: value, self: 1})
            if head is SYMBOL:
                return elcls[ADD]({self: 1, other: 1})
            if head is ADD:
                result = other.copy()
                result._add_value(self, 1, 0)
                return result.canonize()
            if head is MUL:
                if self.pairs == other.pairs:
                    return elcls[ADD]({self:2})
                return elcls[ADD]({self: 1, other: 1})
            return self.Add([self, other])
        return NotImplemented

    def __mul__(self, other):
        other = self.convert(other, False)
        if isinstance(other, self.algebra_class):
            head = other.head
            if head is NUMBER:
                elcls = self.element_classes
                value = other.value
                if value==1:
                    return self
                if value==0:
                    return other
                return elcls[ADD]({self:value})
            if head is SYMBOL:
                result = self.copy()
                result._add_value(other, 1, 0)
                return result.canonize()
            if head is ADD:
                result = self.copy()
                result._add_value(other, 1, 0)
                return result.canonize()
            if head is MUL:
                if self.length() < other.length():
                    result = other.copy()
                    result._add_values(self, 1, 0)
                else:
                    result = self.copy()
                    result._add_values(other, 1, 0)
                return result.canonize()
            return self.Mul([self, other])
        return NotImplemented

    def expand(self):
        elcls = self.element_classes
        result = elcls[ADD]({})
        one = self.one
        pairs = self.pairs
        if len(pairs)==1:
            t, c = pairs.items()[0]
            t = t.expand()
            if c==1:
                return t
            head = t.head
            if head is NUMBER:
                return t ** c
            if head is SYMBOL:
                return elcls[MUL]({t:c})
            if head is MUL:
                t._multiply_values(c, 1, 0)
                return t
            if head is ADD:
                raise NotImplementedError(`t, head, c`)
            else:
                raise TypeError(`t, head`)
        it = pairs.iteritems()
        lhs = elcls[MUL]([it.next()]).expand()
        rhs = elcls[MUL](it).expand()
        h1 = lhs.head
        h2 = rhs.head
        if h1 is ADD:
            if h2 is ADD:
                lhs._expand_multiply_values(rhs.pairs.items(), 1, 0)
            elif h2 is NUMBER:
                lhs._multiply_values(rhs.value, 1, 0)
            else:
                lhs._expand_multiply_values([(rhs,1)], 1, 0)
            return lhs
        if h1 is NUMBER:
            if h2 is ADD:
                rhs._multiply_values(lhs.value, 1, 0)
                return rhs
            if h2 is NUMBER:
                return lhs * rhs
            return elcls[ADD]({rhs:lhs.value})
        if h1 is SYMBOL:
            if h2 is ADD:
                rhs._expand_multiply_values([(lhs,1)], 1, 0)
                return rhs
        return lhs * rhs

class PairsCommutativeSymbol(object):

    head = SYMBOL

    def __new__(cls, obj):
        o = object.__new__(cls)
        o.data = obj
        o._hash = None
        return o

    def __hash__(self):
        h = self._hash
        if h is None:
            self._hash = h = hash(self.data)
        return h

    def __eq__(self, other):
        if self is other:
            return True
        other = self.convert(other, False)
        if isinstance(other, type(self)):
            return self.data==other.data
        return False

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self.data)

    def as_primitive(self):
        return PrimitiveAlgebra((SYMBOL, self.data))

    def __add__(self, other):
        other = self.convert(other, False)
        if isinstance(other, self.algebra_class):
            head = other.head
            elcls = self.element_classes
            if head is NUMBER:
                value = other.value
                if value==0:
                    return self
                return elcls[ADD]({self:1, self.one:value})
            if head is SYMBOL:
                if self.data == other.data:
                    return elcls[ADD]({self: 2})
                return elcls[ADD]({self: 1, other: 1})
            if head is ADD:
                result = other.copy()
                result._add_value(self, 1, 0)
                return result.canonize()
            if head is MUL:
                return elcls[ADD]({self: 1, other: 1})
            return self.Add([self, other])
        return NotImplemented

    def __mul__(self, other):
        other = self.convert(other, False)
        if isinstance(other, self.algebra_class):
            head = other.head
            elcls = self.element_classes
            if head is NUMBER:
                value = other.value
                if value==1:
                    return self
                if value==0:
                    return other
                return elcls[ADD]({self:value})                
            if head is SYMBOL:
                if self.data==other.data:
                    return elcls[MUL]({self: 2})
                return elcls[MUL]({self: 1, other: 1})
            if head is ADD:
                if other.length()>1:
                    return elcls[MUL]({self:1, other: 1})
                t, c = other.pairs.items()[0]
                if t==self:
                    return elcls[ADD]({elcls[MUL]({t: 2}): c})
                return elcls[ADD]({elcls[MUL]({t: 1, self:1}): c})
            if head is MUL:
                result = other.copy()
                result._add_value(self, 1, 0)
                return result.canonize()
            return self.Mul([self, other])
        return NotImplemented

    def expand(self):
        return self

class PairsNumber(object):

    head = NUMBER

    def __new__(cls, p):
        if isinstance(p, cls):
            return p
        o = object.__new__(cls)
        o.value = p
        o._hash = None
        return o

    def __eq__(self, other):
        if self is other:
            return True
        other = self.convert(other, False)
        if isinstance(other, type(self)):
            return self.value==other.value
        return False

    def __hash__(self):
        h = self._hash
        if h is None:
            self._hash = h = hash(self.value)
        return h

    def __lt__(self, other):
        return self.value < other
    def __le__(self, other):
        return self.value <= other
    def __gt__(self, other):
        return self.value > other
    def __ge__(self, other):
        return self.value >= other
    def __ne__(self, other):
        return not (self.value == other)

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self.value)

    def __int__(self):
        return int(self.value)
    def __long__(self):
        return long(self.value)

    def as_primitive(self):
        value = self.value
        if value<0:
            return -PrimitiveAlgebra((NUMBER, -value))
        return PrimitiveAlgebra((NUMBER, value))

    def __abs__(self):
        return type(self)(abs(self.value))
    def __neg__(self):
        return type(self)(-self.value)

    def __add__(self, other):
        other = self.convert(other, False)
        if isinstance(other, self.algebra_class):
            if self.value==0:
                return other
            head = other.head
            elcls = self.element_classes
            if head is NUMBER:
                return elcls[NUMBER](self.value + other.value)
            if head is SYMBOL:
                return elcls[ADD]({self.one: self.value, other: 1})
            if head is ADD:
                result = other.copy()
                result._add_value(self.one, self.value, 0)
                return result.canonize()
            if head is MUL:
                return elcls[ADD]({self.one: self.value, other: 1})
            return self.Add([self, other])
        return NotImplemented

    def __mul__(self, other):
        other = self.convert(other, False)
        if isinstance(other, self.algebra_class):
            value = self.value
            head = other.head
            elcls = self.element_classes
            if head is NUMBER:
                return elcls[NUMBER](value * other.value)
            if value==1:
                return other
            if value==0:
                return self
            if head is SYMBOL:
                return elcls[ADD]({other:value})
            if head is ADD:
                result = other.copy()
                result._multiply_values(value, 1, 0)
                return result
            if head is MUL:
                return elcls[ADD]({other:value})
            return self.Mul([self, other])
        return NotImplemented

    def expand(self):
        return self
