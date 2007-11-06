
from ..core.utils import memoizer_immutable_args, get_object_by_name, UniversalMethod
from ..core import Basic, sympify
from ..core.methods import MutableCompositeDict, ImmutableDictMeths

from .basic import BasicArithmetic
from .function import Function, FunctionSignature

__all__ = ['Mul', 'MutableMul','Pow','Sqrt']

class MutableMul(BasicArithmetic, MutableCompositeDict):
    """Mutable base class for Mul. This class is used temporarily
    during construction of Mul objects.

    See MutableCompositeDict.__doc__ for how to deal with mutable
    instances.
    """

    precedence = Basic.Mul_precedence

    # canonize methods
    
    def update(self, a, p=1, force=False, exp_to_power=True):
        """
        Mul({}).update(a,p) -> Mul({a:p})
        """
        if force:
            # p must be Basic instance
            b = self.get(a,None)
            if b is None:
                self[a] = p
            else:
                self[a] = b + p
            return
        if a.__class__ is dict:
            # construct Mul instance from a canonical dictionary,
            # it must contain Basic instances as keys as well as values.
            assert len(self)==0,`len(self)` # make sure no data is overwritten
            assert p is 1,`p`
            super(MutableMul, self).update(a)
            return
        if a.__class__ is tuple and len(a)==2:
            self.update(*a)
            return
        a = Basic.sympify(a)
        if a.is_MutableAdd and len(a)==1:
            # Mul({x:3,4:1}).update(Add({x:2})) -> Mul({x:3+1,4:1,2:1})
            k, v = a.items()[0]
            self.update(k, p)
            self.update(v, p)
            return
        p = sympify(p)
        if a.is_MutableMul:
            # Mul({x:3}).update(Mul({x:2}), 4) -> Mul({x:3}).update(x,2*4)
            if p.is_Integer:
                for k,v in a.items():
                    self.update(k, v * p)
                return
        elif exp_to_power and a.is_Exp:
            p = a.args[0] * p
            a = Basic.E
        self.update(a, sympify(p), force=True)

    def canonical(self):
        # self will be modified in-place,
        # always return an immutable object
        n = Basic.one
        for k,v in self.items():
            if v.is_zero:
                # Mul({a:0}) -> 1
                del self[k]
                continue
            a = k.try_power(v)
            if a is None:
                continue
            if a.is_Number:
                del self[k]
                n = n * a
            else:
                if a==k and v.is_one: continue
                del self[k]
                self.update(a,exp_to_power=False)
                return self.canonical()
        if self.has_key(n):
            self.update(n,exp_to_power=False)
            return self.canonical()
        self.__class__ = Mul
        if len(self)==0:
            return n
        obj = self
        if len(self)==1:
            # Mul({a:1}) -> a
            k,v = self.items()[0]
            if v.is_one:
                obj = k
        if n.is_one:
            return obj
        return Basic.Add((obj,n))

    # arithmetics methods

    def __imul__(self, other):
        self.update(other)
        return self


class Mul(ImmutableDictMeths, MutableMul):
    """Represents a product, with repeated factors collected into
    powers using a dict representation. The product a**m * b**n
    (where m and n may be arbitrary expressions and not just
    integers) is represented as Mul({a:m, b:n}).

    Note that purely rational multiples are counted using the Add
    class, so 3*x*y**2 --> Add({Mul({x:1, y:2}):3}).
    """

    # constructor methods
    #@memoizer_immutable_args("Mul.__new__")
    def __new__(cls, *args):
        return MutableMul(*args).canonical()

    # arithmetics methods

    def __imul__(self, other):
        return Mul(self, other)

    # object identity methods

    def __iter__(self):
        return iter([t**c for (t,c) in self.items()])

    def __getitem__(self, key):
        if isinstance(key, slice):
            return [t**c for (t,c) in self.items()[key]]
        elif key.__class__ in [int, long]:
            t,c = self.items()[key]
            return t**c
        return dict.__getitem__(self, key)

    def canonical(self):
        return self

    def split(self, op, *args, **kwargs):
        if op == '*':
            return ([x**c for x, c in self.iteritems()])
        if op == '**' and len(self) == 1:
            return list(self.items()[0])
        return [self]

    @property

    def precedence(self):
        return Basic.Mul_precedence

    def tostr(self, level=0):
        seq = []
        p = self.precedence
        pp = Basic.Pow_precedence
        for base, exp in self.iteritems():
            if exp.is_one:
                term = base.tostr(p)
            else:
                if exp==-1:
                    term = '1/%s' % (base.tostr(p))
                else:
                    term = '%s**%s' % (base.tostr(pp), exp.tostr(pp))
                if pp <= p:
                    term = '(%s)' % (term)
            seq.append(term)
        r =  '*'.join(seq).replace('*1/','/')
        if p<=level:
            r = '(%s)' % r
        return r

    def expand(self, *args, **hints):
        """Expand an expression based on different hints. Currently
           supported hints are basic, power, complex, trig and func.
        """
        obj = self
        if hints.get('basic', True):
            items = self.items()
            if len(self)==1:
                base, exponent = items[0]
                b = base.expand(*args, **hints)
                e = exponent.expand(*args, **hints)
                obj = expand_power(b, e)
            elif len(self)==2:
                b1,e1 = items[0]
                b2,e2 = items[1]
                b1 = b1.expand(*args, **hints)
                e1 = e1.expand(*args, **hints)
                b2 = b2.expand(*args, **hints)
                e2 = e2.expand(*args, **hints)
                p1 = expand_power(b1, e1)
                p2 = expand_power(b2, e2)
                obj = expand_mul2(p1, p2)
            else:
                b1,e1 = items[0]
                b1 = b1.expand(*args, **hints)
                e1 = e1.expand(*args, **hints)
                p1 = expand_power(b1,e1)
                p2 = Mul(*items[1:]).expand(*args, **hints)
                obj = expand_mul2(p1, p2)
        return obj

    def try_derivative(self, s):
        terms = self.items()
        factors = []
        for i in xrange(len(terms)):
            b,e = terms[i]
            dbase = b.diff(s)
            dexp = e.diff(s)
            if dexp.is_zero:
                dt = b**(e-1) * dbase * e
            else:
                dt = b**e * (dexp * Basic.Log(b) + dbase * e/b)
            if dt.is_zero:
                continue
            factors.append(Mul(*(terms[:i]+[dt]+terms[i+1:])))
        return Basic.Add(*factors)

    def __call__(self, *args):
        """
        (f**n * g**m)(x) -> f(x)**n * g(x)**m
        """
        return Mul(*[(t(*args), e(*args)) for (t,e) in self.items()])


    @UniversalMethod
    def fdiff(obj, index=1):
        assert not isinstance(obj, BasicType),`obj`
        # (sin*cos)' = sin'*cos + sin*cos'
        terms = obj.items()
        factors = []
        for i in xrange(len(terms)):
            b,e = terms[i]
            dbase = b.fdiff(index)
            dexp = e.fdiff(index)
            if dexp.is_zero:
                dt = b**(e-1) * dbase * e
            else:
                dt = b**e * (dexp * Basic.log(b) + dbase * e/b)
            if dt.is_zero:
                continue
            factors.append(Mul(*(terms[:i]+[dt]+terms[i+1:])))
        return Basic.Add(*factors)

    def try_power(self, other):
        assumptions = get_object_by_name('__assumptions__')
        if other.is_Fraction:
            if assumptions is not None:
                l1 = []
                l2 = []
                for b, e in self.items():
                    if assumptions.check_positive(b):
                        l1.append(b**(e*other))
                    else:
                        l2.append((b,e))
                if l1:
                    return Mul(*(l1+l2))
        return

    def iterMul(self):
        iterator = self.iteritems()
        def itercall():
            b,e = iterator.next()
            if e.is_one:
                return b
            return b**e
        return iter(itercall, False)

    def iterLogMul(self):
        iterator = self.iteritems()
        def itercall():
            b,e = iterator.next()
            if e.is_one:
                return Basic.Log(b)
            return e * Basic.Log(b)
        return iter(itercall, False)

    def clone(self):
        return MutableMul(*[(b.clone(), e.clone()) for b,e in self.items()]).canonical()

    def as_base_exponent(self):
        if len(self)==1:
            return self.items()[0]
        s = set(self.values())
        if len(s)==1:
            return Mul(*self.keys()), s.pop()
        v = s.pop()
        if v.is_Rational:
            p, q = v.p, v.q
            if p<0: sign=-1
            else: sign=1
            for v in s:
                if not v.is_Rational:
                    p = q = sign = 1
                    break
                if v.p>0 and sign==-1: sign=1
                p = Basic.Integer.gcd(abs(v.p), p)
                q = Basic.Integer.gcd(v.q, q)
            c = Basic.Fraction(sign*p,q)
            if c!=1:
                return Mul(*[(b,e/c) for (b,e) in self.items()]), c
        return self, Basic.Integer(1)

    def matches(pattern, expr, repl_dict={}):
        wild_classes = (Basic.Wild, Basic.WildFunctionType)
        if not pattern.atoms(type=wild_classes):
            return Basic.matches(pattern, expr, repl_dict)
        if len(pattern)==1:
            base, exponent = pattern.items()[0]
            if expr.is_Number:
                return (exponent * Basic.Log(base)).matches(Basic.Log(expr), repl_dict)
            b, e = expr.as_base_exponent()
            p1 = e/exponent
            if p1.is_Integer:
                return base.matches(b**p1, repl_dict)
            d = base.matches(b, repl_dict)
            if d is not None:
                d = exponent.replace_dict(d).matches(e, d)
                if d is not None: return d
            return
        wild_part = []
        exact_part = []
        for (b,e) in pattern.iteritems():
            if b.atoms(type=wild_classes) or e.atoms(type=wild_classes):
                wild_part.append((b,e))
            else:
                exact_part.append((b,-e))
        if exact_part:
            exact_part.append((expr, Basic.Integer(1)))
            res = Mul(*wild_part).matches(Mul(*exact_part), repl_dict)
            return res
        log_pattern = Basic.Add(*pattern.iterLogMul())
        log_expr = Basic.Add(*expr.iterLogMul())
        return log_pattern.matches(log_expr, repl_dict)


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
        return Mul(*(num + [1/sympify(x) for x in den]))


class Pow(BasicArithmetic):
    """
    For backward compatibility.

    Pow instances will be never created.
    """
    def __new__(cls, a, b):
        a = Basic.sympify(a)
        b = Basic.sympify(b)
        if b.is_zero: return Basic.one
        if b.is_one: return a
        if a.is_one: return a
        return Mul((a,b))


class Sqrt(Function):
    signature = FunctionSignature((Basic,), (Basic,))
    @classmethod
    def canonize(cls, (arg,), **options):
        return arg ** Basic.Rational(1,2)


@memoizer_immutable_args('expand_power')
def expand_power(x, n):
    """
    x, n must be expanded
    """
    if x.is_Add and n.is_Integer and n.is_positive:
        return expand_integer_power_miller(x, n)
    if x.is_Mul and n.is_Integer:
        return Mul(*[k**(v*n) for k,v in x.items()])
    if n.is_Add:
        # x ** (a+b) -> x**a * x**b
        return Mul(*[x**(c*k) for k,c in n.items()])
    return x ** n

@memoizer_immutable_args('expand_mul2')
def expand_mul2(x, y):
    """
    x, y must be expanded.
    target must be None or MutableAdd instance.
    """
    if x.is_Add and y.is_Add:
        yt = y.items()
        xt = x.items()
        return Basic.Add(*[(t1*t2,c1*c2) for (t1,c1) in xt for (t2,c2) in yt])
    if x.is_Add:
        xt = x.items()
        return Basic.Add(*[(t1*y,c1) for (t1,c1) in xt])
    if y.is_Add:
        return expand_mul2(y, x)
    return x * y

@memoizer_immutable_args('expand_integer_power_miller')
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
    Fraction = Basic.Fraction
    Add = Basic.Add
    m = int(m)
    xt = x.items()
    n = len(xt)-1
    a,b = xt[0]
    x0 = a * b
    p0 = [c*t/x0 for (t,c) in xt]
    l = [x0**m]
    for k in xrange(1, m * n + 1):
        l1 = []
        for i in xrange(1,n+1):
            if i<=k:
                f = Fraction((m+1)*i-k,k)
                p0if = p0[i]*f
                lk = l[k-i]
                if lk.is_Add:
                    l1.extend([(t*p0if,c) for (t,c) in lk.items()])
                else:
                    l1.append(lk*p0if)
        a = Add(*l1)
        l.append(a)
    return Add(*l)
