
import itertools
from ..core import Basic, sympify, objects, classes, instancemethod, sexpr
from ..core.function import new_function_value
from .basic import BasicArithmetic
from .function import Function, FunctionSignature
from ..core.sexpr import LOGFUNC
from .sexpr import FACTORS, s_toBasic, s_power, s_expand, s_mul_sequence, s_add_sequence, s_mul, TERMS

__all__ = ['Pow', 'Log', 'Root', 'Sqrt', 'Exp', 'Ln', 'Lg', 'Lb']

one = objects.one
zero = objects.zero
oo = objects.oo
zoo = objects.zoo
nan = objects.nan
E = objects.E
half = objects.half

def _is_negative(x):
    if isinstance(x, (classes.Number, classes.MathematicalSymbol)):
        return x.is_negative
    if isinstance(x, classes.Mul):
        term, coeff = x.as_term_intcoeff()
        return _is_negative(coeff)

class Pow(Function):
    """ Represents an evaluated exponentation operation.

    Pow(base, exponent) == base ** exponent    
    """

    signature = FunctionSignature((BasicArithmetic, BasicArithmetic),
                                  (BasicArithmetic,))

    def __new__(cls, base, exponent, **options):
        if 'sexpr' in options:
            # XXX: rename sexpr to arithmetic_sexpr as there will be logical_symbol_expr, logical_set_expr
            # Pow is called in canonical form: Pow(<base>, <exp>, sexpr=<sexpr>)
            # exponent may be Python int:
            return new_function_value(cls, (base, exponent), options)
        base, exponent = sympify(base), sympify(exponent)
        obj = cls.canonize((base, exponent), options)
        if obj is not None:
            return obj
        return new_function_value(cls, (base, exponent), options)

    @classmethod
    def canonize(cls, (base, exponent), options):
        """ Canonize exponentiation operation.
        
        The following rules are applied:

          anything ** 0 -> 1
          anything ** 1 -> anything
          1 ** anything -> 1

          E ** Log(anything, E) -> anything
          (x * y) ** integer -> x**integer * y**integer
          (number * x) ** (number) -> number**number * x **number
          
          E**(y + number*Log(x, E)) -> E**y * x**number

        The following rules are applied by the as_sexpr method:
          x ** (integer + integer * y) -> (x**(1 + y)) ** integer
          x ** (integer * y) -> (x**y) ** integer

        """
        if exponent is zero:
            return one
        if exponent is one:
            return base
        if base is one:
            return base
        if not options.get('normalized', True):
            return
        if isinstance(exponent, classes.Log) and base==exponent.base:
            return exponent.logarithm
        if isinstance(base, classes.Mul) or base is objects.I:
            if isinstance(exponent, classes.Integer):
                return s_toBasic(s_power(base.as_sexpr(), exponent))
            if isinstance(exponent, classes.Number):
                term, coeff = base.as_term_coeff()
                if coeff is not one:
                    return term ** exponent * coeff ** exponent

        s_exp = exponent.as_sexpr()
        if s_exp[0] is TERMS:
            # handle b ** (y + r*Log(x, b)) -> b**y * x**r, where r is Number
            exp_log_list = []
            rest = []
            for t, c in s_exp[1]:
                if t[0] is LOGFUNC and t[1].base==base:
                    exp_log_list.append((t[1].logarithm, c))
                else:
                    rest.append((t,c))
            if exp_log_list:
                a = s_add_sequence(rest)
                b = Pow(base, s_toBasic(a)).as_sexpr()
                c = s_toBasic(s_mul_sequence([b]+[Pow(t,c).as_sexpr() for t,c in exp_log_list]))
                return c

        term, coeff = exponent.as_term_coeff()
        if coeff is not one:
            if isinstance(coeff, classes.Integer):
                # x ** (2*y) -> (x**y) ** 2
                new_base = base ** term
                return s_toBasic(s_power(new_base.as_sexpr(), coeff))

            t, c = coeff.as_term_intcoeff()
            if c is not one:
                # x ** (2/3*y) -> (x**(1/3*y)) ** 2
                new_base = base ** (t * term)
                return s_toBasic(s_power(new_base.as_sexpr(), c))
            
        if options.get('try_pow', True):
            # to prevent recursion, __pow__ should call Pow with try_pow=False 
            return base ** exponent
        return

    @instancemethod(Function.as_sexpr)
    def as_sexpr(self, context=sexpr.ARITHMETIC):
        if context==sexpr.ARITHMETIC:
            expr = self.options.get('sexpr')
            if expr is not None:
                return expr
            self.options['sexpr'] = expr = Basic.as_sexpr(self, context=None)
            return expr
        return Basic.as_sexpr(self, context=None)

    @classmethod
    def fdiff1(cls):
        e = classes.Dummy('e')
        b = classes.Dummy('b')
        return classes.Lambda((b,e),e/b) * Pow

    @classmethod
    def fdiff2(cls):
        e = classes.Dummy('e')
        b = classes.Dummy('b')
        return classes.Lambda((b,e),Ln(e)) * Pow

    @property
    def base(self):
        return self.args[0]

    @property
    def exponent(self):
        return self.args[1]

    @property
    def precedence(self):
        return Basic.Pow_precedence

    @instancemethod(Function.tostr)
    def tostr(self, level=0):
        p = self.precedence
        base, exp = self.as_base_exponent()
        b = base.tostr(p)
        e = exp.tostr(p)
        r = '%s**%s' % (b, e)
        if p<=level:
            r = '(%s)' % r
        return r
    
    def expand(self, **hints):
        if hints.get('basic', True):
            return s_toBasic(s_expand(self.as_sexpr()))
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

    def try_antiderivative(self, s):
        b, e = self.args
        if b==s and not e.has(s):
            return s**(e+1)/(e+1)
        if e==s and not b.has(s):
            return self/Log(b,E)

    @instancemethod(Function.try_power)
    def try_power(self, other):
        if isinstance(other, classes.Number):
            if isinstance(other, classes.Integer):
                return Pow(self.base, self.exponent * other)
            if isinstance(self.exponent, classes.Number) and isinstance(self.base, classes.Number):
                if self.base.is_positive:
                    return Pow(self.base, self.exponent * other)

    def iterPow(self):
        return itertools.chain(self.base.iterPow(), iter([self.exponent]))

    def as_base_exponent(self):
        base, exp = self.base, self.exponent
        if isinstance(base, Pow):
            if isinstance(exp, classes.Integer):
                exp = base.exponent * exp
                base = base.base
            elif isinstance(base.exponent, Integer):
                exp = base.exponent * exp
                base = base.base
        return base, exp

    @instancemethod(Function.matches)
    def matches(pattern, expr, repl_dict={}):
        wild_classes = (classes.Wild, classes.WildFunctionType)
        if not pattern.atoms(type=wild_classes):
            return Basic.matches(pattern, expr, repl_dict)
        pb, pe = pattern.args
        if isinstance(expr, classes.Number):
            r = (pe * classes.Log(pb)).matches(classes.Log(expr), repl_dict)
            return r
        b, e = expr.as_base_exponent()
        p1 = e/pe
        if isinstance(p1, classes.Integer):
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

    @instancemethod(Function.as_sexpr)
    def as_sexpr(self, context=sexpr.ARITHMETIC):
        if context==sexpr.ARITHMETIC:
            if 'sexpr' in self.options:
                return self.options['sexpr']
            return (LOGFUNC, self)
        return Basic.as_sexpr(self, context=None)

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
        if isinstance(arg, classes.NaN) or isinstance(arg, classes.Infinity):
            return arg
        if arg.is_zero:
            return objects.moo
        if isinstance(base, classes.EulersNumber):
            if arg is Exp:
                return one
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

    @instancemethod(Function.matches)
    def matches(pattern, expr, repl_dict={}):
        if isinstance(expr, classes.Log):
            d = pattern.base.matches(expr.base, repl_dict)
            if d is not None:
                return pattern.logarithm.matches(expr.logarithm, d)
            d = pattern.logarithm.matches(expr.logarithm, repl_dict)
            return pattern.base.matches(expr.base, d)
        if isinstance(expr, classes.Add) and len(expr)==1:
            # Log(p, base).matches(4*Log(x, base)) -> p.matches(x**4)
            term, coeff = expr.items()[0]
            if isinstance(term, classes.Log) and term.base==pattern.base and isinstance(coeff, classes.Integer):
                return pattern.args[0].matches(term.args[0]**coeff, repl_dict)
        if isinstance(expr, classes.Number):
            return pattern.args[0].matches(Pow(pattern.base, expr), repl_dict)
        if isinstance(pattern.args[0], classes.Wild):
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
