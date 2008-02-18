#
# Author: Pearu Peterson
# Created: January 2008

import types
from collections import defaultdict

from ..core import classes
from ..utils import str_SUM, str_PRODUCT, str_POWER, str_APPLY, str_SYMBOL, str_NUMBER
from ..utils import ADD, MUL, SYMBOL, NUMBER, APPLY, POW, TUPLE, head_to_string, TERMS, FACTORS

from .utils import generate_swapped_first_arguments
from ..utils import RedirectOperation
from .algebra import BasicAlgebra
from .ring import CommutativeRing
from .primitive import PrimitiveAlgebra
from ..arithmetic.numbers import FractionTuple, ExtendedNumber
from ..arithmetic.number_theory import multinomial_coefficients

from .pairs_ops import (add_method, sub_method, rsub_method, neg_method,
                        mul_method, div_method, rdiv_method, pow_method)

def newinstance(cls, head, data, new = object.__new__):
    o = new(cls)
    o.head = head
    o.data = data
    return o

def inspect(obj):
    obj.inspect()

def partial_derivative(func, n):
    dname = '%s_%s' % (func.__name__, n)
    def dfunc(*args):
        raise NotImplementedError('%s%s' % (dname, str(args)))
    dfunc.__name__ = dname
    return dfunc

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

    _has_active = None
    def has_active(self):
        cls = type(self)
        r = self._has_active
        if r is not None:
            return r
        head = self.head
        if head is NUMBER:
            r = type(self.data) is ExtendedNumber
            self._has_active = r
            return r
        if head is TERMS or head is FACTORS:
            for t,c in self.data.iteritems():
                tc = type(c)
                if tc is ExtendedNumber:
                    self._has_active = True
                    return True
                if t.has_active():
                    self._has_active = True
                    return True
                if tc is cls and c.has_active():
                    self._has_active = True
                    return True
            self._has_active = False
            return False
        if head is SYMBOL:
            self._has_active = False
            return False
        if callable(head):
            for a in self.args:
                if a.has_active():
                    self._has_active = True
                    return True
        self._has_active = False
        return False
    
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
            return self.head is other.head and self.data == other.data
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
        return self.head is not NUMBER or not (self.data==0)

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
        cls = self.__class__
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

    def expand(self):
        return expand_dict1[self.head](self, self.__class__)

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
        if number is 1:
            return result
        number = newinstance(cls, NUMBER, number)
        return mul_NUMBER_dict[result.head](number, result, cls)

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
            result = result.canonize()
        if number is 1:
            return result
        else:
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
                cls = self.__class__
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
            cls = self.__class__
            symbols = self._symbols = set([newinstance(cls, SYMBOL, d) for d in self._get_symbols_data()])
        return symbols

    def has_symbol(self, symbol):
        return symbol.data in self._get_symbols_data()

    def has(self, subexpr):
        subexpr = self.convert(subexpr)
        if subexpr.head is SYMBOL:
            return subexpr.data in self._get_symbols_data()
        raise NotImplementedError('%s.has(%r)' % (self.__class__.__name__, subexpr))

    def _subs(self, subexpr, newexpr):
        head = self.head

        if head is subexpr.head:
            if self.data == subexpr.data:
                return newexpr

        if head is SYMBOL or head is NUMBER:
            return self
            
        cls = self.__class__

        if head is ADD:
            d = {}
            result = newinstance(cls, head, d)
            for t,c in self.data.iteritems():
                r = t._subs(subexpr, newexpr)
                inplace_ADD_dict[r.head](result, r, c, cls)
            if len(d)<=1:
                return result.canonize()
            return result

        elif head is MUL:
            d = {}
            result = newinstance(cls, head, d)
            num = 1
            for t,c in self.data.iteritems():
                r = t._subs(subexpr, newexpr)
                n = inplace_MUL_dict[r.head](result, r, c, cls)
                if n is not None:
                    num = num * n
            if len(d)<=1:
                result = result.canonize()
            if num is 1:
                return result
            return result * num

        elif callable(head):
            args = self.data
            if type(args) is tuple:
                args = [a._subs(subexpr, newexpr) for a in args]
                return head(*args)
            else:
                return head(args._subs(subexpr, newexpr))

        raise NotImplementedError(`self`)

    def _diff(self, x, zero, cls):
        head = self.head
        if head is NUMBER:
            return zero
        elif head is SYMBOL:
            if self.data == x:
                return cls.one
            return zero
        elif callable(head):
            return diff_callable_SYMBOL(self, x, zero, cls)
        if x not in self._get_symbols_data():
            return zero
        return diff_SYMBOL_dict[head](self, x, zero, cls)

    @staticmethod
    def _integrator(e, x):
        raise NotImplementedError("Don't know how to integrate(%s, %s)" % \
            (e, x))

    @staticmethod
    def _integrator_definite(e, x, a, b):
        raise NotImplementedError("Don't know how to integrate(%s, %s)" % \
            (e, (x, a, b)))

    def _integrate(self, x, integrator=None):
        """
        Attempt to calculate an antiderivative of self with respect to x.
        This method is able to directly deal with expanded linear
        combinations of constant powers of x (e.g. expanded polynomials).

        Terms that cannot be handled directly are forwarded to
        a user-defined function `integrator`.
        """
        if not self.has_symbol(x):
            return self*x
        if self == x:
            return x**2 / 2
        if integrator is None:
            integrator = self._integrator
        if self.head is MUL:
            product = self.one
            have_x = False
            for b, e in self.data.iteritems():
                # We don't know how to do exponentials yet
                if isinstance(e, self.__class__) and e.has_symbol(x):
                    return integrator(self, x)
                if b == x:
                    if have_x:
                        return integrator(self, x)
                    product *= b**(e+1) / (e+1)
                    have_x = True
                # Cases like (x+y)*x could still be handled by expanding,
                # but this may cause infinite recursion if implemented
                # directly here
                elif b.has_symbol(x):
                    return integrator(self, x)
                else:
                    product *= b**e
            return product
        if self.head is ADD:
            return self.Add(*(coef*term._integrate(x, integrator) \
                              for term, coef in self.data.iteritems()))
        return integrator(self, x)

    def _integrate_definite(self, x, a, b, integrator=None):
        head = self.head
        if head is NUMBER or x not in self._get_symbols_data():
            return self*(a-b)
        if head is SYMBOL and self.data == x:
            return (b**2-a**2) / 2
        if integrator is None:
            integrator = self._integrator_definite
        if head is MUL:
            product = self.one
            have_x = False
            for base, e in self.data.iteritems():
                # We don't know how to do exponentials yet
                if isinstance(e, self.__class__) and e.has_symbol(x):
                    return integrator(self, x, a, b)
                if base.head is SYMBOL and base.data == x:
                    if have_x:
                        return integrator(self, x, a, b)
                    e1 = e+1
                    product *= (b**e1-a**e1) / e1
                    have_x = True
                # Cases like (x+y)*x could still be handled by expanding,
                # but this may cause infinite recursion if implemented
                # directly here
                elif x in base._get_symbols_data():
                    return integrator(self, x, a, b)
                else:
                    product *= newinstance(self.__class__, MUL, {base:e})
            return product
        if head is ADD:
            return self.Add(*(coef*term._integrate_definite(x, a, b, integrator) \
                              for term, coef in self.data.iteritems()))
        return integrator(self, x, a, b)


def diff_callable_SYMBOL(expr, x, zero, cls):
    head = expr.head
    data = expr.data
    if hasattr(head, 'derivative'):
        derivative = head.derivative
        if type(derivative) is tuple:
            terms = []
            for df, arg in zip(derivative, data):
                da = arg._diff(x, zero, cls)
                if da is zero:
                    continue
                terms.append(df(*data) * da)
            return cls.Add(*terms)
        darg = data._diff(x, zero, cls)
        if darg is zero:
            return zero
        return derivative(data) * darg
    if type(data) is tuple:
        terms = []
        for i,arg in enumerate(data):
            da = arg._diff(x, zero, cls)
            if da is zero:
                continue
            df = newinstance(cls, partial_derivative(head, i+1), data)
            terms.append(df * da)
        return cls.Add(*terms)
    da = data._diff(x, zero, cls)
    if da is zero:
        return da
    df = newinstance(cls, partial_derivative(head, 1), data)
    return df * da    

def diff_NUMBER_SYMBOL(expr, x, zero, cls):
    return zero

def diff_SYMBOL_SYMBOL(expr, x, zero, cls):
    if expr.data == x:
        return cls.one
    return zero

def diff_ADD_SYMBOL(expr, x, zero, cls):
    pairs = expr.data
    if len(pairs)==1:
        t, c = pairs.items()[0]
        dt = t._diff(x, zero, cls)
        if c is 1:
            return dt
        return dt * c
    d = {}
    result = newinstance(cls, ADD, d)
    for t, c in pairs.iteritems():
        dt = t._diff(x, zero, cls)
        if dt is zero:
            continue
        inplace_ADD_dict[dt.head](result, dt, c, cls)
    if len(d)<=1:
        return result.canonize()
    return result

def diff_FACTOR_SYMBOL(expr, base, exp, x, zero, log, cls):
    db = base._diff(x, zero, cls)
    if isinstance(exp, inttypes):
        if exp is 1:
            return db
        if exp is 2:
            return base * db * exp
        expr2 = newinstance(cls, MUL, {base:exp-1})
        return expr2 * db * exp

    de = exp._diff(x, zero, cls)
    if de is zero:
        expr2 = newinstance(cls, MUL, {base:exp-1})
        return expr2 * db * exp
    if expr is None:
        expr = newinstance(cls, MUL, {base:exp})
    if db is zero:
        return expr * de * log(base)
    return expr * (de * log(base) + exp * newinstance(cls, MUL, {base:-1}) * db)

def diff_MUL_SYMBOL(expr, x, zero, cls):
    pairs = expr.data
    n = len(pairs)
    args = pairs.items()
    log = cls.Log
    if n==1:
        b, e = args[0]
        return diff_FACTOR_SYMBOL(None, b, e, x, zero, log, cls)
    if n==2:
        b1, e1 = args[0]
        b2, e2 = args[1]
        if e1 is 1:
            t1 = b1
        else:
            t1 = b1 ** e1
        if e2 is 1:
            t2 = b2
        else:
            t2 = b2 ** e2
        dt1 = diff_FACTOR_SYMBOL(t1, b1, e1, x, zero, log, cls)
        dt2 = diff_FACTOR_SYMBOL(t2, b2, e2, x, zero, log, cls)
        return t1 * dt2 + t2 * dt1
    d = {}
    result = newinstance(cls, ADD, d)
    for i in xrange(n):
        b, e = args[i]
        dt = diff_FACTOR_SYMBOL(None, b, e, x, zero, log, cls)
        if dt is zero:
            continue
        d1 = dict(args[:i]+args[i+1:])
        t = newinstance(cls, MUL, d1)
        n = inplace_MUL_dict[dt.head](t, dt, 1, cls)
        if len(d1)<=1:
            t = t.canonize()
        if n is None:
            n = 1
        inplace_ADD_dict[t.head](result, t, n, cls)
    if len(d)<=1:
        return result.canonize()
    return result

diff_SYMBOL_dict = {
    NUMBER: diff_NUMBER_SYMBOL,
    SYMBOL: diff_SYMBOL_SYMBOL,
    ADD: diff_ADD_SYMBOL,
    MUL: diff_MUL_SYMBOL,
    }

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
    try:
        bool(lhs.data)
    except RedirectOperation:
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
    try:
        bool(value)
    except RedirectOperation:
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

def iadd_ADD_NUMBER(lhs, rhs, one_c, cls):
    value = rhs.data * one_c
    try:
        if not value:
            return
    except RedirectOperation:
        pass
    pairs = lhs.data
    one = cls.one
    b = pairs.get(one)
    if b is None:
        pairs[one] = value
    else:
        c = b + value
        try:
            if c:
                pairs[one] = c
            else:
                del pairs[one]
        except RedirectOperation:
            pairs[one] = c
    return

def iadd_ADD_SYMBOL(lhs, rhs, one_c, cls):
    pairs = lhs.data
    b = pairs.get(rhs)
    if b is None:
        pairs[rhs] = one_c
    else:
        c = b + one_c
        try:
            if c:
                pairs[rhs] = c
            else:
                del pairs[rhs]
        except RedirectOperation:
            pairs[rhs] = c
    return

def iadd_ADD_ADD(lhs, rhs, one_c, cls):
    pairs = lhs.data
    get = pairs.get
    for t,c in rhs.data.iteritems():
        c = c * one_c
        b = get(t)
        if b is not None:
            c = b + c
        try:
            if c:
                pairs[t] = c
            elif b is not None:
                del pairs[t]
        except RedirectOperation:
            pairs[t] = c
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
    value = lhs.data
    try:
        if not value:
            return rhs
    except RedirectOperation:
        r = value.__add__(rhs)
        if r is not NotImplemented:
            return cls.convert(r)
    return newinstance(cls, ADD, {lhs.one: lhs.data, rhs: 1})

generate_swapped_first_arguments(add_NUMBER_SYMBOL)

def add_NUMBER_ADD(lhs, rhs, cls):
    value = lhs.data
    try:
        if not value:
            return rhs
    except RedirectOperation:
        r = value.__add__(rhs)
        if r is not NotImplemented:
            return cls.convert(r)
    result = rhs.copy()
    pairs = result.data
    one = cls.one
    b = pairs.get(one)
    if b is None:
        pairs[one] = value
    else:
        c = b + value
        try:
            if c:
                pairs[one] = c
            else:
                del pairs[one]
        except RedirectOperation:
            pairs[one] = c

    if len(pairs)<=1:
        return result.canonize()
    return result

generate_swapped_first_arguments(add_NUMBER_ADD)

def add_NUMBER_MUL(lhs, rhs, cls):
    value = lhs.data
    try:
        if not value:
            return rhs
    except RedirectOperation:
        r = value.__add__(rhs)
        if r is not NotImplemented:
            return cls.convert(r)
    return newinstance(cls,ADD, {cls.one: value, rhs: 1})

generate_swapped_first_arguments(add_NUMBER_MUL)

def add_SYMBOL_SYMBOL(lhs, rhs, cls):
    if lhs == rhs:
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
        try:
            if c:
                pairs[lhs] = c
            else:
                del pairs[lhs]
        except RedirectOperation:
            pairs[lhs] = c
    if len(pairs)<=1:
        return result.canonize()
    return result

generate_swapped_first_arguments(add_SYMBOL_ADD)

def add_SYMBOL_MUL(lhs, rhs, cls):
    return newinstance(cls,ADD,{lhs: 1, rhs: 1})

generate_swapped_first_arguments(add_SYMBOL_MUL)

def add_ADD_ADD(lhs, rhs, cls):
    if len(lhs.data) < len(rhs.data):
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
            try:
                if c:
                    pairs[t] = c
                else:
                    del pairs[t]
            except RedirectOperation:
                pairs[t] = c
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
    try:
        if not value:
            return lhs
    except RedirectOperation:
        r = value.__mul__(rhs)
        if r is not NotImplemented:
            return cls.convert(r)
    if value==1:
        return rhs
    return newinstance(cls, ADD, {rhs:value})

generate_swapped_first_arguments(multiply_NUMBER_SYMBOL)

def multiply_NUMBER_ADD(lhs, rhs, cls):
    value = lhs.data
    try:
        bool(value)
    except RedirectOperation:
        r = value.__mul__(rhs)
        if r is not NotImplemented:
            return cls.convert(r)
        return newinstance(cls, ADD, {rhs:value})
    if value==1:
        return rhs
    d = {}
    result = newinstance(cls, ADD, d)
    for t,c in rhs.data.iteritems():
        c = c * value
        try:
            if c:
                d[t] = c
        except RedirectOperation:
            d[t] = c
    if len(d)<=1:
        return result.canonize()
    return result

generate_swapped_first_arguments(multiply_NUMBER_ADD)

def multiply_NUMBER_MUL(lhs, rhs, cls):
    value = lhs.data
    try:
        if not value:
            return lhs
    except RedirectOperation:
        r = value.__mul__(rhs)
        if r is not NotImplemented:
            return cls.convert(r)
        return newinstance(cls, ADD, {rhs:value})
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

def expand_NUMBER_ADD(lhs, rhs, cls):
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

generate_swapped_first_arguments(expand_NUMBER_ADD)

def expand_SYMBOL_ADD(lhs, rhs, cls):
    d = {}
    result = newinstance(cls, ADD, d)
    for t,c in rhs.data.iteritems():
        d[t * lhs] = c
    return result

generate_swapped_first_arguments(expand_SYMBOL_ADD)

def expand_ADD_ADD(lhs, rhs, cls):
    pairs1 = lhs.data
    pairs2 = rhs.data
    if len(pairs1) < len(pairs2):
        lhs, rhs = rhs, lhs
        pairs1, pairs2 = pairs2, pairs1
    d = {}
    result = newinstance(cls, ADD, d)
    get = d.get
    for t1, c1 in pairs1.iteritems():
        mdict = multiply_dict2[t1.head]
        for t2, c2 in pairs2.iteritems():
            t = mdict[t2.head](t1, t2, cls)
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
    pairs = lhs.data
    if len(pairs)==1:
        t,c = pairs.items()[0]
        return expand_dict2[t.head][rhs.head](t, rhs, cls) * cls.convert(c)
    d = {}
    result = newinstance(cls, ADD, d)
    for t,c in pairs.iteritems():
        d[t * rhs] = c
    if len(d)<=1:
        return result.canonize()
    return result

generate_swapped_first_arguments(expand_ADD_MUL)

def expand_ADD_INTPOW(lhs, m, cls):
    terms = lhs.data.items()
    data = multinomial_coefficients(len(terms), int(m))
    d = {}
    result = newinstance(cls, ADD, d)
    get = d.get
    Factors = cls.Factors
    one = cls.one
    for exps, c in data.iteritems():
        t = []
        n = 1
        for i,e in enumerate(exps):
            if e==0: continue
            t1, c1 = terms[i]
            t.append((t1, e))
            if c1!=1:
                n = n * c1**e
        t = Factors(*t)
        if t.head is NUMBER:
            n = t * n
            t = one
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

