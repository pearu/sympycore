"""
Author: Pearu Peterson <pearu.peterson@gmail.com>
Created: 2006
"""

__all__ = ['Power']

from base import Symbolic, integer_types
from base import RelationalMethods, ArithmeticMethods, FunctionalMethods

class Power(RelationalMethods, ArithmeticMethods, FunctionalMethods,
            Symbolic):
    """ Represents power b ** e.
    """

    ###########################################################################
    #
    # Constructor methods
    #

    def __new__(cls, base, exponent):
        """
        Applies default rules:
          x ** 1 -> x
          x ** 0 -> 1
          x ** nan -> nan, x is not 0, 1
        
        (n*a*b)**m -> n**m * a ** m * b ** m, whenever m is integer
                    -> n**m * (a * b) ** m, if m is number
        """
        base = Symbolic(base)
        exponent = Symbolic(exponent)
        lambda_args = None
        if isinstance(base, Symbolic.Lambda):
            lambda_args = base.args
            base = base.expr
        if isinstance(exponent, Symbolic.Lambda):
            lambda_args, exponent = Symbolic.process_lambda_args(lambda_args, exponent)
            
        if isinstance(exponent, Symbolic.One):
            result = base
        elif isinstance(exponent, Symbolic.Zero):
            result = Symbolic.One()
        else:
            result = base.eval_power(exponent)
        if result is None:
            if isinstance(exponent, Symbolic.NaN):
                result = Symbolic.NaN()
            else:
                result = Symbolic.__new__(cls, base, exponent)
        if lambda_args is None:
            return result
        return Symbolic.Lambda(*(lambda_args+(result,)))

    def astuple(self):
        return (self.__class__.__name__, self.base, self.exponent)

    def eval_power(base, exponent):
        """
        exponent is symbolic object but not equal to 0, 1

        a ** n ** m -> a ** (n*m), n, m are numbers
        (n * a) ** m -> n**m * a ** m, n,m are numbers
        """
        if isinstance(exponent, Symbolic.Number):
            if isinstance(base.exponent, Symbolic.Number):
                return Power(base.base, base.exponent * exponent)
        if isinstance(base, Symbolic.Mul):
            if isinstance(base.coeff, Symbolic.Number):
                if not isinstance(base.coeff, Symbolic.One):
                    return base.coeff ** exponent * Symbolic.Mul(*base.seq) ** exponent
        return

    def init(self, base, exponent):
        self.base = base
        self.exponent = exponent
        return

    ############################################################################
    #
    # Informational methods
    #
       
    def get_precedence(self): return 60

    ###########################################################################
    #
    # Transformation methods
    #

    def tostr(self, level=0):
        precedence = self.get_precedence()
        r = '%s ** %s' % (self.base.tostr(precedence),self.exponent.tostr(precedence))
        if precedence<=level:
            return '(%s)' % (r)
        return r
        
    def calc_expanded(self):
        """
        (a*b)**n -> a**n * b**n
        (a+b+..) ** n -> a**n + n*a**(n-1)*b + .., n is positive integer
        """
        base = self.base.expand()
        exponent = self.exponent.expand()
        result = base ** exponent
        if isinstance(result, Power):
            base = result.base
            exponent = result.exponent
        else:
            return result
        if isinstance(exponent, Symbolic.Integer):
            if isinstance(base, Symbolic.Mul):
                return Symbolic.Mul([t**exponent for t in base.astuple()[1:]])
            if exponent.is_positive() and isinstance(base, Symbolic.Add):
                ## Consider polynomial
                ##   P(x) = sum_{i=0}^n p_i x^k
                ## and its m-th exponent
                ##   P(x)^m = sum_{k=0}^{m n} a(m,k) x^k
                ## The coefficients a(m,k) can be computed using the J.C.P. Miller Pure Recurrence
                ## [see D.E.Knuth, Seminumerical Algorithms, The art of Computer
                ## Programming v.2, Addison Wesley, Reading, 1981;]:
                ##  a(m,k) = 1/(k p_0) sum_{i=1}^n p_i ((m+1)i-k) a(m,k-i),
                ## where a(m,0) = p_0^m.
                m = int(exponent)
                p = base.astuple()[1:]
                n = len(p)-1
                cache = {0: p[0] ** m}
                p0 = [t/p[0] for t in p]
                for k in range(1, m * n + 1):
                    a = []
                    for i in range(1,n+1):
                        if i<=k:
                            a.append(Symbolic.Mul(Symbolic.Rational((m+1)*i-k, k),
                                                  p0[i], cache[k-i]).expand())
                    cache[k] = Symbolic.Add(*a)
                return Symbolic.Add(*cache.values())
        return result

    def calc_diff(self, *args):
        if not args: return self.calc_diff
        if len(args)>1: return self.calc_diff(args[0]).diff(*args[1:])
        dbase = self.base.diff(*args)
        dexp = self.exponent.diff(*args)
        return self * (dexp * Symbolic.Log()(self.base) + dbase * self.exponent/self.base)

    def calc_integrate(self, *args):
        if not args: return self.calc_integral
        if len(args)>1: return self.calc_integrate(args[0]).integrate(*args[1:])
        a = args[0]
        if isinstance(a, Symbolic.Range):
            v = a.coeff
            if v not in self.exponent.free_symbols() and self.base.is_equal(v):
                n1 = self.exponent + Symbolic.One()
                return (a.seq[1]**n1 - a.seq[0]**n1)/n1
        else:
            v = a
            if v not in self.exponent.free_symbols() and self.base.is_equal(v):
                n1 = self.exponent + Symbolic.One()
                return (v**n1)/n1
        op = Symbolic.Integral(a)
        return Symbolic.Apply(op, self)

    ###########################################################################
    #
    # Comparison methods
    #

    def compare(self, other):
        if self is other: return 0
        c = self.compare_classes(other)
        if c: return c
        if isinstance(self.exponent, Symbolic.Number) and isinstance(other.exponent, Symbolic.Number):
            c = abs(self.exponent).compare(abs(other.exponent))
        else:
            c = self.exponent.compare(other.exponent)
        if c: return c
        return self.base.compare(other.base)

#
# End of Power class
#
################################################################################

Symbolic.Power = Power

#EOF
