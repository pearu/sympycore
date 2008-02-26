#
# Author: Pearu Peterson
# Created: January 2008

import types
from collections import defaultdict

from ..core import classes
from ..utils import str_SUM, str_PRODUCT, str_POWER, str_APPLY, str_SYMBOL, str_NUMBER
from ..utils import ADD, MUL, SYMBOL, NUMBER, APPLY, POW, TUPLE, head_to_string, TERMS, FACTORS

from .utils import generate_swapped_first_arguments
from .algebra import BasicAlgebra
from .ring import CommutativeRing
from .primitive import PrimitiveAlgebra
from ..arithmetic.numbers import FractionTuple
from ..arithmetic.number_theory import multinomial_coefficients

from .pairs_ops import (add_method, sub_method, rsub_method, neg_method,
                        mul_method, div_method, rdiv_method, pow_method)

from .pairs_iops import (inplace_add, inplace_add2, inplace_sub,
                         return_terms, return_factors,
                         inplace_mul, inplace_mul2)

from .pairs_expand import expand

def newinstance(cls, head, data, new = object.__new__):
    o = new(cls)
    o.head = head
    o.data = data
    return o

def inspect(obj):
    obj.inspect()

inttypes = (int, long)

class CommutativeRingWithPairs(CommutativeRing):
    """ Implementation of a commutative ring where sums and products
    are represented as dictionaries of pairs.
    """
    __slots__ = ['head', 'data', '_hash',
                 '_symbols', '_symbols_data',
                 '_has_active']
    one_c = 1   # one element of coefficient algebra
    one_e = 1   # one element of exponent algebra
    zero_c = 0  # zero element of coefficient algebra
    zero_e = 0  # zero element of exponent algebra

    _hash = None
    _symbols = None
    _symbols_data = None

    coefftypes = (int, long, FractionTuple)
    exptypes = (int, long, FractionTuple)

    _coeff_terms = (1, None) # set by MUL_VALUE_TERMS
    __neg__ = neg_method
    __add__ = __radd__ = add_method
    __sub__ = sub_method
    __rsub__ = rsub_method
    __mul__ = __rmul__ = mul_method
    __div__ = div_method
    __rdiv__ = rdiv_method
    __pow__ = pow_method
    expand = expand

    def __new__(cls, data, head=None):
        if head is None:
            if isinstance(data, cls):
                return data
            return cls.convert(data)
        if head in [ADD, MUL] and not isinstance(data, dict):
            data = dict(data)
        return newinstance(cls, head, data)

    def __eq__(self, other):
        if self is other:
            return True
        to = type(other)
        if to is type(self):
            return self.head == other.head and self.data == other.data
        if self.head is NUMBER and (to is int or to is long):
            return self.data == other
        return False

    def __hash__(self):
        h = self._hash
        if not h:
            data = self.data
            if type(data) is dict:
                h = hash(frozenset(data.iteritems()))
            else:
                h = hash(data)
            self._hash = h
        return h

    def __nonzero__(self):
        return self.head is not NUMBER or bool(self.data)

    def copy(self):
        if self.head in [ADD, MUL]:
            return newinstance(type(self), self.head, dict(self.data))
        return self

    #def __repr__(self):
    #    return '%s(%r, head=%s)' % (type(self).__name__, self.data, head_to_string[self.head])

    def as_tree(self, tab='', level=0):
        if level:
            r = []
        else:
            r = [type(self).__name__+':']
        data = self.data
        head = self.head
        if head in [SYMBOL, NUMBER]:
            r.append(tab + '%s[%s]' % (head_to_string[head], data))
        elif head in [ADD, MUL]:
            r.append(tab + '%s[' % (head_to_string[head]))
            for t,c in data.iteritems():
                r.append(t.as_tree(tab=tab + ('  %s:' % (str(c))), level=level+1))
            r.append(tab+']')
        elif callable(head):
            r.append(tab + '%s[%s]' % (head, data))
        else:
            raise NotImplementedError(`self, head`)
        return '\n'.join(r)

    @classmethod
    def coefficient_to_str_data(cls, obj, sort=True):
        if isinstance(obj, inttypes):
            if obj < 0:
                return str_SUM, str(obj)
            return str_NUMBER, str(obj)
        if hasattr(obj, 'to_str_data'):
            return obj.to_str_data(sort)
        raise NotImplementedError('%s.coefficient_to_str_data(%r)' % (cls.__name__, obj))

    @classmethod
    def exponent_to_str_data(cls, obj, sort=True):
        if isinstance(obj, inttypes):
            if obj < 0:
                return str_SUM, str(obj)
            return str_NUMBER, str(obj)
        if hasattr(obj, 'to_str_data'):
            return obj.to_str_data(sort)
        raise NotImplementedError('%s.exponent_to_str_data(%r)' % (cls.__name__, obj))

    @classmethod
    def callable_to_str_data(cls, obj, sort=True):
        if isinstance(obj, BasicAlgebra):
            return obj.to_str_data(sort=True)
        if hasattr(obj, '__name__'):
            return str_SYMBOL, obj.__name__
        return str_SYMBOL, str(obj)

    def __str__(self):
        return self.to_str_data()[1]

    def to_str_data(self, sort=True):
        head = self.head
        one = self.one
        cls = type(self)
        if head is NUMBER:
            return cls.coefficient_to_str_data(self.data, sort)
        if head is ADD:
            pos_dict = {}
            neg_dict = {}
            for t, c in self.data.iteritems():
                if c<0:
                    d = neg_dict
                    c = -c
                else:
                    d = pos_dict
                h1, s1 = cls.coefficient_to_str_data(c, sort)
                h2, s2 = t.to_str_data(sort)
                if t is one:
                    h, s = h1, s1
                elif c==1:
                    h, s = h2, s2
                else:
                    if h1 > str_PRODUCT:
                        s1 = '(%s)' % (s1)
                    if h2 > str_PRODUCT:
                        s2 = '(%s)' % (s2)
                    s = '%s*%s' % (s1,s2)
                    h = str_PRODUCT
                l = d.get(h)
                if l is None:
                    l = d[h] = []
                l.append(s)
            if sort:
                r1 = []
                for k in sorted(pos_dict):
                    r1 += sorted(pos_dict[k])
                r2 = []
                for k in sorted(neg_dict):
                    r2 += sorted(neg_dict[k])
            else:
                r1 = reduce(lambda x,y:x+y, pos_dict.values(),[])
                r2 = reduce(lambda x,y:x+y, neg_dict.values(),[])
            if r1:
                if r2:
                    return str_SUM, (' + '.join(r1)) + ' - ' + (' - '.join(r2))
                if len(r1)>1:
                    return str_SUM, (' + '.join(r1))
                h,l = pos_dict.items()[0]
                return h, l[0]
            return str_SUM, '-' + (' - '.join(r2))
        if head is MUL:
            d = {}
            for t, c in self.data.iteritems():
                h1, s1 = t.to_str_data(sort)
                h2, s2 = cls.exponent_to_str_data(c, sort)
                if c==1:
                    if h1 > str_POWER:
                        s1 = '(%s)' % (s1)
                    h, s = h1, s1
                else:
                    if h1 >= str_POWER:
                        s1 = '(%s)' % (s1)
                    if h2 >= str_POWER:
                        s2 = '(%s)' % (s2)
                    s = '%s**%s' % (s1, s2)
                    h = str_POWER
                l = d.get(h)
                if l is None:
                    l = d[h] = []
                l.append(s)
            if sort:
                r1 = []
                for k in sorted(d):
                    r1 += sorted(d[k])
            else:
                r1 = reduce(lambda x,y:x+y, d.values(),[])
            if len(r1)>1:
                return str_PRODUCT, '*'.join(r1)
            h, l = d.items()[0]
            return h, l[0]
        if callable(head):
            h1, s1 = cls.callable_to_str_data(head, sort)
            if h1 > str_APPLY:
                s1 = '(%s)' % (s1)
            args = self.data
            if type(args) is not tuple:
                args = args,
            s2 = ', '.join([a.to_str_data(sort)[1] for a in args])
            return str_APPLY, '%s(%s)' % (s1, s2)
        return str_SYMBOL, str(self.data)

    @property
    def func(self):
        head = self.head
        data = self.data
        if head is SYMBOL or head is NUMBER:
            return lambda : self
        elif head is ADD:
            if len(self.data)==1:
                return self.Mul
            return self.Add
        elif head is MUL:
            if len(data)>1:
                return self.Mul
            return self.Pow
        elif callable(head):
            return head
        raise NotImplementedError(`self, head`)

    @property
    def args(self):
        head = self.head
        if head is SYMBOL or head is NUMBER:
            return []
        elif head is ADD:
            if len(self.data)==1:
                t, c = self.data.items()[0]
                return [self.convert(c)] + t.as_Mul_args()
            return self.as_Add_args()
        elif head is MUL:
            if len(self.data)>1:
                return self.as_Mul_args()
            return self.as_Pow_args()
        elif callable(head):
            data = self.data
            if type(data) is tuple:
                return data
            return data,
        raise NotImplementedError(`self, head`)

    @property
    def is_Add(self):
        return self.head is ADD and len(self.data) > 1

    @property
    def is_Mul(self):
        return (self.head is ADD and len(self.data) == 1) \
            or (self.head is MUL and len(self.data) > 1)

    @property
    def is_Pow(self):
        return self.head is MUL and len(self.data) == 1

    @property
    def is_Number(self):
        return self.head is NUMBER

    @property
    def is_Symbol(self):
        return self.head is SYMBOL

    def as_Add_args(self):
        head = self.head
        data = self.data
        if head is ADD:
            if len(data)==1:
                return [self]
            return [t * c for t,c in data.iteritems()]
        return [self]

    def as_Mul_args(self):
        head = self.head
        data = self.data
        if head is ADD and len(data)==1:
            t,c = data.items()[0]
            return [self.convert(c)] + t.as_Mul_args()
        if head is MUL:
            if len(data)==1:
                return [self]
            l = []
            for t,c in data.iteritems():
                if c==1:
                    l.extend(t.as_Mul_args())
                else:
                    l.append(t**c)
            return l
        return [self]

    def as_Pow_args(self):
        head = self.head
        data = self.data
        if head is MUL:
            if len(data)==1:
                return data.items()[0]
            return [self, self.one_e] #XXX: improve me
        return [self, self.one_e]

    def as_Terms_args(self):
        head = self.head
        if head is NUMBER:
            return [(self.one, self.data)]
        if head is ADD:
            return self.data.items()
        return [(self, self.one_c)]

    def as_Factors_args(self):
        head = self.head
        if head is MUL:
            return self.data.items()
        return [(self, self.one_e)]
    
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
        func = self.func
        args = self.args
        if func==self.Add:
            r = PrimitiveAlgebra((ADD,tuple(map(PrimitiveAlgebra, args))))
            r.commutative_add = True
        elif func==self.Mul:
            if args[0].head is NUMBER and args[0].data < 0:
                if args[0].data==-1:
                    args = map(PrimitiveAlgebra,args[1:])
                    if len(args)==1:
                        self._primitive = r = -args[0]
                        return r
                else:
                    args = [PrimitiveAlgebra(-args[0])] + map(PrimitiveAlgebra,args[1:])
                r = PrimitiveAlgebra((MUL,tuple(args)))
                r.commutative_mul = True
                r = -r
            else:
                args = map(PrimitiveAlgebra, args)
                r = PrimitiveAlgebra((MUL,tuple(args)))
            r.commutative_mul = True
        elif func==self.Pow:
            r = PrimitiveAlgebra((POW, tuple(map(PrimitiveAlgebra, args))))
        elif head is NUMBER:
            value = self.data
            if hasattr(value, 'as_primitive'):
                r = value.as_primitive()
            elif isinstance(value, (int, long, float)) and value<0:
                r = -PrimitiveAlgebra((NUMBER, -value))
            else:
                r = PrimitiveAlgebra((NUMBER, value))
        elif head is SYMBOL:
            data = self.data
            if hasattr(data, 'as_primitive'):
                r = data.as_primitive()
            else:
                r = PrimitiveAlgebra((SYMBOL, self.data))
        elif callable(head):
            data = self.data
            if hasattr(data, 'as_primitive'):
                args = data.as_primitive(),
            elif isinstance(data, tuple):
                args = tuple(map(PrimitiveAlgebra, data))
            else:
                args = PrimitiveAlgebra(data),
            r = PrimitiveAlgebra((APPLY, (head,)+args))
        else:
            data = self.data
            if hasattr(data, 'as_primitive'):
                r = data.as_primitive()
            else:
                r = PrimitiveAlgebra((SYMBOL, (self.head,self.data)))
        return r

    def old_expand(self):
        return expand_dict1[self.head](self, type(self))

    @classmethod
    def Symbol(cls, obj):
        return newinstance(cls, SYMBOL, obj)

    @classmethod
    def Number(cls, obj):
        return newinstance(cls, NUMBER, obj)

    @classmethod
    def Add(cls, *seq):
        d = {}
        d_get = d.get
        one = cls.one
        for t in seq:
            inplace_add(cls, t, d, d_get, one)
        return return_terms(cls, d)

    @classmethod
    def Sub(cls, *seq):
        d = {}
        d_get = d.get
        one = cls.one
        if seq:
            inplace_sub(cls, seq[0], d, d_get, one)
        for t in seq[1:]:
            inplace_sub(cls, t, d, d_get, one)
        return return_terms(cls, d)

    @classmethod
    def Terms(cls, *seq):
        d = {}
        d_get = d.get
        one = cls.one
        for t,c in seq:
            inplace_add2(cls, t, c, d, d_get, one)
        return return_terms(cls, d)

    @classmethod
    def Mul(cls, *seq):
        d = {}
        d_get = d.get
        number = 1
        for t in seq:
            n = inplace_mul(cls, t, d, d_get)
            if n is not 1:
                number = number * n
        r = return_factors(cls, d)
        if number is 1:
            return r
        return r * number

    @classmethod
    def Factors(cls, *seq):
        d = {}
        d_get = d.get
        number = 1
        for t, c in seq:
            n = inplace_mul2(cls, t, c, d, d_get)
            if n is not 1:
                number = number * n
        r = return_factors(cls, d)
        if number is 1:
            return r
        return r * number

    @classmethod
    def npower(cls, base, exp):
        return pow_coeff_int(base, exp, cls)

    @classmethod
    def Pow(cls, base, exp):
        if isinstance(exp, cls):
            if exp.head is NUMBER:
                exp = exp.data
            else:
                return pow_dict2[base.head][exp.head](base, exp, cls)
        if base.head is NUMBER:
            return cls.npower(base.data, exp)
        if isinstance(exp, inttypes):
            return pow_dict1[base.head](base, exp, cls)
        return pow_dict2[base.head][NUMBER](base, newinstance(cls, NUMBER, exp), cls)

    def __int__(self):
        assert self.head is NUMBER,`self`
        return int(self.data)

    def __long__(self):
        assert self.head is NUMBER,`self`
        return long(self.data)

    def __abs__(self):
        assert self.head is NUMBER,`self`
        return type(self)(abs(self.data))

    def __pos__(self):
        return self

    def __lt__(self, other):
        return self.data < other
    def __le__(self, other):
        return self.data <= other
    def __gt__(self, other):
        return self.data > other
    def __ge__(self, other):
        return self.data >= other
    def __ne__(self, other):
        return not (self == other)

    def _get_symbols_data(self):
        _symbols_data = self._symbols_data
        if _symbols_data is None:
            head = self.head
            if head is SYMBOL:
                _symbols_data = set([self.data])
            elif head is NUMBER:
                _symbols_data = set()
            elif head is ADD:
                _symbols_data = set()
                for k in self.data:
                    _symbols_data |= k._get_symbols_data()
            elif head is MUL:
                _symbols_data = set()
                cls = type(self)
                for k, c in self.data.iteritems():
                    _symbols_data |= k._get_symbols_data()
                    if isinstance(c, cls):
                        _symbols_data |= c._get_symbols_data()
            else:
                _symbols_data = set()
                for arg in self.args:
                    _symbols_data |= arg._get_symbols_data()
            self._symbols_data = _symbols_data
        return _symbols_data

    @property
    def symbols(self):
        symbols = self._symbols
        if symbols is None:
            cls = type(self)
            symbols = self._symbols = set([newinstance(cls, SYMBOL, d) for d in self._get_symbols_data()])
        return symbols

    def has_symbol(self, symbol):
        return symbol.data in self._get_symbols_data()

    def has(self, subexpr):
        subexpr = self.convert(subexpr)
        if subexpr.head is SYMBOL:
            return subexpr.data in self._get_symbols_data()
        raise NotImplementedError('%s.has(%r)' % (type(self).__name__, subexpr))

    def _subs(self, subexpr, newexpr):
        head = self.head

        if head is subexpr.head:
            if self.data == subexpr.data:
                return newexpr

        if head is SYMBOL or head is NUMBER:
            return self
            
        cls = type(self)

        if head is ADD:
            d = {}
            d_get = d.get
            one = cls.one
            for t,c in self.data.iteritems():
                r = t._subs(subexpr, newexpr)
                if c is 1:
                    inplace_add(cls, r, d, d_get, one)
                else:
                    inplace_add2(cls, r, c, d, d_get, one)
            return return_terms(cls, d)

        elif head is MUL:
            d = {}
            d_get = d.get
            num = 1
            for t,c in self.data.iteritems():
                r = t._subs(subexpr, newexpr)
                if type(c) is cls:
                    c = c._subs(subexpr, newexpr)
                if c is 1:
                    n = inplace_mul(cls, r, d, d_get)
                else:
                    n = inplace_mul2(cls, r, c, d, d_get)
                if n is not 1:
                    num = num * n
            r = return_factors(cls, d)
            if num is 1:
                return r
            return r * num

        elif callable(head):
            args = self.data
            if type(args) is tuple:
                args = [a._subs(subexpr, newexpr) for a in args]
                return head(*args)
            else:
                return head(args._subs(subexpr, newexpr))

        raise NotImplementedError(`self`)

A = CommutativeRingWithPairs
A.one = A.Number(1)
A.zero = A.Number(0)

def pow_coeff_int(lhs, rhs, cls):
    if not rhs or lhs==1:
        return cls.one
    if rhs > 0:
        return newinstance(cls, NUMBER, lhs ** rhs)
    r = pow_coeff_int(lhs, -rhs, cls)
    return newinstance(cls, MUL, {r:-1})

def pow_NUMBER_int(lhs, rhs, cls):
    if not rhs:
        return cls.one
    if rhs==1:
        return lhs
    value = lhs.data
    if rhs > 0:
        return newinstance(cls, NUMBER, value ** rhs)
    if value==1:
        return lhs
    r = pow_NUMBER_int(lhs, -rhs, cls)
    return newinstance(cls, MUL, {r:-1})

def pow_SYMBOL_int(lhs, rhs, cls):
    if not rhs:
        return cls.one
    if rhs==1:
        return lhs
    return newinstance(cls, MUL, {lhs:rhs})

def pow_ADD_int(lhs, rhs, cls):
    if not rhs:
        return cls.one
    if rhs==1:
        return lhs
    pairs = lhs.data
    if len(pairs)==1:
        t, c = pairs.items()[0]
        return pow_dict1[t.head](t, rhs, cls) * pow_coeff_int(c, rhs, cls)
    return newinstance(cls, MUL, {lhs:rhs})

def pow_MUL_int(lhs, rhs, cls):
    if not rhs:
        return cls.one
    if rhs==1:
        return lhs
    pairs = lhs.data
    if len(pairs)==1:
        t, c = pairs.items()[0]
        if isinstance(c, inttypes):
            return pow_dict1[t.head](t, c*rhs, cls)
    d = {}
    r = newinstance(cls, MUL, d)
    for t,c in pairs.iteritems():
        d[t] = c * rhs
    return r

def pow_NUMBER_NUMBER(lhs, rhs, cls):
    if isinstance(rhs.data, inttypes):
        return pow_NUMBER_int(lhs, rhs.data, cls)
    return newinstance(cls, MUL, {lhs:rhs})

def pow_NUMBER_ADD(lhs, rhs, cls):
    pairs = rhs.data
    if len(pairs)==1:
        t,c = pairs.items()[0]
        if isinstance(c, inttypes):
            lhs = pow_NUMBER_int(lhs, c, cls)
            rhs = t
    return newinstance(cls, MUL, {lhs:rhs})

def pow_NUMBER_MUL(lhs, rhs, cls):
    return newinstance(cls, MUL, {lhs:rhs})

def pow_NUMBER_SYMBOL(lhs, rhs, cls):
    r = lhs.data.__pow__(rhs)
    if r is not NotImplemented:
        return cls.convert(r)
    return newinstance(cls, MUL, {lhs:rhs})

def pow_ADD_NUMBER(lhs, rhs, cls):
    if isinstance(rhs.data, inttypes):
        return pow_ADD_int(lhs, rhs.data, cls)
    return newinstance(cls, MUL, {lhs:rhs})

def pow_ADD_ADD(lhs, rhs, cls):
    pairs = lhs.data
    if len(pairs)==1:
        t, c = pairs.items()[0]
        c = cls.convert(c)
        return c**rhs * t**rhs
    return newinstance(cls, MUL, {lhs:rhs})

def pow_ADD_MUL(lhs, rhs, cls):
    return newinstance(cls, MUL, {lhs:rhs})

def pow_ADD_SYMBOL(lhs, rhs, cls):
    return newinstance(cls, MUL, {lhs:rhs})

def pow_MUL_NUMBER(lhs, rhs, cls):
    if isinstance(rhs.data, inttypes):
        return pow_MUL_int(lhs, rhs.data, cls)
    return newinstance(cls, MUL, {lhs:rhs})

def pow_MUL_ADD(lhs, rhs, cls):
    pairs = lhs.data
    if len(pairs)==1:
        t,c = pairs.items()[0]
        lhs = t
        c = cls.convert(c)
        rhs = mul_NUMBER_dict[rhs.head](c, rhs, cls)
    return newinstance(cls, MUL, {lhs:rhs})

def pow_MUL_MUL(lhs, rhs, cls):
    pairs = lhs.data
    if len(pairs)==1:
        t, c = pairs.items()[0]
        if isinstance(c, inttypes):
            lhs = t
            c = cls.convert(c)
            rhs = mul_NUMBER_dict[rhs.head](c, rhs, cls)
    return newinstance(cls, MUL, {lhs:rhs})

def pow_MUL_SYMBOL(lhs, rhs, cls):
    pairs = lhs.data
    if len(pairs)==1:
        t, c = pairs.items()[0]
        if isinstance(c, inttypes):
            lhs = pow_dict2[t.head][rhs.head](t, rhs, cls)
            rhs = cls.convert(c)
    return newinstance(cls, MUL, {lhs:rhs})

def pow_SYMBOL_NUMBER(lhs, rhs, cls):
    value = rhs.data
    if isinstance(value, inttypes):
        return pow_SYMBOL_int(lhs, value, cls)
    r = value.__rpow__(lhs)
    if r is not NotImplemented:
        return cls.convert(r)
    return newinstance(cls, MUL, {lhs:rhs})

def pow_SYMBOL_ADD(lhs, rhs, cls):
    pairs = rhs.data
    if len(pairs)==1:
        t,c = pairs.items()[0]
        if isinstance(c, inttypes):
            lhs = pow_dict2[lhs.head][t.head](lhs, t, cls)
            rhs = cls.convert(c)
    return newinstance(cls, MUL, {lhs:rhs})

def pow_SYMBOL_MUL(lhs, rhs, cls):
    return newinstance(cls, MUL, {lhs:rhs})

def pow_SYMBOL_SYMBOL(lhs, rhs, cls):
    return newinstance(cls, MUL, {lhs:rhs})

####################################################################
# Implementation of binary operations +, *, and expanding products.

def multiply_NUMBER_NUMBER(lhs, rhs, cls):
    return newinstance(cls, NUMBER, lhs.data * rhs.data)

def multiply_NUMBER_SYMBOL(lhs, rhs, cls):
    value = lhs.data
    if not value:
        return lhs
    if value==1:
        return rhs
    return newinstance(cls, ADD, {rhs:value})

generate_swapped_first_arguments(multiply_NUMBER_SYMBOL)

def multiply_NUMBER_ADD(lhs, rhs, cls):
    value = lhs.data
    if value==1:
        return rhs
    d = {}
    result = newinstance(cls, ADD, d)
    for t,c in rhs.data.iteritems():
        c = c * value
        if c:
            d[t] = c
    if len(d)<=1:
        return result.canonize()
    return result

generate_swapped_first_arguments(multiply_NUMBER_ADD)

def multiply_NUMBER_MUL(lhs, rhs, cls):
    value = lhs.data
    if not value:
        return lhs
    if value==1:
        return rhs
    b = rhs.data.get(lhs)
    if b is not None:
        result = rhs.copy()
        pairs = result.data
        c = b + cls.one_e
        if c:
            pairs[lhs] = c
            return result
        else:
            del pairs[lhs]
        if len(pairs)<=1:
            return result.canonize()
        return result
    return newinstance(cls,ADD,{rhs:value})

generate_swapped_first_arguments(multiply_NUMBER_MUL)

def multiply_SYMBOL_SYMBOL(lhs, rhs, cls):
    if lhs==rhs:
        return newinstance(cls, MUL, {lhs:2})
    return newinstance(cls, MUL, {lhs:1, rhs:1})

def multiply_SYMBOL_ADD(lhs, rhs, cls):
    pairs = rhs.data
    if len(pairs)==1:
        t, c = pairs.items()[0]
        if lhs==t:
            return newinstance(cls,ADD,{newinstance(cls, MUL, {lhs: 2}): c})
        return multiply_dict2[lhs.head][t.head](lhs, t, cls) * c
    return newinstance(cls, MUL, {lhs:1, rhs: 1})

generate_swapped_first_arguments(multiply_SYMBOL_ADD)

def multiply_SYMBOL_MUL(lhs, rhs, cls):
    result = rhs.copy()
    pairs = result.data
    b = pairs.get(lhs)
    if b is None:
        pairs[lhs] = 1
    else:
        c = b + 1
        if c:
            pairs[lhs] = c
        else:
            del pairs[lhs]
    if len(pairs)<=1:
        return result.canonize()
    return result

generate_swapped_first_arguments(multiply_SYMBOL_MUL)

def multiply_ADD_ADD(lhs, rhs, cls):
    ldata = lhs.data
    rdata = rhs.data
    if len(ldata)==1:
        t1, c1 = ldata.items()[0]
        if len(rdata)==1:
            t2, c2 = rdata.items()[0]
            t = multiply_dict2[t1.head][t2.head](t1, t2, cls)
            if t==cls.one:
                return newinstance(cls, NUMBER, c1*c2)
            return newinstance(cls,ADD,{t: c1*c2})
        r = newinstance(cls, MUL, {t1:1, rhs:1})
        return newinstance(cls, ADD, {r: c1})
    elif len(rdata)==1:
        t2, c2 = rdata.items()[0]
        r = newinstance(cls, MUL, {t2:1, lhs:1})
        return newinstance(cls, ADD, {r: c2})
    else:
        if ldata==rdata:
            return newinstance(cls, MUL, {lhs:2})
        return newinstance(cls, MUL, {lhs:1, rhs:1})

def multiply_ADD_MUL(lhs, rhs, cls):
    ldata = lhs.data
    if len(ldata)==1:
        t, c = ldata.items()[0]
        return multiply_dict2[t.head][rhs.head](t, rhs, cls) * c
    result = rhs.copy()
    pairs = result.data
    b = pairs.get(lhs)
    if b is None:
        pairs[lhs] = 1
    else:
        c = b + 1
        if c:
            pairs[lhs] = c
        else:
            del pairs[lhs]
    if len(pairs)<=1:
        return result.canonize()
    return result

generate_swapped_first_arguments(multiply_ADD_MUL)

def multiply_MUL_MUL(lhs, rhs, cls):
    ldata = lhs.data
    rdata = rhs.data
    if len(ldata) < len(rdata):
        rhs, lhs = lhs, rhs
        ldata, rdata = rdata, ldata
    pairs = dict(ldata)
    result = newinstance(cls, MUL, pairs)
    get = pairs.get
    number = 1
    for t,c in rdata.iteritems():
        b = get(t)
        if b is None:
            pairs[t] = c
        else:
            c = b + c
            if c:
                if t.head is NUMBER:
                    r = t**c
                    if r.head is NUMBER:
                        number = number * r
                        del pairs[t]
                    else:
                        pairs[t] = c
                else:
                    pairs[t] = c
            else:
                del pairs[t]
    if len(pairs)<=1:
        result = result.canonize()
    if number==1:
        return result
    return result * number

# function maps:

pow_dict1 = defaultdict(lambda: pow_SYMBOL_int,
                        {NUMBER: pow_NUMBER_int,
                         ADD: pow_ADD_int,
                         MUL: pow_MUL_int
                         })

pow_ADD_dict = defaultdict(lambda: pow_ADD_SYMBOL,
                           {NUMBER: pow_ADD_NUMBER,
                            ADD: pow_ADD_ADD,
                            MUL: pow_ADD_MUL})

pow_MUL_dict = defaultdict(lambda: pow_MUL_SYMBOL,
                           {NUMBER: pow_MUL_NUMBER,
                            ADD: pow_MUL_ADD,
                            MUL: pow_MUL_MUL})

pow_NUMBER_dict = defaultdict(lambda: pow_NUMBER_SYMBOL,
                              {NUMBER: pow_NUMBER_NUMBER,
                               ADD: pow_NUMBER_ADD,
                               MUL: pow_NUMBER_MUL})

pow_SYMBOL_dict = defaultdict(lambda: pow_SYMBOL_SYMBOL,
                              {NUMBER: pow_SYMBOL_NUMBER,
                               ADD: pow_SYMBOL_ADD,
                               MUL: pow_SYMBOL_MUL})


pow_dict2 = defaultdict(lambda: pow_SYMBOL_dict,
                        {NUMBER: pow_NUMBER_dict,
                         ADD: pow_ADD_dict,
                         MUL: pow_MUL_dict})


mul_NUMBER_dict = defaultdict(lambda:multiply_NUMBER_SYMBOL,
                              {NUMBER: multiply_NUMBER_NUMBER,
                               ADD: multiply_NUMBER_ADD,
                               MUL: multiply_NUMBER_MUL,
                               })

mul_ADD_dict = defaultdict(lambda:multiply_ADD_SYMBOL,
                           {NUMBER: multiply_ADD_NUMBER,
                            ADD: multiply_ADD_ADD,
                            MUL: multiply_ADD_MUL,
                            })

mul_MUL_dict = defaultdict(lambda:multiply_MUL_SYMBOL,
                           {NUMBER: multiply_MUL_NUMBER,
                            ADD: multiply_MUL_ADD,
                            MUL: multiply_MUL_MUL,
                            })

mul_SYMBOL_dict = defaultdict(lambda:multiply_SYMBOL_SYMBOL,
                              {NUMBER: multiply_SYMBOL_NUMBER,
                               ADD: multiply_SYMBOL_ADD,
                               MUL: multiply_SYMBOL_MUL,
                               })
