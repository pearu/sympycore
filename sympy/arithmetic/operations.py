
import itertools

from ..core import Basic, sympify, objects, classes
from ..core.utils import UniversalMethod
from ..core.function import new_function_value
from .basic import BasicArithmetic
from .function import Function, FunctionSignature

__all__ = ['Pow', 'Mul', 'Add', 'Sub', 'Sqrt', 'Div']

# Exp is defined in sympy.functions but it will be imported
# after sympy.arithmetic (which is setting moo=-oo).
Basic.is_Exp = None

class ArithmeticFunction(Function):
    """ Base class for Add and Mul classes.
    
    Important notes:
    - Add and Mul implement their own __new__ methods.
    - Add and Mul do not implement canonize() method but are
      subclasses of Function.
    - Instances of Add and Mul are created in as_Basic
      methods of TermCoeffDict and BaseExpDict, respectively.
    - One should not subclass from Add and Mul classes.
    - Add and Mul instances have the following attributes:
       * ._dict_content - holds TermCoeffDict or BaseExpDict instance
       * .args - equals to _dict_content.args_flattened
       * .args_sorted - use .get_args_sorted() for initializing
       * .args_frozenset - use .get_args_frozenset() for initializing
       * BaseExpDict instances have additional attribute .coeff such
         that <BaseExpDict instance>[coeff] == 1
         and coeff.is_Number == True
    """

    arguments_sorted = True
    signature = FunctionSignature([BasicArithmetic],(BasicArithmetic,))

    def __eq__(self, other):
        if self.__class__ is other.__class__:
            return dict.__eq__(self._dict_content, other._dict_content)
        if isinstance(other, Basic):
            return False
        if isinstance(other, str):
            return self==sympify(other)
        return False

    def instance_compare(self, other):
        return dict.__cmp__(self._dict_content, other._dict_content)

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
        l.sort(Basic.static_compare)
        if l:
            l.append('')
        return '%s((%s))' % (self.__class__.__name__, ', '.join(map(str,l)))

    def as_Basic(self):
        obj = self.canonical()
        if obj.__class__ is TermCoeffDict:
            obj = new_function_value(Add, self.args_flattened, {})
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
        if acls is Add or acls is TermCoeffDict:
            for k,v in a.iterTermCoeff():
                self.inplace_add(k, v)
            return self

        if acls is Mul:
            # Mul(2,x) -> Add({x:2})
            a, p = a.as_term_coeff()
        elif a.is_Number:
            # Add(3) -> Add({1:3})
            p = a
            a = objects.one
        else:
            p = objects.one

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
        if acls is TermCoeffDict or acls is Add:
            for k,v in a.iterTermCoeff():
                self.inplace_add(k, v*p)
            return

        # Add(3) -> Add({1:3})
        if acls is Mul:
            a, c = a.as_term_coeff()
            p = c * p
        elif a.is_Number:
            p = a * p
            a = objects.one

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
        if 1:
            oo = objects.oo
            zero = objects.zero
            moo = objects.moo
            zoo = objects.zoo
            nan = objects.nan
            one = objects.one
            if self.has_key(nan):
                return nan
            elif self.has_key(zoo):
                self.pop(one, None)
                self.pop(oo, None)
                self.pop(moo, None)
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
            if v.is_zero:
                del self[k]
            elif v.is_one:
                l.append(k)
            else:
                l.append(k * v)
        if len(l)==0:
            return objects.zero
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
        if acls is TermCoeffDict or acls is Add:
            for k,v in a.iterTermCoeff():
                for k1,v1 in items:
                    self.inplace_add(k*k1,v*v1)
            return self
        term, coeff = a.as_term_coeff()
        if coeff.is_one:
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
        if acls is TermCoeffDict or acls is Add:
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
        if a.is_one:
            return self
        d = TermCoeffDict(())
        d.update(self)
        d *= a
        return d

    def __add__(self, a):
        if a.is_zero:
            return self
        d = TermCoeffDict(())
        d.update(self)
        d += a
        return d

class Add(ArithmeticFunction):

    def __new__(cls, *args):
        return TermCoeffDict(map(sympify,args)).as_Basic()
    
    @property
    def precedence(self):
        return Basic.Add_precedence

    def tostr(self, level=0):
        p = self.precedence
        r = ' + '.join([op.tostr(p) for op in self.iterSorted()]) or '0'
        r = r.replace(' + -',' - ')
        if p<=level:
            r = '(%s)' % r
        return r

    def iterTermCoeff(self):
        return self._dict_content.iterTermCoeff()

    def iterAdd(self):
        return iter(self.args)

    def expand(self, **hints):
        if hints.get('basic', True):
            return Add(*[item.expand(**hints) for item in self])
        return self

    def try_derivative(self, s):
        return Add(*[t.diff(s) * e for (t,e) in self.iterTermCoeff()])

    def __mul__(self, other):
        other = sympify(other)
        if other.is_Number:
            return (self._dict_content * other).as_Basic()
        return classes.Mul(self, other)

    def matches(pattern, expr, repl_dict={}):
        wild_classes = (Basic.Wild, Basic.WildFunctionType)
        if not pattern.atoms(type=wild_classes):
            return Basic.matches(pattern, expr, repl_dict)
        wild_part = TermCoeffDict(())
        exact_part = TermCoeffDict(())
        for (t,c) in pattern.iterTermCoeff():
            if t.atoms(type=wild_classes):
                wild_part += (t, c)
            else:
                exact_part += (t, -c)
        if exact_part:
            exact_part += expr
            res = wild_part.as_Basic().matches(exact_part.as_Basic(), repl_dict)
            return res
        piter = pattern.iterTermCoeff()
        pt, pc = piter.next()
        rpat = TermCoeffDict(tuple(piter)).as_Basic()
        if expr.is_Add:
            items1, items2 = [], []
            for item in expr.iterTermCoeff():
                if item[1]==pc:
                    items1.append(item)
                else:
                    items2.append(item)
            items = items1 + items2
        else:
            items = [expr.as_term_coeff()]
        for i in xrange(len(items)):
            t, c = items[i]
            d = pt.matches(t*(c/pc), repl_dict)
            if d is None:
                continue
            npat = rpat.replace_dict(d)
            nexpr = TermCoeffDict(items[:i]+items[i+1:]).as_Basic()
            d = npat.matches(nexpr, d)
            if d is not None:
                return d
        d = pt.matches(objects.zero, repl_dict)
        if d is not None:
            d = rpat.replace_dict(d).matches(expr, d)
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
            obj = new_function_value(Mul, self.args_flattened, {})
            obj._dict_content = self
        else:
            self.args_flattened = [obj]
        return obj

    def __imul__(self, a, exp_to_power=True):
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


        if acls is BaseExpDict or acls is Mul:
            for k,v in a.iterBaseExp():
                self.inplace_mul(k, v, exp_to_power=exp_to_power)
            return self
        elif acls is Pow:
            p = a.exponent
            a = a.base
        elif exp_to_power and a.is_Exp:
            p = a.args[0]
            a = objects.E
        else:
            p = objects.one

        b = self.get(a)
        if b is None:
            self[a] = p
        else:
            self[a] = b + p
        return self

    def inplace_mul(self, a, p, exp_to_power=True):
        """
        BaseExpDict({}).update(a,p) -> BaseExpDict({a:p})
        """
        acls = a.__class__

        a = sympify(a)

        if (acls is Mul and p.is_Integer) or acls is BaseExpDict:
            for k,v in a.iterBaseExp():
                self.inplace_mul(k, v*p, exp_to_power=exp_to_power)
            return self
        elif acls is Pow and p.is_Integer:
            p = a.exponent * p
            a = a.base
        elif exp_to_power and a.is_Exp:
            p = a.args[0] * p
            a = objects.E
        b = self.get(a)
        if b is None:
            self[a] = p
        else:
            self[a] = b + p
        return self

    def canonical(self):
        one = objects.one
        zero = objects.zero
        oo = objects.oo
        nan = objects.nan
        n = objects.one
        
        for k, v in self.items():
            if v.is_zero:
                del self[k]
                continue
            if v.is_one and not k.is_Number:
                continue
            a = k.try_power(v)
            if a is None:
                continue
            del self[k]
            if a.is_Number:
                n = n * a
            else:
                if not n.is_one:
                    self.__imul__(n, exp_to_power=False)
                self.__imul__(a, exp_to_power=False)
                return self.canonical()
        v = self.get(n,None)
        if v is not None:
            self[n] = v + one
            n = one
        if 0: pass
        elif self.has_key(nan):
            return nan
        elif self.has_key(oo):
            if n < 0: n=-one
            elif n > 0: n=one
            else: return nan
        elif n.is_zero:
            #XXX: assert not self.has(oo),`self`
            return n

        if len(self)==0:
            return n
        if len(self)==1:
            k, v = self.items()[0]
            if n.is_one:
                if v.is_one:
                    return k
                return Pow(k, v, normalized=False)
            if v.is_one and k.is_Add:
                return k * n
        l = []
        for k, v in self.iterBaseExp():
            if v.is_one:
                l.append(k)
            else:
                if v.is_one:
                    l.append(k)
                else:
                    l.append(Pow(k, v, normalized=False))
        if not n.is_one:
            l.insert(0, n)
            self[n] = one
        self.coeff = n
        self.args_flattened = l
        return self

    def __iter__(self):
        return iter(self.args_flattened)

    iterBaseExp = dict.iteritems


class Mul(ArithmeticFunction):

    def __new__(cls, *args):
        return BaseExpDict(map(sympify,args)).as_Basic()
    
    @property
    def precedence(self):
        return Basic.Mul_precedence

    def tostr(self, level=0):
        p = self.precedence
        r = '*'.join([op.tostr(p) for op in self.iterSorted()]) or '1'
        r = r.replace('-1*','-')
        if p<=level:
            r = '(%s)' % r
        return r

    def iterBaseExp(self, full=False):
        coeff = self._dict_content
        if not full or (coeff.is_one or not coeff.is_Rational):
            return self._dict_content.iterBaseExp()

    def expand(self, **hints):
        if hints.get('basic', True):
            it = iter(self)
            a = it.next()
            b = Mul(*it)
            a = a.expand(**hints)
            b = b.expand(**hints)
            if a.is_Add:
                return (a._dict_content * b).as_Basic()
            elif b.is_Add:
                return (b._dict_content * a).as_Basic()
            return Mul(a, b)
        return self

    def iterMul(self):
        return iter(self)

    def as_term_coeff(self):
        d = self._dict_content
        c = d.coeff
        if c.is_one:
            return self, c
        d = BaseExpDict(())
        for k,v in self.iterBaseExp():
            if k==c: continue
            d[k] = v
        return d.as_Basic(), c

    def as_base_exponent(self):
        if not self._dict_content.coeff.is_one:
            t, c = self.as_term_coeff()
            b, e = t.as_base_exponent()
            p = c.try_power(1/e)
            if p is not None:
                return p*b, e
            return self, objects.one
        p = None
        for b,e in self.iterBaseExp():
            if not e.is_Rational:
                p = None
                break
            if p is None:
                p, q = e.p, e.q
                if p<0:
                    sign = -1
                else:
                    sign = 1
            else:
                if e.p>0 and sign==-1:
                    sign = 1
                p = Basic.Integer.gcd(abs(e.p), p)
                q = Basic.Integer.gcd(e.q, q)
        if p is not None:
            c = Basic.Fraction(sign*q,p)
            if not c.is_one:
                return BaseExpDict([(b,e*c) for (b,e) in self.iterBaseExp()]).as_Basic(),1/c
        return self, objects.one


    def try_power(self, other):
        t, c = self.as_term_coeff()
        if not c.is_one and other.is_Rational:
            return c**other * t**other

    def try_derivative(self, s):
        terms = list(self)
        factors = []
        for i in xrange(len(terms)):
            dt = terms[i].diff(s)
            if dt.is_zero:
                continue
            factors.append(classes.Mul(*(terms[:i]+[dt]+terms[i+1:])))
        return classes.Add(*factors)

    def __mul__(self, other):
        other = sympify(other)
        if other.is_Number:
            if other.is_one:
                return self
            # here we shall skip d.canonical()
            d = BaseExpDict(())
            one = objects.one
            td = self._dict_content
            d.update(td)
            if td.coeff.is_one:
                coeff = other
                l = [other] + td.args_flattened
            else:
                coeff = other * td.coeff
                l = [coeff] + td.args_flattened[1:]
                del d[td.coeff]
            d[coeff] = one
            d.coeff = coeff
            d.args_flattened = l
            obj = new_function_value(Mul, l, {})
            obj._dict_content = d
            return obj
        return classes.Mul(self, other)

    def matches(pattern, expr, repl_dict={}):
        wild_classes = (Basic.Wild, Basic.WildFunctionType)
        if not pattern.atoms(type=wild_classes):
            return Basic.matches(pattern, expr, repl_dict)
        wild_part = BaseExpDict(())
        exact_part = BaseExpDict(())
        for (b,e) in pattern.iterBaseExp():
            if b.atoms(type=wild_classes) or e.atoms(type=wild_classes):
                wild_part *= (b, e)
            else:
                exact_part *= (b, -e)
        if exact_part:
            exact_part *= expr
            res = wild_part.as_Basic().matches(exact_part.as_Basic(), repl_dict)
            return res
        log_pattern = Basic.Add(*pattern.iterLogMul())
        log_expr = Basic.Add(*expr.iterLogMul())
        return log_pattern.matches(log_expr, repl_dict)


class Pow(Function):

    signature = FunctionSignature((BasicArithmetic,BasicArithmetic),(BasicArithmetic,))
    
    @classmethod
    def canonize(cls, (base, exponent), options):
        if options.get('normalized', True):
            if exponent.is_zero:
                return objects.one
            if exponent.is_one:
                return base
            if base.is_one:
                return base
            return base.try_power(exponent)
        return

    @property
    def base(self):
        return self.args[0]

    @property
    def exponent(self):
        return self.args[1]

    @property
    def precedence(self):
        return Basic.Pow_precedence

    def tostr(self, level=0):
        p = self.precedence
        b = self.base.tostr(p)
        e = self.exponent.tostr(p)
        r = '%s**%s' % (b, e)
        if p<=level:
            r = '(%s)' % r
        return r
    
    def expand(self, **hints):
        if hints.get('basic', True):
            b = self.base.expand(**hints)
            e = self.exponent.expand(**hints)
            if b.is_Add and e.is_Integer and e>0:
                return expand_integer_power_miller(b, e)
            if b.is_Mul and e.is_Integer:
                return Mul(*[Pow(b, e*n) for (b,n) in b.iterBaseExp()])
            if e.is_Add:
                # XXX: b.is_Mul
                return Mul(*[Pow(b, item) for item in e])
            return Pow(b, e)
        return self

    def try_derivative(self, s):
        b,e = self.args
        dbase = b.diff(s)
        dexp = e.diff(s)
        if dexp.is_zero:
            dt = b**(e-1) * dbase * e
        else:
            dt = b**e * (dexp * classes.Log(b) + dbase * e/b)
        return dt

    def try_power(self, other):
        if other.is_Integer:
            return Pow(self.base, self.exponent * other)

    def iterPow(self):
        return itertools.chain(self.base.iterPow(), iter([self.exponent]))

    def as_base_exponent(self):
        return self.base, self.exponent

    def matches(pattern, expr, repl_dict={}):
        wild_classes = (Basic.Wild, Basic.WildFunctionType)
        if not pattern.atoms(type=wild_classes):
            return Basic.matches(pattern, expr, repl_dict)
        pb, pe = pattern.args
        if expr.is_Number:
            r = (pe * Basic.Log(pb)).matches(Basic.Log(expr), repl_dict)
            return r
        b, e = expr.as_base_exponent()
        p1 = e/pe
        if p1.is_Integer:
            return pb.matches(b**p1, repl_dict)
        d = pb.matches(b, repl_dict)
        if d is not None:
            d = pe.replace_dict(d).matches(e, d)
            if d is not None:
                return d
        d = pe.matches(e, repl_dict)
        if d is not None:
            d = pb.replace_dict(d).matches(b, d)
            if d is not None:
                return d
        return

class Sqrt(Pow):

    def __new__(cls, base):
        return Pow(base, classes.Fraction(1,2))

class Sub(BasicArithmetic):
    """
    Sub() <=> 0
    Sub(x) <=> -x
    Sub(x, y, z, ...) <=> x - (y + z + ...)
    """
    def __new__(cls, *args):
        if len(args) == 1:
            return -sympify(args[0])
        pos, neg = list(args[:1]), args[1:]
        return Add(*(pos + [-Add(*neg)]))

class Div(BasicArithmetic):
    """
    Div() <=> 1
    Div(x) <=> 1/x
    Div(x, y, z, ...) <=> x / (y * z * ...)
    """
    def __new__(cls, *args):
        if len(args) == 1:
            return 1/sympify(args[0])
        num, den = list(args[:1]), args[1:]
        return Mul(*(num + [1/Mul(*den)]))

# ALGORITHMS

def expand_integer_power_miller(x, m):
    """
    x, m must be expanded
    x must be Add instance
    m must be positive integer
    """
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
    Fraction = classes.Fraction
    m = int(m)
    n = len(x)-1
    xt = x.args
    x0 = xt[0]
    p0 = [item/x0 for item in xt]
    r = TermCoeffDict(())
    d1 = TermCoeffDict((x0**m,))
    r += d1.canonical()
    l = [d1]
    for k in xrange(1, m * n + 1):
        d1 = TermCoeffDict(())
        for i in xrange(1, min(n+1,k+1)):
            nn = (m+1)*i-k
            if nn:
                d1 += (l[k-i] * p0[i], Fraction(nn,k))
        r += d1.canonical()
        l.append(d1)
    return r.as_Basic()
