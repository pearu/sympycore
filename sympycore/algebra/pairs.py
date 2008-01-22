#
# Author: Pearu Peterson
# Created: January 2007

import types
from collections import defaultdict

from ..core import classes
from .algebraic_structures import CommutativeRing
from .primitive import PrimitiveAlgebra, ADD, MUL, SYMBOL, NUMBER, APPLY, POW, head_to_string
from .numberlib import mpq
from .utils import generate_swapped_first_arguments
from .utils import RedirectOperation
from .utils import not_implemented

def newinstance(cls, head, data, new = object.__new__):
    o = new(cls)
    o.head = head
    o.data = data
    return o

def inspect(obj):
    obj.inspect()

class CommutativeRingWithPairs(CommutativeRing):
    """ Implementation of a commutative ring where sums and products
    are represented as dictionaries of pairs.
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
        if self.head is NUMBER and isinstance(other, (int, long)):
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

    def __nonzero__(self):
        return self.head is not NUMBER or self.data!=0

    def copy(self):
        if self.head in [ADD, MUL]:
            return newinstance(self.__class__, self.head, dict(self.data))
        return self

    #def __repr__(self):
    #    return '%s(%r, head=%s)' % (self.__class__.__name__, self.data, head_to_string[self.head])

    def as_tree(self, tab='', level=0):
        if level:
            r = []
        else:
            r = [self.__class__.__name__+':']
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
            return (self.data,)
        raise NotImplementedError(`self, head`)

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
            return r
        if func==self.Mul:
            if args[0].head is NUMBER and args[0].data < 0:
                if args[0].data==-1:
                    args = map(PrimitiveAlgebra,args[1:])
                    if len(args)==1:
                        return -args[0]
                else:
                    args = [PrimitiveAlgebra(-args[0])] + map(PrimitiveAlgebra,args[1:])
                r = -PrimitiveAlgebra((MUL,tuple(args)))
            else:
                args = map(PrimitiveAlgebra, args)
                r = PrimitiveAlgebra((MUL,tuple(args)))
            r.commutative_mul = True
            return r
        if func==self.Pow:
            r = PrimitiveAlgebra((POW, tuple(map(PrimitiveAlgebra, args))))
            return r
        if head is NUMBER:
            value = self.data
            if hasattr(value, 'as_primitive'):
                return value.as_primitive()
            if value<0:
                r = -PrimitiveAlgebra((NUMBER, -value))
            else:
                r = PrimitiveAlgebra((NUMBER, value))
            return r
        elif head is SYMBOL:
            data = self.data
            if hasattr(data, 'as_primitive'):
                return data.as_primitive()
            return PrimitiveAlgebra((SYMBOL, self.data))
        elif callable(head):
            return PrimitiveAlgebra((APPLY, (self.head, self.data)))
        else:
            data = self.data
            if hasattr(data, 'as_primitive'):
                return data.as_primitive()
            return PrimitiveAlgebra((SYMBOL, (self.head,self.data)))


    def expand(self):
        return expand_dict1[self.head](self, self.__class__)

    def _matches_needs_revision(pattern, expr, repl_dict={}, wild_expressions=[], wild_predicates=[]):
        r = CommutativeRing.matches(pattern, expr, repl_dict, wild_expressions, wild_predicates)
        head = pattern.head
        if r is not None or head is NUMBER:
            return r
        if head is SYMBOL:
            if expr.head is SYMBOL:
                #XXX: return pattern.data.matches(expr.data, repl_dict, ...)
                return
            return
        if not wild_expression:
            return
        wild_part = []
        exact_part = []
        for t,c in pattern.data.iteritems():
            if t.has(*wild_exprssions):
                wild_part.append((t,c))
            else:
                exact_part.append((t,-c))

        def newobj(data):
            r = newinstance(pattern.__class__, pattern.head, data)
            if len(data)<=1:
                return r.canonize()
            return r

        if exact_part:
            if head is ADD:
                new_expr = expr + newobj(dict(exact_part))
            elif head is MUL:
                new_expr = expr * newobj(dict(exact_part))
            else:
                raise TypeError(`pattern, head`)
            new_pattern = newobj(dict(wild_part))
            return new_pattern.matches(expr, repl_dict, wild_expressions, wild_predicate)

        args = repl_dict, wild_expressions, wild_predicates
        if head is ADD:
            expr_args = list(expr.as_Terms_args)
            op = lambda x,y: x*y
        else:
            assert head is MUL,`expr`
            expr_args = list(expr.as_Factors_args)
            op = lambda x,y: x**y
            
        for i in xrange(len(wild_part)):
            wild, wcoeff = wild_part[i]
            rest = newobj(dict(wild_part[:i] + wild_part[i+1:]))

            # sort expression arguments by matching coefficient/exponent
            items1, items2 = [], []
            for item in expr_args:
                if item[1]==wcoeff:
                    items1.append(item)
                else:
                    items2.append(item)
            items = items1 + items2

            # matches nontrivial wild:
            for j in xrange(len(items)):
                t, c = items[j]
                cc = c/wcoeff # XXX: check for fractional powers if head is MUL
                r = wild.matches(op(t,cc), *args)
                if r is None:
                    continue
                new_pattern = rest.subs(r.items())
                new_expr = newobj(dict(items[:j]+items[j+1:]))
                r = new_pattern.matches(new_expr, *args)
                if r is not None:
                    return r

            # matches trivial wild:
            r = wild.matches(pattern.zero, *args)
            if r is not None:
                r = rest.subs(r.items()).matches(expr, *args)
                if r is not None:
                    return r
        return

    @classmethod
    def Symbol(cls, obj):
        return newinstance(cls, SYMBOL, obj)

    @classmethod
    def Number(cls, obj):
        return newinstance(cls, NUMBER, obj)

    @classmethod
    def Add(cls, *seq):
        d = {}
        result = newinstance(cls, ADD, d)
        for t in seq:
            inplace_ADD_dict[t.head](result, t, 1, cls)
        if len(d)<=1:
            return result.canonize()
        return result

    @classmethod
    def Mul(cls, *seq):
        d = {}
        result = newinstance(cls, MUL, d)
        number = 1
        for t in seq:
            head = t.head
            n = inplace_MUL_dict[head](result, t, 1, cls)
            if n is not None:
                number = number * n
        if len(d)<=1:
            result = result.canonize()
        return multiply_dict2[result.head][NUMBER](result, newinstance(cls, NUMBER, number), cls)

    @classmethod
    def Pow(cls, base, exponent):
        if isinstance(exponent, (int,long)):
            return pow_dict1[base.head](base, exponent, cls)
        return pow_dict2[base.head][exponent.head](base, exponent, cls)

    @classmethod
    def Terms(cls, *seq):
        d = {}
        result = newinstance(cls, ADD, d)
        for t,c in seq:
            inplace_ADD_dict[t.head](result, t, c, cls)
        if len(d)<=1:
            return result.canonize()
        return result

    @classmethod
    def Factors(cls, *seq):
        d = {}
        result = newinstance(cls, MUL, d)
        number = 1
        for t,c in seq:
            head = t.head
            n = inplace_MUL_dict[head](result, t, c, cls)
            if n is not None:
                number = number * n
        if len(d)<=1:
            return result.canonize() * number
        return result * number

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

    def __add__(self, other, redirect_operation='__add__'):
        other = self.convert(other, False)
        if other is NotImplemented:
            return NotImplemented
        try:
            return add_dict2[self.head][other.head](self, other, self.__class__)
        except RedirectOperation:
            return self.redirect_operation(self, other, redirect_operation=redirect_operation)

    def __radd__(self, other, redirect_operation='__radd__'):
        other = self.convert(other, False)
        if other is NotImplemented:
            return NotImplemented
        try:
            return add_dict2[other.head][self.head](other, self, other.__class__)
        except RedirectOperation:
            return self.redirect_operation(self, other, redirect_operation=redirect_operation)
        
    def __mul__(self, other, redirect_operation='__mul__'):
        other = self.convert(other, False)
        if other is NotImplemented:
            return NotImplemented
        try:
            return multiply_dict2[self.head][other.head](self, other, self.__class__)
        except RedirectOperation:
            return self.redirect_operation(self, other, redirect_operation=redirect_operation)

    def __rmul__(self, other, redirect_operation='__rmul__'):
        other = self.convert(other, False)
        if other is NotImplemented:
            return NotImplemented
        try:
            return multiply_dict2[other.head][self.head](other, self, other.__class__)
        except RedirectOperation:
            return self.redirect_operation(self, other, redirect_operation=redirect_operation)

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

    def diff(self, x):
        head = self.head
        if head is SYMBOL:
            if self.data == x.data:
                return self.one
            return self.zero
        if head is NUMBER:
            return self.zero
        if head is ADD:
            return A.Terms(*((s.diff(x), c) for s, c in self.data.items()))
        if head is MUL:
            pairs = self.data.items()
            L = len(pairs)
            if L == 1:
                b, e = pairs.pop()
                if isinstance(e, (int, long)) or e.head is NUMBER:
                    return e*b**(e-1) * b.diff(x)
        raise NotImplementedError

    def integrate(self, x, integrator=not_implemented):
        """
        Attempt to calculate an antiderivative of self with respect to x.
        This method is able to directly deal with expanded linear
        combinations of constant powers of x (e.g. expanded polynomials).

        Terms that cannot be handled directly are forwarded to
        a user-defined function `integrator`.

        TODO: identify nonconstant terms correctly
        """
        if self.head is SYMBOL:
            if self == x:
                return x**2 / 2
            return self*x
        if self.head is NUMBER:
            return self*x
        if self.head is MUL:
            product = self.one
            have_x = False
            for b, e in self.data.items():
                if b == x:
                    if have_x:
                        return integrator(self, x)
                    product *= b**(e+1) / (e+1)
                    have_x = True
                else:
                    product *= b
            return product
        if self.head is ADD:
            return self.Add(*(coef*term.integrate(x, integrator) \
                for term, coef in self.data.items()))
        return integrator(self, x)

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
    d = {}
    r = newinstance(cls, MUL, d)
    for t,c in lhs.pairs.iteritems():
        d[t] = c * rhs
    return r

def pow_NUMBER_NUMBER(lhs, rhs, cls):
    if isinstance(rhs.data, (int, long)):
        return pow_NUMBER_int(lhs, rhs.data, cls)
    return newinstance(cls, MUL, {lhs:rhs})

def pow_NUMBER_ADD(lhs, rhs, cls):
    pairs = rhs.data
    if len(pairs)==1:
        t,c = pairs.items()[0]
        if isinstance(c, (int, long)):
            lhs = pow_NUMBER_int(lhs, c, cls)
            rhs = t
    return newinstance(cls, MUL, {lhs:rhs})

def pow_NUMBER_MUL(lhs, rhs, cls):
    return newinstance(cls, MUL, {lhs:rhs})

def pow_NUMBER_SYMBOL(lhs, rhs, cls):
    return newinstance(cls, MUL, {lhs:rhs})

def pow_ADD_NUMBER(lhs, rhs, cls):
    if isinstance(rhs.data, (int, long)):
        return pow_ADD_int(lhs, rhs.data, cls)
    return newinstance(cls, MUL, {lhs:rhs})

def pow_ADD_ADD(lhs, rhs, cls):
    pairs = rhs.data
    if len(pairs)==1:
        t,c = pairs.items()[0]
        if isinstance(c, (int, long)):
            lhs = pow_dict2[lhs.head][t.head](lhs, t, cls)
            rhs = cls.convert(c)
    return newinstance(cls, MUL, {lhs:rhs})

def pow_ADD_MUL(lhs, rhs, cls):
    return newinstance(cls, MUL, {lhs:rhs})

def pow_ADD_SYMBOL(lhs, rhs, cls):
    return newinstance(cls, MUL, {lhs:rhs})

def pow_MUL_NUMBER(lhs, rhs, cls):
    if isinstance(rhs.data, (int, long)):
        return pow_MUL_int(lhs, rhs.data, cls)
    return newinstance(cls, MUL, {lhs:rhs})

def pow_MUL_ADD(lhs, rhs, cls):
    pairs = rhs.data
    if len(pairs)==1:
        t,c = pairs.items()[0]
        if isinstance(c, (int, long)):
            lhs = pow_dict2[lhs.head][t.head](lhs, t, cls)
            rhs = cls.convert(c)
    return newinstance(cls, MUL, {lhs:rhs})

def pow_MUL_MUL(lhs, rhs, cls):
    return newinstance(cls, MUL, {lhs:rhs})

def pow_MUL_SYMBOL(lhs, rhs, cls):
    return newinstance(cls, MUL, {lhs:rhs})

def pow_SYMBOL_NUMBER(lhs, rhs, cls):
    if isinstance(rhs.data, (int, long)):
        return pow_SYMBOL_int(lhs, rhs.data, cls)
    return newinstance(cls, MUL, {lhs:rhs})

def pow_SYMBOL_ADD(lhs, rhs, cls):
    pairs = rhs.data
    if len(pairs)==1:
        t,c = pairs.items()[0]
        if isinstance(c, (int, long)):
            lhs = pow_dict2[lhs.head][t.head](lhs, t, cls)
            rhs = cls.convert(c)
    return newinstance(cls, MUL, {lhs:rhs})

def pow_SYMBOL_MUL(lhs, rhs, cls):
    return newinstance(cls, MUL, {lhs:rhs})

def pow_SYMBOL_SYMBOL(lhs, rhs, cls):
    return newinstance(cls, MUL, {lhs:rhs})

def iadd_ADD_NUMBER(lhs, rhs, one_c, cls):
    value = rhs.data * one_c
    if not value:
        return
    pairs = lhs.data
    one = cls.one
    b = pairs.get(one)
    if b is None:
        pairs[one] = value
    else:
        c = b + value
        if c:
            pairs[one] = c
        else:
            del pairs[one]
    return

def iadd_ADD_SYMBOL(lhs, rhs, one_c, cls):
    pairs = lhs.data
    b = pairs.get(rhs)
    if b is None:
        pairs[rhs] = one_c
    else:
        c = b + one_c
        if c:
            pairs[rhs] = c
        else:
            del pairs[rhs]
    return

def iadd_ADD_ADD(lhs, rhs, one_c, cls):
    pairs = lhs.data
    get = pairs.get
    for t,c in rhs.data.iteritems():
        b = get(t)
        if b is None:
            pairs[t] = c * one_c
        else:
            c = b + c * one_c
            if c:
                pairs[t] = c
            else:
                del pairs[t]
    return

def iadd_ADD_MUL(lhs, rhs, one_c, cls):
    pairs = lhs.data
    b = pairs.get(rhs)
    if b is None:
        pairs[rhs] = one_c
    else:
        c = b + one_c
        if c:
            pairs[rhs] = c
        else:
            del pairs[rhs]
    return

def imul_MUL_NUMBER(lhs, rhs, one_e, cls):
    return rhs.data ** one_e

def imul_MUL_SYMBOL(lhs, rhs, one_e, cls):
    pairs = lhs.data
    b = pairs.get(rhs)
    if b is None:
        pairs[rhs] = one_e
    else:
        c = b + one_e
        if c:
            pairs[rhs] = c
        else:
            del pairs[rhs]
    return

def imul_MUL_ADD(lhs, rhs, one_e, cls):
    pairs = lhs.data
    d = rhs.data
    if len(d)==1:
        t,c = d.items()[0]
        inplace_MUL_dict[t.head](lhs, t, one_e, cls)
        return c ** one_e
    b = pairs.get(rhs)
    if b is None:
        pairs[rhs] = one_e
    else:
        c = b + one_e
        if c:
            pairs[rhs] = c
        else:
            del pairs[rhs]
    return

def imul_MUL_MUL(lhs, rhs, one_e, cls):
    pairs = lhs.data
    get = pairs.get
    for t,c in rhs.data.iteritems():
        b = get(t)
        if b is None:
            pairs[t] = c * one_e
        else:
            c = b + c * one_e
            if c:
                pairs[t] = c
            else:
                del pairs[t]
    return

def expand_ADD(obj, cls):
    d = {}
    result = newinstance(obj.__class__, ADD, d)
    for t,c in obj.data.iteritems():
        t = t.expand()
        inplace_ADD_dict[t.head](result, t, c, cls)
    if len(d)<=1:
        return result.canonize()
    return result

def expand_MUL(obj, cls):
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
        elif head is MUL:
            t._multiply_values(c, 1, 0)
            return t
        elif head is ADD:
            return expand_ADD_INTPOW(t, c, cls)
        return newinstance(cls, MUL, {t:c})
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
    return expand_dict2[lhs.head][rhs.head](lhs, rhs, cls)


####################################################################
# Implementation of binary operations +, *, and expanding products.

def add_NUMBER_NUMBER(lhs, rhs, cls):
    return newinstance(cls, NUMBER, lhs.data + rhs.data)

def add_NUMBER_SYMBOL(lhs, rhs, cls):
    if lhs.data:
        return newinstance(cls, ADD, {lhs.one: lhs.data, rhs: 1})
    return rhs

generate_swapped_first_arguments(add_NUMBER_SYMBOL)

def add_NUMBER_ADD(lhs, rhs, cls):
    value = lhs.data
    if not value:
        return rhs
    result = rhs.copy()
    pairs = result.data
    one = cls.one
    b = pairs.get(one)
    if b is None:
        pairs[one] = value
    else:
        c = b + value
        if c:
            pairs[one] = c
        else:
            del pairs[one]
    if len(pairs)<=1:
        return result.canonize()
    return result

generate_swapped_first_arguments(add_NUMBER_ADD)

def add_NUMBER_MUL(lhs, rhs, cls):
    value = lhs.data
    if value:
        return newinstance(cls,ADD, {cls.one: value, rhs: 1})
    return rhs

generate_swapped_first_arguments(add_NUMBER_MUL)

def add_SYMBOL_SYMBOL(lhs, rhs, cls):
    if lhs.data==rhs.data:
        return newinstance(cls,ADD,{lhs: 2})
    return newinstance(cls,ADD,{lhs: 1, rhs: 1})

def add_SYMBOL_ADD(lhs, rhs, cls):
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

generate_swapped_first_arguments(add_SYMBOL_ADD)

def add_SYMBOL_MUL(lhs, rhs, cls):
    return newinstance(cls,ADD,{lhs: 1, rhs: 1})

generate_swapped_first_arguments(add_SYMBOL_MUL)

def add_ADD_ADD(lhs, rhs, cls):
    if lhs.length() < rhs.length():
        rhs, lhs = lhs, rhs
    result = lhs.copy()
    pairs = result.data
    get = pairs.get
    for t,c in rhs.data.iteritems():
        b = get(t)
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
    pairs = result.data
    b = pairs.get(rhs)
    if b is None:
        pairs[rhs] = 1
    else:
        c = b + 1
        if c:
            pairs[rhs] = c
        else:
            del pairs[rhs]
    if len(pairs)<=1:
        return result.canonize()
    return result

generate_swapped_first_arguments(add_ADD_MUL)

def add_MUL_MUL(lhs, rhs, cls):
    if lhs.data==rhs.data:
        return newinstance(cls,ADD,{lhs: 2})
    return newinstance(cls,ADD,{lhs: 1, rhs: 1})

def multiply_NUMBER_NUMBER(lhs, rhs, cls):
    return newinstance(cls, NUMBER, lhs.data * rhs.data)

def multiply_NUMBER_SYMBOL(lhs, rhs, cls):
    value = lhs.data
    if value:
        if value==1:
            return rhs
        return newinstance(cls, ADD, {rhs:value})
    return lhs

generate_swapped_first_arguments(multiply_NUMBER_SYMBOL)

def multiply_NUMBER_ADD(lhs, rhs, cls):
    value = lhs.data
    if value:
        if value==1:
            return rhs
        d = {}
        result = newinstance(cls, ADD, d)
        for t,c in rhs.data.iteritems():
            d[t] = c * value
        if len(d)<=1:
            return result.canonize()
        return result
    return lhs

generate_swapped_first_arguments(multiply_NUMBER_ADD)

def multiply_NUMBER_MUL(lhs, rhs, cls):
    value = lhs.data
    if value:
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
    return lhs

generate_swapped_first_arguments(multiply_NUMBER_MUL)

def multiply_SYMBOL_SYMBOL(lhs, rhs, cls):
    if lhs.data==rhs.data:
        return newinstance(cls, MUL, {lhs:2})
    return newinstance(cls, MUL, {lhs:1, rhs:1})

def multiply_SYMBOL_ADD(lhs, rhs, cls):
    if rhs.length()>1:
        return newinstance(cls, MUL, {lhs:1, rhs: 1})
    t, c = rhs.data.items()[0]
    if lhs==t:
        return newinstance(cls,ADD,{newinstance(cls, MUL, {lhs: 2}): c})
    if t.head is MUL:
        t = t * lhs
        if t.head is NUMBER:
            return t * c
        return newinstance(cls, ADD, {t: c})
    return newinstance(cls,ADD,{newinstance(cls, MUL, {lhs: 1, t:1}): c})

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
    if lhs.length()==rhs.length()==1:
        t1, c1 = lhs.data.items()[0]
        t2, c2 = rhs.data.items()[0]
        t = multiply_dict2[t1.head][t2.head](t1, t2, cls)
        if t==lhs.one:
            return newinstance(cls, NUMBER, c1*c2)
        return newinstance(cls,ADD,{t: c1*c2})
    else:
        if lhs.data==rhs.data:
            return newinstance(cls, MUL, {lhs:2})
        return newinstance(cls, MUL, {lhs:1, rhs:1})

def multiply_ADD_MUL(lhs, rhs, cls):
    if lhs.length()>1:
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
    t, c = lhs.data.items()[0]
    return multiply_dict2[t.head][rhs.head](t, rhs, cls) * c

generate_swapped_first_arguments(multiply_ADD_MUL)

def multiply_MUL_MUL(lhs, rhs, cls):
    if lhs.length() < rhs.length():
        rhs, lhs = lhs, rhs
    result = newinstance(cls, MUL, dict(lhs.data))
    pairs = result.data
    get = pairs.get
    for t,c in rhs.data.iteritems():
        b = get(t)
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

def expand_NUMBER_ADD(lhs, rhs, cls):
    value = lhs.data
    if value:
        if value==1:
            return rhs
        d = {}
        result = newinstance(cls, ADD, d)
        for t,c in lhs.data.iteritems():
            d[t] = c * value
        if len(d)<=1:
            return result.canonize()
        return result
    return lhs

generate_swapped_first_arguments(expand_NUMBER_ADD)

def expand_SYMBOL_ADD(lhs, rhs, cls):
    d = {}
    result = newinstance(cls, ADD, d)
    for t,c in rhs.data.iteritems():
        d[t * lhs] = c
    return result

generate_swapped_first_arguments(expand_SYMBOL_ADD)

def expand_ADD_ADD(lhs, rhs, cls):
    if lhs.length() > rhs.length():
        lhs, rhs = rhs, lhs
    d = {}
    result = newinstance(cls, ADD, d)
    pairs1 = lhs.data
    pairs2 = rhs.data
    get = d.get
    for t1, c1 in pairs1.iteritems():
        t1_head = t1.head
        for t2, c2 in pairs2.iteritems():
            t = multiply_dict2[t1_head][t2.head](t1, t2, cls)
            c = c1 * c2
            b = get(t)
            if b is None:
                d[t] = c
            else:
                c = b + c
                if c:
                    d[t] = c
                else:
                    del d[t]
    if len(d)<=1:
        return result.canonize()
    return result

def expand_ADD_MUL(lhs, rhs, cls):
    d = {}
    result = newinstance(cls, ADD, d)
    for t,c in lhs.data.iteritems():
        d[t * rhs] = c
    return result

generate_swapped_first_arguments(expand_ADD_MUL)

def expand_ADD_INTPOW(lhs, m, cls):
    terms = lhs.data.items()
    data = generate_expand_data(len(terms), int(m))
    d = {}
    result = newinstance(cls, ADD, d)
    get = d.get
    for exps, c in data.iteritems():
        t, n = exps.apply_to_terms(terms)
        t = newinstance(cls, MUL, dict(t)).canonize()
        b = get(t)
        if b is None:
            d[t] = n * c
        else:
            c = b + n * c
            if c:
                d[t] = c
            else:
                del d[t]
    return result

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

inplace_ADD_dict = defaultdict(lambda: iadd_ADD_SYMBOL,
                               {NUMBER: iadd_ADD_NUMBER,
                                ADD: iadd_ADD_ADD,
                                MUL: iadd_ADD_MUL,
                                })

inplace_MUL_dict = defaultdict(lambda: imul_MUL_SYMBOL,
                               {NUMBER: imul_MUL_NUMBER,
                                ADD: imul_MUL_ADD,
                                MUL: imul_MUL_MUL,
                                })

expand_NUMBER_dict = defaultdict(lambda:multiply_NUMBER_SYMBOL,
                                 {NUMBER: multiply_NUMBER_NUMBER,
                                  ADD: expand_NUMBER_ADD,
                                  MUL: multiply_NUMBER_MUL,
                                  })

expand_ADD_dict = defaultdict(lambda:expand_ADD_SYMBOL,
                              {NUMBER: expand_ADD_NUMBER,
                               ADD: expand_ADD_ADD,
                               MUL: expand_ADD_MUL,
                               })

expand_MUL_dict = defaultdict(lambda:multiply_MUL_SYMBOL,
                              {NUMBER: multiply_MUL_NUMBER,
                               ADD: expand_MUL_ADD,
                               MUL: multiply_MUL_MUL,
                               })

expand_SYMBOL_dict = defaultdict(lambda:multiply_SYMBOL_SYMBOL,
                                 {NUMBER: multiply_SYMBOL_NUMBER,
                                  ADD: expand_SYMBOL_ADD,
                                  MUL: multiply_SYMBOL_MUL,
                                  })

expand_dict2 = defaultdict(lambda:expand_SYMBOL_dict,
                           {NUMBER:expand_NUMBER_dict,
                            ADD:expand_ADD_dict,
                            MUL:expand_MUL_dict,
                            })

expand_dict1 = defaultdict(lambda: (lambda obj, cls: obj),
                           {NUMBER: lambda obj, cls: obj,
                            ADD: expand_ADD,
                            MUL: expand_MUL,
                            })

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

multiply_dict2 = defaultdict(lambda:mul_SYMBOL_dict,
                             {NUMBER:mul_NUMBER_dict,
                              ADD:mul_ADD_dict,
                              MUL:mul_MUL_dict,
                              })

add_NUMBER_dict = defaultdict(lambda:add_NUMBER_SYMBOL,
                              {NUMBER: add_NUMBER_NUMBER,
                               ADD: add_NUMBER_ADD,
                               MUL: add_NUMBER_MUL,
                               })

add_ADD_dict = defaultdict(lambda:add_ADD_SYMBOL,
                           {NUMBER: add_ADD_NUMBER,
                            ADD: add_ADD_ADD,
                            MUL: add_ADD_MUL,
                            })

add_MUL_dict = defaultdict(lambda:add_MUL_SYMBOL,
                           {NUMBER: add_MUL_NUMBER,
                            ADD: add_MUL_ADD,
                            MUL: add_MUL_MUL,
                            })

add_SYMBOL_dict = defaultdict(lambda:add_SYMBOL_SYMBOL,
                              {NUMBER: add_SYMBOL_NUMBER,
                               ADD: add_SYMBOL_ADD,
                               MUL: add_SYMBOL_MUL,
                               })

add_dict2 = defaultdict(lambda:add_SYMBOL_dict,
                        {NUMBER:add_NUMBER_dict,
                         ADD:add_ADD_dict,
                         MUL:add_MUL_dict,
                         })

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

    # Generate binomial coefficients
    if n == 2:
        d = {ExponentsTuple((0, m)):1}
        a = 1
        for k in xrange(1, m+1):
            a = (a * (m-k+1))//k
            d[ExponentsTuple((k, m-k))] = a
        return d

    # Generate multinomial coefficients

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
    r_get = r.get
    l = [r.items()]
    for k in xrange(1, m*(n-1)+1):
        d = {}
        d_get = d.get
        for i in xrange(1, min(n,k+1)):
            nn = (m+1)*i-k
            if nn:
                t = p0[i]
                for t2, c2 in l[k-i]:
                    tt = t2 * t
                    cc = mpq(nn * c2, k)
                    b = d_get(tt)
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
            b = r_get(t)
            if b is None:
                r[t] = c
            else:
                c = b + c
                if c:
                    r[t] = c
                else:
                    del r[t]
    return r
