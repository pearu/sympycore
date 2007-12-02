"""
Defines TermCoeffDict and BaseExpDict classes for holding
and manipulating sums and products efficiently. The instances
of these classes are used as internal data representations
in Add and Mul classes, respectively.
"""

import itertools

from ..core import Basic, sympify, objects, classes
from ..core.function import new_function_value

__all__ = ['TermCoeffDict', 'BaseExpDict']

one = objects.one
zero = objects.zero
oo = objects.oo
zoo = objects.zoo
nan = objects.nan
E = objects.E

class TermCoeffDict(dict):
    """
    Holds (term, coeff) pairs of a sum.
    """

    # constructor methods
    def __new__(cls, args):
        obj = dict.__new__(cls)
        for a in args:
            obj += a
        return obj

    def __init__(self, *args):
        # avoid calling default dict.__init__.
        pass

    def __repr__(self):
        l = self.items()
        l.sort(cmp)
        if l:
            l.append('')
        return '%s((%s))' % (self.__class__.__name__, ', '.join(map(str,l)))

    def as_Basic(self):
        obj = self.canonical()
        if obj.__class__ is TermCoeffDict:
            obj = new_function_value(classes.Add, self.args_flattened, {})
            obj._dict_content = self
        else:
            self.args_flattened = [obj]
        return obj

    def __iadd__(self, a):
        acls = a.__class__

        if acls is tuple:
            self.inplace_add(*a)
            return self
        
        elif acls is dict:
            # construct TermCoeffDict instance from a canonical dictionary
            # it must contain Basic instances as keys as well as values.
            assert len(self)==0,`len(self)` # make sure no data is overwritten
            self.update(a)
            return self
        
        # Flatten sum
        if acls is TermCoeffDict or a.is_Add:
            for k,v in a.iterTermCoeff():
                self.inplace_add(k, v)
            return self

        if a.is_Mul:
            # Mul(2,x) -> Add({x:2})
            a, p = a.as_term_coeff()
        elif a.is_Number:
            # Add(3) -> Add({1:3})
            p = a
            a = one
        else:
            p = one

        # If term is already present, add the coefficients together.
        # Otherwise insert new term.
        b = self.get(a, None)
        if b is None:
            self[a] = p
        else:
            # Note: we don't have to check if the coefficient turns to
            # zero here. Zero terms are cleaned up later, in canonical()
            self[a] = b + p
        return self

    def inplace_add(self, a, p):
        """
        TermCoeffDict({}).update(a,p) -> TermCoeffDict({a:p})
        """
        acls = a.__class__
        # Flatten sum
        if acls is TermCoeffDict or a.is_Add:
            for k,v in a.iterTermCoeff():
                self.inplace_add(k, v*p)
            return

        # Add(3) -> Add({1:3})
        if a.is_Mul:
            a, c = a.as_term_coeff()
            p = c * p
        elif a.is_Number:
            p = a * p
            a = one

        # If term is already present, add the coefficients together.
        # Otherwise insert new term.
        b = self.get(a, None)
        if b is None:
            self[a] = p
        else:
            # Note: we don't have to check if the coefficient turns to
            # zero here. Zero terms are cleaned up later, in canonical()
            self[a] = b + p
        return

    def canonical(self):
        if self.has_key(nan):
            return nan
        elif self.has_key(zoo):
            self.pop(one, None)
            self.pop(oo, None)
            #self.pop(moo, None)
        elif self.has_key(oo):
            #if self.has_key(moo):
            #    return nan
            v = self[oo]
            if v==0:
                return nan
            self.pop(one, None)
        #elif self.has_key(moo):
        #    if self.has_key(oo):
        #        return nan
        #    self.pop(one, None)
        l = []
        for k, v in self.items():
            if v is zero:
                del self[k]
            elif v is one:
                l.append(k)
            else:
                l.append(k * v)
        if len(l)==0:
            return zero
        if len(l)==1:
            return l[0]
        self.args_flattened = l
        return self

    def __iter__(self):
        return iter(self.args_flattened)

    iterTermCoeff = dict.iteritems
    iterAdd = __iter__

    def __imul__(self, a):
        acls = a.__class__
        if acls is tuple:
            return self.inplace_mul(*a)
        if a.is_Number:
            for k,v in self.items():
                self[k] = v*a
            return self
        items = self.items()
        self.clear()
        if acls is TermCoeffDict or a.is_Add:
            for k,v in a.iterTermCoeff():
                for k1,v1 in items:
                    self.inplace_add(k*k1,v*v1)
            return self
        term, coeff = a.as_term_coeff()
        if coeff is one:
            for k, v in items:
                self.inplace_add(k*term, v)
        else:
            for k, v in items:
                self.inplace_add(k*term, v*coeff)
        return self

    def inplace_mul(self, a, p):
        if a.is_Number:
            p1 = a*p
            for k,v in self.items():
                self[k] = v*p1
            return self
        items = self.items()
        self.clear()
        acls = a.__class__
        if acls is TermCoeffDict or a.is_Add:
            for k,v in a.iterTermCoeff():
                p1 = v*p
                for k1,v1 in items:
                    self.inplace_add(k*k1,v*p1)
            return self
        term, coeff = a.as_term_coeff()
        p1 = coeff*p
        for k, v in items:
            self.inplace_add(k*term, v*p1)
        return self

    def __mul__(self, a):
        if a is one:
            return self
        d = TermCoeffDict(())
        d.update(self)
        d *= a
        return d

    def __add__(self, a):
        if a is zero:
            return self
        d = TermCoeffDict(())
        d.update(self)
        d += a
        return d


class BaseExpDict(dict):
    """
    Holds (base, exponent) pairs of a product.
    """
    
    # constructor methods
    def __new__(cls, args):
        obj = dict.__new__(cls)
        for a in args:
            obj *= a
        return obj

    def __init__(self, *args):
        # avoid calling default dict.__init__.
        pass

    def as_Basic(self):
        obj = self.canonical()
        if obj.__class__ is BaseExpDict:
            obj = new_function_value(classes.Mul, self.args_flattened, {})
            obj._dict_content = self
        else:
            self.args_flattened = [obj]
        return obj

    def __imul__(self, a):
        acls = a.__class__
        if acls is tuple:
            self.inplace_mul(*a)
            return self

        if acls is dict:
            # construct BaseExpDict instance from a canonical dictionary,
            # it must contain Basic instances as keys as well as values.
            assert len(self)==0,`len(self)` # make sure no data is overwritten
            dict.update(self, a)
            # make sure to set also coeff attribute that contains a
            # dictionary key of Number instance that has value 1,
            # ie it is a coefficient.
            return self

        if acls is BaseExpDict or a.is_Mul:
            for k,v in a.iterBaseExp():
                self.inplace_mul(k, v)
            return self
        elif a.is_Pow:
            p = a.exponent
            a = a.base
        else:
            p = one

        b = self.get(a)
        if b is None:
            self[a] = p
        else:
            self[a] = b + p
        return self

    def inplace_mul(self, a, p):
        """
        BaseExpDict({}).update(a,p) -> BaseExpDict({a:p})
        """
        a = sympify(a)
        acls = a.__class__

        if (a.is_Mul and p.is_Integer) or acls is BaseExpDict:
            for k,v in a.iterBaseExp():
                self.inplace_mul(k, v*p)
            return self
        elif a.is_Pow and p.is_Integer:
            p = a.exponent * p
            a = a.base
        b = self.get(a)
        if b is None:
            self[a] = p
        else:
            self[a] = b + p
        return self

    def canonical(self):
        n = one
        flag = True
        for k, v in self.items():
            if v is zero:
                del self[k]
                continue
            if v is one and not k.is_Number:
                flag = False
                continue
            flag = flag and k.is_Number and v.is_Number and k.is_positive
            a = k.try_power(v)
            if a is None:
                continue
            del self[k]
            if a.is_Number:
                n = n * a
            else:
                if not n is one:
                    self *= n
                self *= a
                return self.canonical()
        v = self.get(n,None)
        if v is not None:
            self[n] = v + one
            n = one
        if self.has_key(nan):
            return nan
        elif self.has_key(oo):
            if n < 0:
                n=-one
            elif n > 0:
                n=one
            else:
                return nan
        elif n is zero:
            #XXX: assert not self.has(oo),`self`
            return n
        if len(self)==0:
            return n
        if flag:
            print n,self
            d = self.inverse_dict()
            if len(d) < len(self):
                self.clear()
                for v, k in d.iteritems():
                    print (k,v),k.try_power(v)
                    self[k] = v
        if len(self)==1:
            k, v = self.items()[0]
            if n is one:
                return classes.Pow(k, v, normalized=False)
            if v is one and k.is_Add:
                return k * n
        l = []
        for k, v in self.iterBaseExp():
            if v is one:
                l.append(k)
            else:
                l.append(classes.Pow(k, v, normalized=False))
        if n is not one:
            l.insert(0, n)
            self[n] = one
        self.coeff = n
        self.args_flattened = l
        return self

    def inverse_dict(self):
        d = {}
        for k, v in self.iterBaseExp():
            n = d.get(v,None)
            if n is None:
                d[v] = k
            else:
                d[v] = n * k
        return d

    def __iter__(self):
        return iter(self.args_flattened)

    iterBaseExp = dict.iteritems

    def __mul__(self, a):
        if a is one:
            return self
        d = self.__class__(())
        d.update(self)
        d *= a
        return d


class _IntegerMonomial(BaseExpDict):
    """Integer monomial - a monomial with positive integer
    bases and fractional exponents.
    """

    def __imul__(self, a):
        acls = a.__class__
        if acls is tuple:
            return self.inplace_mul(*a)

        if acls is dict:
            assert len(self)==0,`len(self)` # make sure no data is overwritten
            dict.update(self, a)
            return self

        return self.inplace_mul(a, one)

    def inplace_mul(self, a, p):
        """
        BaseExpDict({}).update(a,p) -> BaseExpDict({a:p})
        """
        a = sympify(a)
        acls = a.__class__

        if acls is IntegerMonomial:
            for k,v in a.iterBaseExp():
                self.inplace_mul(k, v*p)
            return self
        elif a.is_Pow:
            p = a.exponent * p
            a = a.base

        if a.is_Integer:
            factors = classes.Integer.factor_trial_division(a.p)
            factors.pop(1, None)
            if not factors:
                return self
            if len(factors)>1:
                for k, v in factors.iteritems():
                    self.inplace_mul(classes.Integer(k), v * p)
                return self
            k, v = factors.popitem()
            a = classes.Integer(k)
            p = v * p
        elif a.is_Fraction:
            self.inplace_mul(a.p, p)
            self.inplace_mul(a.q, -p)
            return self
        else:
            assert a.is_Rational,`a,p`

        b = self.get(a)
        if b is None:
            self[a] = p
        else:
            self[a] = b + p
        return self








