
import itertools
from ..core import Basic, sympify, objects, classes
from .basic import BasicArithmetic
from .function import Function, FunctionSignature

__all__ = ['Pow', 'Sqrt']

one = objects.one
zero = objects.zero
oo = objects.oo
zoo = objects.zoo
nan = objects.nan
E = objects.E
half = objects.half

class Pow(Function):
    """ Represents an evaluated exponentation operation.
    """

    signature = FunctionSignature((BasicArithmetic, BasicArithmetic),
                                  (BasicArithmetic,))
    
    @classmethod
    def canonize(cls, (base, exponent), options):
        if base is E:
            return classes.Exp(exponent)
        if exponent is half:
            return classes.Sqrt(base)
        if exponent is zero:
            return one
        if exponent is one:
            return base
        if base is one:
            return base
        if options.get('normalized', True):
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
                return classes.Mul(*[Pow(b, e*n) for (b,n) in b.iterBaseExp()])
            if e.is_Add:
                # XXX: b.is_Mul
                return classes.Mul(*[Pow(b, item) for item in e])
            return Pow(b, e)
        return self

    def try_derivative(self, s):
        b,e = self.args
        dbase = b.diff(s)
        dexp = e.diff(s)
        if dexp is zero:
            dt = b**(e-1) * dbase * e
        else:
            dt = b**e * (dexp * classes.Log(b) + dbase * e/b)
        return dt

    def try_power(self, other):
        if other.is_Number:
            if other.is_Integer:
                return Pow(self.base, self.exponent * other)
            if self.exponent.is_Number and self.base.is_Number:
                if self.base.is_positive:
                    return Pow(self.base, self.exponent * other)

    def iterPow(self):
        return itertools.chain(self.base.iterPow(), iter([self.exponent]))

    def as_base_exponent(self):
        return self.base, self.exponent

    def matches(pattern, expr, repl_dict={}):
        wild_classes = (classes.Wild, classes.WildFunctionType)
        if not pattern.atoms(type=wild_classes):
            return Basic.matches(pattern, expr, repl_dict)
        pb, pe = pattern.args
        if expr.is_Number:
            r = (pe * classes.Log(pb)).matches(classes.Log(expr), repl_dict)
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

    def __new__(cls, b, e=None):
        if e is None:
            return Pow.__new__(cls, b, half)
        assert e is half,`e`
        return Pow.__new__(cls, b, e)

    @classmethod
    def canonize(cls, (base, exponent), options):
        if base is E:
            return classes.Exp(exponent)
        if base is one:
            return base
        if options.get('normalized', True):
            return base.try_power(exponent)
        return


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

from operations import TermCoeffDict
