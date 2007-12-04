
import itertools
from ..core import Basic, sympify, objects, classes
from .basic import BasicArithmetic
from .function import Function, FunctionSignature

__all__ = ['Pow', 'Log', 'Root', 'Sqrt', 'Exp', 'Ln', 'Lg', 'Lb']

one = objects.one
zero = objects.zero
oo = objects.oo
zoo = objects.zoo
nan = objects.nan
E = objects.E
half = objects.half

def _is_negative(x):
    if x.is_Number:
        return x.is_negative
    if x.is_Mul:
        return _is_negative(x[0])

class Pow(Function):
    """ Represents an evaluated exponentation operation.

    Pow(base, exponent) == base ** exponent    
    """

    signature = FunctionSignature((BasicArithmetic, BasicArithmetic),
                                  (BasicArithmetic,))
    
    @classmethod
    def canonize(cls, (base, exponent), options):
        if exponent is zero:
            return one
        if exponent is one:
            return base
        if base is one:
            return base
        if not options.get('normalized', True):
            return
        if exponent.is_Log and base==exponent.base:
            return exponent.logarithm

        excluded = []
        included = []
        for a in exponent.iterAdd():
            it = a.iterMul()
            cs = []
            b = None
            for f in it:
                if f.is_Log and f.base==base:
                    excluded.append(f.args[0] ** classes.Mul(*(cs+list(it))))
                    break
                cs.append(f)
            else:
                included.append(a)
        if excluded:
            if included:
                return classes.Mul(*(excluded+[cls(classes.Add(*included))]))
            else:
                return classes.Mul(*excluded)

        return base.try_power(exponent)

    @classmethod
    def fdiff1(cls):
        e = Dummy('e')
        b = Dummy('b')
        return Lambda((b,e),e/b) * Pow

    @classmethod
    def fdiff2(cls):
        e = Dummy('e')
        b = Dummy('b')
        return Lambda((b,e),Ln(e)) * Pow

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


class Root(Function):
    """ Root(b,e) is the inverse of Pow with respect to the first argument:
      Pow(Root(b, e), e) -> e.

    Root represents the principal part of the root.
    """
    signature = FunctionSignature((BasicArithmetic, BasicArithmetic),
                                  (BasicArithmetic,))

    def __new__(cls, base, arg):
        return Pow(base, one/arg)

    @classmethod
    def fdiff1(cls):
        e = classes.Dummy('e')
        b = classes.Dummy('b')
        return classes.Lambda((b,e),Root(b, e/(1-e))/e)


class Log(Function):
    """ Log(x, base=E) is inverse of Pow with respect to the second argument:
      Pow(b, Log(l, b)) -> l

    Log represents the principal part of the logarithm.

    References:
      http://en.wikipedia.org/wiki/Logarithm
    """

    signature = FunctionSignature((BasicArithmetic, BasicArithmetic),
                                  (BasicArithmetic,))

    def __new__(cls, arg, base=E):
        # abs(base) must be non-zero and non-one
        return Function.__new__(cls, arg, base)

    @property
    def logarithm(self):
        return self.args[0]

    @property
    def base(self):
        return self.args[1]

    @classmethod
    def canonize(cls, (arg, base)):
        if arg.is_one:
            return zero
        if arg==base:
            return one
        if _is_negative(base):
            return cls(arg, -base) / (one + pi * I * cls(E, -base))
        if _is_negative(arg):
            return objects.pi * objects.I * cls(E, base) + cls(-arg, base)
        if arg.is_NaN or arg.is_Infinity:
            return arg
        if arg.is_zero:
            return objects.moo
        return

    @classmethod
    def fdiff1(cls):
        x = classes.Dummy('x')
        b = classes.Dummy('b')
        return classes.Lambda((x,b),Log(E,b)/x)

    @classmethod
    def fdiff2(cls):
        x = classes.Dummy('x')
        b = classes.Dummy('b')
        return classes.Lambda((x,b),-Log(x,b)*Log(E,b)/b)

    def matches(pattern, expr, repl_dict={}):
        if expr.is_Log:
            d = pattern.base.matches(expr.base, repl_dict)
            if d is not None:
                return pattern.logarithm.matches(expr.logarithm, d)
            d = pattern.logarithm.matches(expr.logarithm, repl_dict)
            return pattern.base.matches(expr.base, d)
        if expr.is_Add and len(expr)==1:
            # Log(p, base).matches(4*Log(x, base)) -> p.matches(x**4)
            term, coeff = expr.items()[0]
            if term.is_Log and term.base==pattern.base and coeff.is_Integer:
                return pattern.args[0].matches(term.args[0]**coeff, repl_dict)
        if expr.is_Number:
            return pattern.args[0].matches(Pow(pattern.base, expr), repl_dict)
        if pattern.args[0].is_Wild:
            return pattern.args[0].matches(Pow(pattern.base, expr), repl_dict)


class Ln(Function):
    """ Ln(x) is Log(x, E).
    """

    signature = FunctionSignature((BasicArithmetic,),
                                  (BasicArithmetic,))

    def __new__(cls, arg):
        return Log(arg, E)

    @classmethod
    def fdiff1(cls):
        x = classes.Dummy('x')
        return classes.Lambda(x,1/x)

class Lg(Function):
    """ Lg(x) is Log(x, 10).
    """

    signature = FunctionSignature((BasicArithmetic,),
                                  (BasicArithmetic,))

    def __new__(cls, arg):
        return Log(arg, 10)

    @classmethod
    def fdiff1(cls):
        x = classes.Dummy('x')
        return classes.Lambda(x,Log(E,10)/x)

class Lb(Function):
    """ Lb(x) is Log(x, 2).
    """

    signature = FunctionSignature((BasicArithmetic,),
                                  (BasicArithmetic,))

    def __new__(cls, arg):
        return Log(arg, 2)

    @classmethod
    def fdiff1(cls):
        x = classes.Dummy('x')
        return classes.Lambda(x,Log(E,2)/x)


class Exp(Function):
    """ Exp(x) is Pow(E, x).

    References:
      http://en.wikipedia.org/wiki/Exponential_function
    """

    signature = FunctionSignature((BasicArithmetic,),
                                  (BasicArithmetic,))

    def __new__(cls, arg):
        return Pow(E, arg)

    @classmethod
    def fdiff1(cls):
        return cls

class Sqrt(Function):
    """ Sqrt(x) is Root(x, 2).
    """

    signature = FunctionSignature((BasicArithmetic,),
                                  (BasicArithmetic,))

    def __new__(cls, arg):
        return Root(arg, 2)

    @classmethod
    def fdiff1(cls):
        x = classes.Dummy('x')
        return classes.Lambda(x, half/Sqrt(x))


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
