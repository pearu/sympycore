
from ..core.utils import memoizer_immutable_args, get_object_by_name, UniversalMethod
from ..core import Basic, sympify
from ..core.methods import MutableCompositeDict, ImmutableDictMeths

from .basic import BasicArithmetic
from .function import Function, FunctionSignature

class MutableMul(BasicArithmetic, MutableCompositeDict):
    """Mutable base class for Mul. This class is used temporarily
    during construction of Mul objects.

    See MutableCompositeDict.__doc__ for how to deal with mutable
    instances.
    """

    precedence = Basic.Mul_precedence

    # canonize methods
    
    def update(self, a, p=1, force=False):
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
                self.update(a)
                return self.canonical()
        if self.has_key(n):
            self.update(n)
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

    def __getitem__(self, key):
        if isinstance(key, slice) or key.__class__ in [int, long]:
            return self.items()[key]
        return dict.__getitem__(self, key)

    def canonical(self):
        return self

    def split(self, op, *args, **kwargs):
        if op == '*':
            return ([x**c for x, c in self[:]])
        if op == '**' and len(self) == 1:
            return list(self.items()[0])
        return [self]

    @property

    def precedence(self):
        return Basic.Mul_precedence

    def tostr(self, level=0):
        seq = []
        items = self[:]
        p = self.precedence
        pp = Basic.Pow_precedence
        for base, exp in items:
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

    def __eq__(self, other):
        if isinstance(other, Mul):
            return dict.__eq__(self, other)
        if isinstance(other, Basic):
            return False
        return self==sympify(other)

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

    def clone(self):
        return MutableMul(*[(b.clone(), e.clone()) for b,e in self.items()]).canonical()

    @staticmethod
    def seq_as_base_exponent(seq):
        # seq = [(b1,e1),(b2,e2),..]
        # return None if the result would be (Mul(*seq), 1).
        if len(seq)==1:
            return seq[0]
        s = set([e for (b,e) in seq])
        if len(s)==1:
            v = s.pop()
            if v.is_one: return None
            return Mul(*[b for (b,e) in seq]), v
        v = s.pop()
        c,t = v.as_coeff_term()
        if c==1: return None
        gcd_numer, gcd_denom = c.p, c.q
        if c.p<0: sign = -1
        else: sign = 1
        for v in s:
            c,t = v.as_coeff_term()
            if c==1:
                return self, Basic.Integer(1)
            if c.p>0 and sign==-1: sign=1
            gcd_numer = Basic.Integer.gcd(abs(c.p), gcd_numer)
            gcd_denom = Basic.Integer.gcd(c.q, gcd_denom)
        if gcd_numer==gcd_denom==sign==1:
            return None
        exponent = Basic.Fraction(sign*gcd_numer, gcd_denom)
        r = MutableMul()
        for b,e in seq:
            r.update(b,e/exponent)
        return r.canonical(), exponent

    def as_base_exponent(self):
        r = self.seq_as_base_exponent(self.items())
        if r is None:
            return self, Basic.Integer(1)
        return r

    def matches(pattern, expr, repl_dict={}, evaluate=False):
        pbase, pexponent = pattern.as_base_exponent()
        if not pexponent.is_one:
            ebase, eexponent = expr.as_base_exponent()
            #print `pbase, pexponent`, `ebase, eexponent`
            d = pbase.matches(ebase, repl_dict, evaluate)
            if d is None: return
            d = pexponent.matches(eexponent, d, evaluate)
            return d

        wild_classes = (Basic.Wild,Basic.WildFunctionType)
        wild_part = {}
        exact_part = {}
        for b, e in pattern.items():
            if b.atoms(type=wild_classes) or e.atoms(type=wild_classes):
                wild_part[b] = e
            else:
                exact_part[b] = e
        if exact_part:
            if not expr.is_Mul:
                c, t = expr.as_coeff_term()
                if c==1:
                    items = [(t,1)]
                else:
                    items = [(c,1),(t,1)]
            else:
                items = expr.items()
            new_expr = MutableMul()
            for b,e in items:
                v = exact_part.pop(b, None)
                if v is None:
                    new_expr.update(b,e)
                    continue
                if v==e:
                    continue
                return
            if exact_part:
                return
            return MutableMul(wild_part).canonical()\
                   .matches(Mul(*new_expr.items()),
                            repl_dict, evaluate)
        if len(wild_part)==1:
            # pattern is b**e
            b, e = expr.as_base_exponent()
        print wild_part


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
