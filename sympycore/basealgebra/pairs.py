#
# Author: Pearu Peterson
# Created: January 2008
#
"""Provides CommutativeRingWithPairs class.
"""
__docformat__ = "restructuredtext"

__all__ = ['CommutativeRingWithPairs']

from ..apair import APair
from ..core import classes
from ..utils import str_SUM, str_PRODUCT, str_POWER, str_APPLY, str_SYMBOL, str_NUMBER
from ..utils import TERMS, FACTORS, SYMBOL, NUMBER, APPLY, POW, TUPLE, head_to_string

from .algebra import BasicAlgebra
from .ring import CommutativeRing
from .primitive import PrimitiveAlgebra
from ..arithmetic.numbers import FractionTuple, realtypes

from .pairs_ops import (add_method, sub_method, rsub_method, neg_method,
                        mul_method, div_method, rdiv_method, pow_method)

from .pairs_iops import (inplace_add, inplace_add2, inplace_sub,
                         return_terms, return_factors,
                         inplace_mul, inplace_mul2)

from .pairs_expand import expand

class CommutativeRingWithPairs(APair, CommutativeRing):
    """ Implementation of a commutative ring where sums and products
    are represented as dictionaries of pairs.
    """
    __slots__ = ['_symbols', '_symbols_data', '_has_active',
                 #'head', 'data','_hash',
                 ]
    
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

    __repr__ = CommutativeRing.__repr__

    def __new__(cls, data, head=None, new=APair.__new__):
        if head is None:
            if type(data) is cls:
                return data
            return cls.convert(data)
        if (head is TERMS or head is FACTORS) and type(data) is not dict:
            data = dict(data)
        return new(cls, head, data)
        obj = object.__new__(cls)
        obj.head = head
        obj.data = data
        return obj

    def __eq__(self, other):
        if self is other:
            return True
        to = type(other)
        if to is type(self):
            return self.head == other.head and self.data == other.data
        if self.head is NUMBER and (to is int or to is long):
            return self.data == other
        return False

    def __nonzero__(self):
        return self.head is not NUMBER or bool(self.data)

    def copy(self, new=object.__new__):
        """ Return a copy of self.
        """
        head = self.head
        if head is TERMS or head is FACTORS:
            obj = new(type(self))
            obj.head = head
            obj.data = dict(self.data)
            return obj
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
        elif head in [TERMS, FACTORS]:
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
        tobj = type(obj)
        if tobj is int or tobj is long:
            if obj < 0:
                return str_SUM, str(obj)
            return str_NUMBER, str(obj)
        if hasattr(obj, 'to_str_data'):
            return obj.to_str_data(sort)
        raise NotImplementedError('%s.coefficient_to_str_data(%r)' % (cls.__name__, obj))

    @classmethod
    def exponent_to_str_data(cls, obj, sort=True):
        tobj = type(obj)
        if tobj is int or tobj is long:
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
        if head is TERMS:
            pos_dict = {}
            neg_dict = {}
            for t, c in self.data.iteritems():
                if isinstance(c, realtypes) and c<0:
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
        if head is FACTORS:
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
        """ Return callable func such that ``self.func(**self.args) == self``
        """
        head = self.head
        data = self.data
        if head is SYMBOL or head is NUMBER:
            return lambda : self
        elif head is TERMS:
            if len(self.data)==1:
                return self.Mul
            return self.Add
        elif head is FACTORS:
            if len(data)>1:
                return self.Mul
            return self.Pow
        elif callable(head):
            return head
        raise NotImplementedError(`self, head`)

    @property
    def args(self):
        """ Return a sequence args such that ``self.func(**self.args) == self``
        """
        head = self.head
        if head is SYMBOL or head is NUMBER:
            return []
        elif head is TERMS:
            if len(self.data)==1:
                t, c = self.data.items()[0]
                return [self.convert(c)] + t.as_Mul_args()
            return self.as_Add_args()
        elif head is FACTORS:
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
        return self.head is TERMS and len(self.data) > 1

    @property
    def is_Mul(self):
        return (self.head is TERMS and len(self.data) == 1) \
            or (self.head is FACTORS and len(self.data) > 1)

    @property
    def is_Pow(self):
        return self.head is FACTORS and len(self.data) == 1

    @property
    def is_Number(self):
        return self.head is NUMBER

    @property
    def is_Symbol(self):
        return self.head is SYMBOL

    def as_Add_args(self):
        head = self.head
        data = self.data
        if head is TERMS:
            if len(data)==1:
                return [self]
            return [t * c for t,c in data.iteritems()]
        return [self]

    def as_Mul_args(self):
        head = self.head
        data = self.data
        if head is TERMS and len(data)==1:
            t,c = data.items()[0]
            return [self.convert(c)] + t.as_Mul_args()
        if head is FACTORS:
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
        if head is FACTORS:
            if len(data)==1:
                return data.items()[0]
            return [self, self.one_e] #XXX: improve me
        return [self, self.one_e]

    def as_Terms_args(self):
        head = self.head
        if head is NUMBER:
            return [(self.one, self.data)]
        if head is TERMS:
            return self.data.items()
        return [(self, self.one_c)]

    def as_Factors_args(self):
        head = self.head
        if head is FACTORS:
            return self.data.items()
        return [(self, self.one_e)]
    
    def as_primitive(self):
        """ Convert algebra element to a primitive algebra element.
        """
        head = self.head
        func = self.func
        args = self.args
        if func==self.Add:
            r = PrimitiveAlgebra((TERMS,tuple(map(PrimitiveAlgebra, args))))
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
                r = PrimitiveAlgebra((FACTORS,tuple(args)))
                r.commutative_mul = True
                r = -r
            else:
                args = map(PrimitiveAlgebra, args)
                r = PrimitiveAlgebra((FACTORS,tuple(args)))
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

    @classmethod
    def Symbol(cls, obj, new=object.__new__):
        """ Construct new symbol instance as an algebra element.
        """
        r = new(cls)
        r.head = SYMBOL
        r.data = obj
        return r

    @classmethod
    def Number(cls, obj, new=object.__new__):
        """ Construct new number instance as an algebra number.
        """
        r = new(cls)
        r.head = NUMBER
        r.data = obj
        return r

    @classmethod
    def Add(cls, *seq):
        """ Return canonized sum as an algebra element.
        """
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
        """ Return canonized product as an algebra element.
        """
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
    def Pow(cls, base, exp):
        return pow_method(base, exp)

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
        if type(other) is type(self):
            return self.data < other.data
        return self.data < other
    def __le__(self, other):
        if type(other) is type(self):
            return self.data <= other.data
        return self.data <= other
    def __gt__(self, other):
        if type(other) is type(self):
            return self.data > other.data
        return self.data > other
    def __ge__(self, other):
        if type(other) is type(self):
            return self.data >= other.data
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
            elif head is TERMS:
                _symbols_data = set()
                for k in self.data:
                    _symbols_data |= k._get_symbols_data()
            elif head is FACTORS:
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
        """ Return as set of symbols that are contained in self.
        """
        symbols = self._symbols
        if symbols is None:
            cls = type(self)
            Symbol = cls.Symbol
            symbols = self._symbols = set([Symbol(d) for d in self._get_symbols_data()])
        return symbols

    def has_symbol(self, symbol):
        """ Check if self contains symbol.
        """
        return symbol.data in self._get_symbols_data()

    def has(self, subexpr):
        """ Check if self contains sub-expression.
        """
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

        if head is TERMS:
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

        elif head is FACTORS:
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

    def as_term_intcoeff(self):
        """ Return ``(term, coeff)`` such that self=term*coeff and
        coeff is integer.
        """
        head = self.head
        data = self.data
        if head is NUMBER:
            td = type(data)
            if td is int or td is long:
                return self.one, data
            if td is FractionTyple:
                n,p = data
                return self.Number(FractionTuple((1, p))), n
        elif head is TERMS:
            if len(data)==1:
                t, c = data.items()[0]
                td = type(c)
                if td is int or td is long:
                    return t, c
                if td is FractionTuple:
                    n,p = c
                    return t * FractionTyple((1,p)), n
        return self, 1

    def to_polynomial_data(self, variables=None, fixed=False):
        """ Convert pairs representation to ``{exponents: coeff},
        variables_list`` representation.

        For example::
        
          x**2 + 3*sin(x) -> {(2,0):1, (0,1):3}, [x,sin(x)]
          3*x*(x+y)**2 -> {(1,2):3}, [x, x+y]

        Notes:

        * In general, ``exponent``-s are tuples of integers. An
          expection is when ``len(variable_list)==1``: ``exponent``-s
          will be integers.

        * When ``fixed`` is True then one must provide ``variables` list
          that will be equal to returned ``variable_list``. Symbols
          not in a variables list are treated as coefficients.
          
        """
        head = self.head
        data = self.data
        cls = type(self)
        if variables is None:
            assert not fixed
            variables = []
        else:
            variables = list(variables)
        if head is NUMBER:
            l = len(variables)
            if l==1:
                return {0 : data}, variables
            return {(0,)*l : data}, variables
        if head is TERMS:
            exps_append_methods = []
            exponents = []
            coeffs = []
            for t, c in data.iteritems():
                if fixed:
                    rest = 1
                h = t.head
                exps = [0] * len(variables)
                exps_append_methods.append(exps.append)
                if h is FACTORS:
                    for f, e in t.data.iteritems():
                        if isinstance(e, CommutativeRing):
                            r, e  = e.as_term_intcoeff()
                            f = f**r
                        else:
                            te = type(e)
                            if te is FractionTuple:
                                n,p = e
                                f = f ** FractionTuple((1,p))
                                e = n
                            elif te is int or te is long:
                                pass
                            else:
                                f = cls.Factors((f,e))
                                e = 1
                        try:
                            i = variables.index(f)
                        except ValueError:
                            if fixed:
                                # XXX: that's a bit slow
                                rest *= f**e
                            else:
                                i = len(variables)
                                variables.append(f)
                                [mth(0) for mth in exps_append_methods]
                                exps[i] += e
                        else:
                            exps[i] += e
                elif h is NUMBER:
                    assert t.data==1,`t`
                else:
                    try:
                        i = variables.index(t)
                    except ValueError:
                        if fixed:
                            rest *= t
                        else:
                            i = len(variables)
                            variables.append(t)
                            [mth(0) for mth in exps_append_methods]
                            exps[i] += 1
                    else:
                        exps[i] += 1
                exponents.append(exps)
                if fixed and rest is not 1:
                    c = c * rest
                coeffs.append(c)
            l = len(variables)
            d = {}
            if l==1:
                for exps, coeff in zip(exponents, coeffs):
                    d[exps[0]] = coeff
            else:
                for exps, coeff in zip(exponents, coeffs):
                    d[tuple(exps)] = coeff
            return d, variables
        elif head is FACTORS:
            exps = [0] * len(variables)
            coeff = 1
            for f, e in data.iteritems():
                if isinstance(e, CommutativeRing):
                    r, e  = e.as_term_intcoeff()
                    f = f**r
                else:
                    te = type(e)
                    if te is FractionTuple:
                        n,p = e
                        f = f ** FractionTuple((1,p))
                        e = n
                    elif te is int or te is long:
                        pass
                    else:
                        f = cls.Factors((f,e))
                        e = 1
                try:
                    i = variables.index(f)
                except ValueError:
                    if fixed:
                        coeff *= f**e
                        continue
                    i = len(variables)
                    variables.append(f)
                    exps.append(0)
                exps[i] += e
            l = len(variables)
            if l==1:
                return {exps[0]: coeff}, variables
            return {tuple(exps): coeff}, variables
        else:
            coeff = 1
            l = len(variables)
            exps = [0]*l
            try:
                i = variables.index(self)
            except ValueError:
                if fixed:
                    coeff = self
                    exps = [0]*l
                else:
                    i = len(variables)
                    variables.append(self)
                    exps.append(1)
                    l += 1
            else:
                exps[i] = 1
            if l==1:
                return {exps[0]: coeff}, variables
            return {tuple(exps): coeff}, variables

classes.CommutativeRingWithPairs = CommutativeRingWithPairs

# initialize one and zero attributes:
CommutativeRingWithPairs.one = CommutativeRingWithPairs.Number(1)
CommutativeRingWithPairs.zero = CommutativeRingWithPairs.Number(0)

