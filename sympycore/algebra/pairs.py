import types

from ..core import classes
from .algebraic_structures import BasicAlgebra
from .primitive import PrimitiveAlgebra, ADD, MUL, SYMBOL, NUMBER
from .numberlib import mpq

def newinstance(cls, head, data, new = object.__new__):
    o = new(cls)
    o.head = head
    o.data = data
    return o

class CommutativeRingWithPairs(BasicAlgebra):
    """ Contains generic methods to algebra classes that
    use Pairs.
    """
    __slots__ = ['head', 'data', '_hash']
    one_c = 1   # one element of coefficient algebra
    one_e = 1   # one element of exponent algebra
    zero_c = 0  # zero element of coefficient algebra
    zero_e = 0  # zero element of exponent algebra

    _hash = None
    def __new__(cls, data, head=None):
        if head is None:
            if isinstance(data, cls):
                return data
            return cls.convert(data)
        if head in [ADD, MUL] and not isinstance(data, dict):
            data = dict(data)
        return newinstance(cls, head, data)

    def length(self):
        """ Return the number of pairs (if applicable).
        """
        # we don't define __len__ in order to avoid implementing sequence protocol
        # that will by misused by numpy.array
        if self.head in [ADD, MUL]:
            return len(self.data)
        raise TypeError('.length(): unexpected head value: %r' % (self.head))

    def __eq__(self, other):
        if self is other:
            return True
        if other.__class__ is self.__class__:
            return self.head is other.head and self.data == other.data
        if self.head is NUMBER and isinstance(other, self.algebra_numbers):
            return self.data == other
        return False

    def __hash__(self):
        h = self._hash
        if h is None:
            data = self.data
            if type(data) is dict:
                h = hash(frozenset(data.iteritems()))
            else:
                h = hash(data)
            self._hash = h
        return h

    def copy(self):
        if self.head in [ADD, MUL]:
            return newinstance(self.__class__, self.head, self.data.copy())
        return self

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self.data)

    def canonize(self):
        head = self.head
        if head is ADD:
            pairs = self.data
            if not pairs:
                return self.zero
            if len(pairs)==1:
                t, c = pairs.items()[0]
                if c==1:
                    return t
                if self.one==t:
                    return self.convert(c)
        elif head is MUL:
            pairs = self.data
            pairs.pop(self.one, None)
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
        head = self.head
        if head is ADD:
            l = []
            one_c = self.one_c
            one = self.one
            for t,c in self.data.iteritems():
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
        elif head is MUL:
            l = []
            one_c = self.one_c
            for t,c in self.data.iteritems():
                t = PrimitiveAlgebra(t)
                if one_c==c:
                    l.append(t)
                else:
                    l.append(t ** c)
            if len(l)==1:
                return l[0]
            r = PrimitiveAlgebra((MUL,tuple(l)))
            r.commutative_mul = True
        elif head is SYMBOL:
            r = PrimitiveAlgebra((SYMBOL, self.data))
        elif head is NUMBER:
            value = self.data
            if value<0:
                r = -PrimitiveAlgebra((NUMBER, -value))
            else:
                r = PrimitiveAlgebra((NUMBER, value))
        else:
            raise TypeError(`self, head`)
        return r

    def expand(self):
        return expand_dict[self.head](self)

    @classmethod
    def Add(cls, seq):
        terms = newinstance(cls, ADD,{})
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
                terms._add_value(one, t.data, zero_c)
            elif head is ADD:
                terms._add_values(t.data.iteritems(), one_c, zero_c)
            elif head is MUL:
                terms._add_value(t, one_c, zero_c)
            else:
                raise TypeError(`t, head`)
        return terms.canonize()

    @classmethod
    def Mul(cls, seq):
        result = newinstance(cls, MUL,{})
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
                number = number * t.data
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
            return newinstance(cls, NUMBER, number)
        head = result.head
        if head is NUMBER:
            return newinstance(cls, NUMBER, result * number)
        if head is ADD:
            r = result.copy()
            r._multiply_values(number, one_c, zero_c)
            return r.canonize()
        return newinstance(cls, ADD, {result:number})

    def __int__(self):
        assert self.head is NUMBER,`self`
        return int(self.data)
    def __long__(self):
        assert self.head is NUMBER,`self`
        return long(self.data)

    def __abs__(self):
        assert self.head is NUMBER,`self`
        return type(self)(abs(self.data))

    def __neg__(self):
        if self.head is NUMBER:
            return type(self)(-self.data)
        return -1 * self

    def __pos__(self):
        return self

    def __add__(self, other):
        other = self.convert(other, False)
        if other is NotImplemented:
            return NotImplemented
        return add_dict[self.head, other.head](self, other, self.__class__)

    def __mul__(self, other):
        other = self.convert(other, False)
        return multiply_dict[self.head, other.head](self, other, self.__class__)

    def __radd__(self, other):
        other = self.convert(other, False)
        if other is NotImplemented:
            return NotImplemented
        return add_dict[other.head, self.head](other, self, other.__class__)

    def __rmul__(self, other):
        other = self.convert(other, False)
        if other is NotImplemented:
            return NotImplemented
        return multiply_dict[other.head, self.head](other, self, other.__class__)

    def __lt__(self, other):
        return self.data < other
    def __le__(self, other):
        return self.data <= other
    def __gt__(self, other):
        return self.data > other
    def __ge__(self, other):
        return self.data >= other
    def __ne__(self, other):
        return not (self.data == other)

    def _add_value(self, rhs, one, zero):
        if self._hash is not None:
            raise TypeError('cannot add value to immutable pairs inplace'\
                            ' (hash has been computed)')
        pairs = self.data
        b = pairs.get(rhs)
        if b is None:
            pairs[rhs] = one
        else:
            c = b + one
            if c:
                pairs[rhs] = c
            else:
                del pairs[rhs]

    def _add_values(self, rhs, one, zero):
        if self._hash is not None:
            raise TypeError('cannot add values to immutable pairs inplace'\
                            ' (hash has been computed)')
        pairs = self.data
        for t,c in rhs:
            b = pairs.get(t)
            if b is None:
                pairs[t] = c
            else:
                c = b + c
                if c:
                    pairs[t] = c
                else:
                    del pairs[t]

    def _add_values_mul_coeff(self, rhs, coeff, zero):
        if self._hash is not None:
            raise TypeError('cannot add values to immutable pairs inplace'\
                            ' (hash has been computed)')
        pairs = self.data
        for t,c in rhs:
            b = pairs.get(t)
            if b is None:
                pairs[t] = c * coeff
            else:
                c = b + c * coeff
                if c:
                    pairs[t] = c
                else:
                    del pairs[t]

    def _multiply_values(self, rhs, one, zero):
        if self._hash is not None:
            raise TypeError('cannot multiply values to immutable pairs inplace'\
                            ' (hash has been computed)')
        d = {}
        for t,c in self.data.iteritems():
            d[t] = c * rhs
        self.data = d

class CommutativePairs: # XXX: to be removed
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


def expand_ADD(obj):
    result = newinstance(obj.__class__, ADD, {})
    one = obj.one
    for t,c in obj.data.iteritems():
        t = t.expand()
        head = t.head
        if head is NUMBER:
            result._add_value(one, t.data * c, 0)
        elif head is SYMBOL:
            result._add_value(t, c, 0)
        elif head is MUL:
            result._add_value(t, c, 0)
        elif head is ADD:
            p = t.data
            result._add_values_mul_coeff(p.items(), c, 0)
        else:
            raise TypeError(`t, head`)
    return result.canonize()

def expand_MUL(obj):
    cls = type(obj)
    pairs = obj.data
    if len(pairs)==1:
        t, c = pairs.items()[0]
        t = t.expand()
        if c==1:
            return t
        if c < 1:
            return t ** c
        head = t.head
        if head is NUMBER:
            return t ** c
        if head is SYMBOL:
            return newinstance(cls, MUL, {t:c})
        if head is MUL:
            t._multiply_values(c, 1, 0)
            return t
        if head is ADD:
            return expand_ADD_INTPOW(t, c, cls)
        else:
            raise TypeError(`t, head`)
    # split product into lhs * rhs:
    it = pairs.iteritems()
    t, c = it.next()
    if c==1:
        lhs = t.expand()
    else:
        lhs = newinstance(cls, MUL, {t:c}).expand()
    if len(pairs)==2:
        t, c = it.next()
        if c==1:
            rhs = t.expand()
        else:
            rhs = newinstance(cls, MUL, {t:c}).expand()
    else:
        rhs = newinstance(cls, MUL, dict(it)).expand()
    return expand_dict[lhs.head, rhs.head](lhs, rhs, cls)


####################################################################
# Implementation of binary operations +, *, and expanding products.

def add_NUMBER_NUMBER(lhs, rhs, cls):
    return newinstance(cls, NUMBER, lhs.data + rhs.data)

def add_NUMBER_SYMBOL(lhs, rhs, cls):
    if lhs.data==0:
        return rhs
    return newinstance(cls, ADD, {lhs.one: lhs.data, rhs: 1})

def add_NUMBER_ADD(lhs, rhs, cls):
    value = lhs.data
    if value==0:
        return rhs
    result = rhs.copy()
    pairs = result.data
    one = lhs.one
    b = pairs.get(one)
    if b is None:
        pairs[one] = value
    else:
        c = b + value
        if c:
            pairs[one] = c
        else:
            del pairs[one]
    return result

def add_NUMBER_MUL(lhs, rhs, cls):
    value = lhs.data
    if value==0:
        return rhs
    return newinstance(cls,ADD,{lhs.one: value, rhs: 1})

def add_SYMBOL_NUMBER(lhs, rhs, cls):
    value = rhs.data
    if value==0:
        return lhs
    return newinstance(cls,ADD,{lhs.one: value, lhs: 1})

def add_SYMBOL_SYMBOL(lhs, rhs, cls):
    if lhs.data==rhs.data:
        return newinstance(cls,ADD,{lhs: 2})
    return newinstance(cls,ADD,{lhs: 1, rhs: 1})

def add_SYMBOL_ADD(lhs, rhs, cls):
    result = rhs.copy()
    result._add_value(lhs, 1, 0)
    return result.canonize()

def add_SYMBOL_MUL(lhs, rhs, cls):
    return newinstance(cls,ADD,{lhs: 1, rhs: 1})

def add_ADD_NUMBER(lhs, rhs, cls):
    if rhs==0:
        return lhs
    result = lhs.copy()
    result._add_value(lhs.one, rhs.data, 0)
    return result.canonize()

def add_ADD_SYMBOL(lhs, rhs, cls):
    result = lhs.copy()
    result._add_value(rhs, 1, 0)
    return result.canonize()

def add_ADD_ADD(lhs, rhs, cls):
    if lhs.length() < rhs.length():
        rhs, lhs = lhs, rhs
    result = lhs.copy()
    pairs = result.data
    for t,c in rhs.data.iteritems():
        b = pairs.get(t)
        if b is None:
            pairs[t] = c
        else:
            c = b + c
            if c:
                pairs[t] = c
            else:
                del pairs[t]
    if len(pairs)<=1:
        return result.canonize()
    return result

def add_ADD_MUL(lhs, rhs, cls):
    result = lhs.copy()
    result._add_value(rhs, 1, 0)
    return result.canonize()

def add_MUL_NUMBER(lhs, rhs, cls):
    if rhs==0:
        return lhs
    return newinstance(cls,ADD,{lhs.one: rhs.data, lhs: 1})

add_MUL_SYMBOL = add_SYMBOL_MUL

def add_MUL_ADD(lhs, rhs, cls):
    result = rhs.copy()
    result._add_value(lhs, 1, 0)
    return result.canonize()

def add_MUL_MUL(lhs, rhs, cls):
    if lhs==rhs:
        return newinstance(cls,ADD,{lhs: 2})
    return newinstance(cls,ADD,{lhs: 1, rhs: 1})

def multiply_NUMBER_NUMBER(lhs, rhs, cls):
    return newinstance(cls, NUMBER, lhs.data * rhs.data)

def multiply_NUMBER_SYMBOL(lhs, rhs, cls):
    value = lhs.data    
    if value==1:
        return rhs
    if value==0:
        return lhs
    return newinstance(cls, ADD, {rhs:value})

def multiply_NUMBER_ADD(lhs, rhs, cls):
    value = lhs.data    
    if value==1:
        return rhs
    if value==0:
        return lhs
    result = newinstance(cls, ADD, {})
    d = result.data
    for t,c in rhs.data.iteritems():
        d[t] = c * value
    if len(d)==1:
        return result.canonize()
    return result

def multiply_NUMBER_MUL(lhs, rhs, cls):
    value = lhs.data    
    if value==1:
        return rhs
    if value==0:
        return lhs
    return newinstance(cls,ADD,{rhs:value})

def multiply_SYMBOL_NUMBER(lhs, rhs, cls):
    value = rhs.data    
    if value==1:
        return lhs
    if value==0:
        return rhs
    return newinstance(cls,ADD,{lhs:value})

def multiply_SYMBOL_SYMBOL(lhs, rhs, cls):
    if lhs==rhs:
        return newinstance(cls, MUL, {lhs:2})
    return newinstance(cls, MUL, {lhs:1, rhs:1})

def multiply_SYMBOL_ADD(lhs, rhs, cls):
    if rhs.length()>1:
        return newinstance(cls, MUL, {lhs:1, rhs: 1})
    t, c = rhs.data.items()[0]
    if lhs==t:
        return newinstance(cls,ADD,{newinstance(cls, MUL, {lhs: 2}): c})
    return newinstance(cls,ADD,{newinstance(cls, MUL, {lhs: 1, t:1}): c})

def multiply_SYMBOL_MUL(lhs, rhs, cls):
    result = rhs.copy()
    result._add_value(lhs, 1, 0)
    return result.canonize()

def multiply_ADD_NUMBER(lhs, rhs, cls):
    value = rhs.data    
    if value==1:
        return lhs
    if value==0:
        return rhs
    result = newinstance(cls,ADD,{})
    d = result.data
    for t,c in lhs.data.iteritems():
        d[t] = c * value
    if len(d)==1:
        return result.canonize()
    return result

def multiply_ADD_SYMBOL(lhs, rhs, cls):
    if lhs.length()>1:
        return newinstance(cls, MUL, {lhs:1, rhs: 1})
    t, c = lhs.data.items()[0]
    if rhs==t:
        return newinstance(cls,ADD,{newinstance(cls, MUL, {rhs: 2}): c})
    return newinstance(cls,ADD,{newinstance(cls, MUL, {rhs: 1, t:1}): c})

def multiply_ADD_ADD(lhs, rhs, cls):
    if lhs.length()==rhs.length()==1:
        t1, c1 = lhs.data.items()[0]
        t2, c2 = rhs.data.items()[0]
        t = t1 * t2
        if t==lhs.one:
            return c1*c2
        return newinstance(cls,ADD,{t: c1*c2})
    else:
        if lhs.data==rhs.data:
            return newinstance(cls, MUL, {lhs:2})
        return newinstance(cls, MUL, {lhs:1, rhs:1})

def multiply_ADD_MUL(lhs, rhs, cls):
    result = rhs.copy()
    if lhs.length()>1:
        result._add_value(lhs, 1, 0)
        return result.canonize()
    t, c = lhs.data.items()[0]
    result._add_value(t, 1, 0)
    result = result.canonize()
    return multiply_dict[result.head, NUMBER](result, newinstance(cls, NUMBER, c), cls)

def multiply_MUL_NUMBER(lhs, rhs, cls):
    value = rhs.data    
    if value==1:
        return lhs
    if value==0:
        return rhs
    return newinstance(cls,ADD,{lhs:value})

def multiply_MUL_SYMBOL(lhs, rhs, cls):
    result = lhs.copy()
    result._add_value(rhs, 1, 0)
    return result.canonize()

def multiply_MUL_ADD(lhs, rhs, cls):
    result = lhs.copy()
    if lhs.length()>1:
        result._add_value(rhs, 1, 0)
        return result.canonize()
    t, c = rhs.data.items()[0]
    result._add_value(t, 1, 0)
    result = result.canonize()
    return multiply_dict[result.head, NUMBER](result, newinstance(cls, NUMBER, c), cls)

def multiply_MUL_MUL(lhs, rhs, cls):
    if lhs.length() < rhs.length():
        rhs, lhs = lhs, rhs
    result = lhs.copy()
    pairs = result.data
    for t,c in rhs.data.iteritems():
        b = pairs.get(t)
        if b is None:
            pairs[t] = c
        else:
            c = b + c
            if c:
                pairs[t] = c
            else:
                del pairs[t]
    return result.canonize()

def expand_NUMBER_ADD(lhs, rhs, cls):
    value = lhs.data
    if value==0:
        return lhs
    if value==1:
        return rhs
    result = newinstance(cls,ADD,{})
    d = result.data
    for t,c in lhs.data.iteritems():
        d[t] = c * value
    return result

def expand_SYMBOL_ADD(lhs, rhs, cls):
    result = newinstance(cls,ADD,{})
    d = result.data
    for t,c in rhs.data.iteritems():
        d[t * lhs] = c
    return result

def expand_ADD_NUMBER(lhs, rhs, cls):
    value = rhs.data
    if value==0:
        return rhs
    if value==1:
        return lhs
    result = newinstance(cls,ADD,{})
    d = result.data
    for t,c in lhs.data.iteritems():
        d[t] = c * value
    return result

def expand_ADD_SYMBOL(lhs, rhs, cls):
    result = newinstance(cls,ADD,{})
    d = result.data
    for t,c in lhs.data.iteritems():
        d[t * rhs] = c
    return result

def expand_ADD_ADD(lhs, rhs, cls):
    if lhs.length() > rhs.length():
        lhs, rhs = rhs, lhs
    result = newinstance(cls,ADD,{})
    pairs1 = lhs.data
    pairs2 = rhs.data
    d = result.data
    for t1, c1 in pairs1.iteritems():
        for t2, c2 in pairs2.iteritems():
            t = t1 * t2
            c = c1 * c2
            b = d.get(t)
            if b is None:
                d[t] = c
            else:
                c = b + c
                if c:
                    d[t] = c
                else:
                    del d[t]
    return result

def expand_ADD_MUL(lhs, rhs, cls):
    result = newinstance(cls,ADD,{})
    d = result.data
    for t,c in lhs.data.iteritems():
        d[t * rhs] = c
    return result

def expand_MUL_ADD(lhs, rhs, cls):
    result = newinstance(cls,ADD,{})
    d = result.data
    for t,c in rhs.data.iteritems():
        d[t * lhs] = c
    return result

def expand_ADD_INTPOW(lhs, m, cls):
    terms = lhs.data.items()
    data = generate_expand_data(len(terms), int(m))
    result = newinstance(cls,ADD,{})
    d = result.data
    for exps, c in data.iteritems():
        t, n = exps.apply_to_terms(terms)
        t = newinstance(cls, MUL, dict(t)).canonize()
        b = d.get(t)
        if b is None:
            d[t] = n * c
        else:
            c = b + n * c
            if c:
                d[t] = c
            else:
                del d[t]
    return result

add_dict = {
    (NUMBER, NUMBER): add_NUMBER_NUMBER,
    (NUMBER, SYMBOL): add_NUMBER_SYMBOL,
    (NUMBER, ADD): add_NUMBER_ADD,
    (NUMBER, MUL): add_NUMBER_MUL,
    (SYMBOL, NUMBER): add_SYMBOL_NUMBER,
    (SYMBOL, SYMBOL): add_SYMBOL_SYMBOL,
    (SYMBOL, ADD): add_SYMBOL_ADD,
    (SYMBOL, MUL): add_SYMBOL_MUL,
    (ADD, NUMBER): add_ADD_NUMBER,
    (ADD, SYMBOL): add_ADD_SYMBOL,
    (ADD, ADD): add_ADD_ADD,
    (ADD, MUL): add_ADD_MUL,
    (MUL, NUMBER): add_MUL_NUMBER,
    (MUL, SYMBOL): add_MUL_SYMBOL,
    (MUL, ADD): add_MUL_ADD,
    (MUL, MUL): add_MUL_MUL,
    }

multiply_dict = {
    (NUMBER, NUMBER): multiply_NUMBER_NUMBER,
    (NUMBER, SYMBOL): multiply_NUMBER_SYMBOL,
    (NUMBER, ADD): multiply_NUMBER_ADD,
    (NUMBER, MUL): multiply_NUMBER_MUL,
    (SYMBOL, NUMBER): multiply_SYMBOL_NUMBER,
    (SYMBOL, SYMBOL): multiply_SYMBOL_SYMBOL,
    (SYMBOL, ADD): multiply_SYMBOL_ADD,
    (SYMBOL, MUL): multiply_SYMBOL_MUL,
    (ADD, NUMBER): multiply_ADD_NUMBER,
    (ADD, SYMBOL): multiply_ADD_SYMBOL,
    (ADD, ADD): multiply_ADD_ADD,
    (ADD, MUL): multiply_ADD_MUL,
    (MUL, NUMBER): multiply_MUL_NUMBER,
    (MUL, SYMBOL): multiply_MUL_SYMBOL,
    (MUL, ADD): multiply_MUL_ADD,
    (MUL, MUL): multiply_MUL_MUL,
    }

expand_dict = {
    NUMBER: lambda obj: obj,
    SYMBOL: lambda obj: obj,
    ADD: expand_ADD,
    MUL: expand_MUL,
    (NUMBER, NUMBER): multiply_NUMBER_NUMBER,
    (NUMBER, SYMBOL): multiply_NUMBER_SYMBOL,
    (NUMBER, ADD): expand_NUMBER_ADD,
    (NUMBER, MUL): multiply_NUMBER_MUL,
    (SYMBOL, NUMBER): multiply_SYMBOL_NUMBER,
    (SYMBOL, SYMBOL): multiply_SYMBOL_SYMBOL,
    (SYMBOL, ADD): expand_SYMBOL_ADD,
    (SYMBOL, MUL): multiply_SYMBOL_MUL,
    (ADD, NUMBER): expand_ADD_NUMBER,
    (ADD, SYMBOL): expand_ADD_SYMBOL,
    (ADD, ADD): expand_ADD_ADD,
    (ADD, MUL): expand_ADD_MUL,
    (MUL, NUMBER): multiply_MUL_NUMBER,
    (MUL, SYMBOL): multiply_MUL_SYMBOL,
    (MUL, ADD): expand_MUL_ADD,
    (MUL, MUL): multiply_MUL_MUL,
    }


###

class ExponentsTuple(tuple):

    def __div__(self, other):
        return self * other**-1

    def __mul__(self, other):
        assert isinstance(other, type(self)),`other`
        return self.__class__([i+j for i,j in zip(self,other)])

    def __pow__(self, e):
        assert isinstance(e, int),`e`
        return self.__class__([i*e for i in self])

    def apply_to_terms(self, terms):
        l = []
        num = 1
        j = None
        for i,e in enumerate(self):
            if e==0: continue
            t, c = terms[i]
            l.append((t, e))
            if c!=1:
                num = num * c**e
        return l, num

def generate_expand_data(n, m):
    """ Return power-coefficient dictionary of an expanded
    sum (A1 + A2 + .. + An)**m.
    """
    ## 
    ## Consider polynomial
    ##   P(x) = sum_{i=0}^n p_i x^k
    ## and its m-th exponent
    ##   P(x)^m = sum_{k=0}^{m n} a(m,k) x^k
    ## The coefficients a(m,k) can be computed using the
    ## J.C.P. Miller Pure Recurrence [see D.E.Knuth,
    ## Seminumerical Algorithms, The art of Computer
    ## Programming v.2, Addison Wesley, Reading, 1981;]:
    ##  a(m,k) = 1/(k p_0) sum_{i=1}^n p_i ((m+1)i-k) a(m,k-i),
    ## where a(m,0) = p_0^m.
    
    symbols = [ExponentsTuple((0,)*i + (1,) +(0,)*(n-i-1)) for i in range(n)]
    s0 = symbols[0]
    p0 = [s/s0 for s in symbols]
    r = {s0**m:1}
    l = [r.items()]
    for k in xrange(1, m*(n-1)+1):
        d = {}
        for i in xrange(1, min(n,k+1)):
            nn = (m+1)*i-k
            if nn:
                t = p0[i]
                for t2, c2 in l[k-i]:
                    tt = t2 * t
                    cc = mpq(nn * c2, k)
                    b = d.get(tt)
                    if b is None:
                        d[tt] = cc
                    else:
                        cc = b + cc
                        if cc:
                            d[tt] = cc
                        else:
                            del d[tt]
        r1 = d.items()
        l.append(r1)
        for t, c in r1:
            b = r.get(t)
            if b is None:
                r[t] = c
            else:
                c = b + c
                if c:
                    r[t] = c
                else:
                    del r[t]
    return r
