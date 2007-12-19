
from ..core import Basic, BasicType, classes, objects, sympify
from ..core.utils import UniversalMethod
from .methods import ArithmeticMethods

__all__ = ['BasicArithmetic']

class BasicArithmetic(ArithmeticMethods, Basic):
    """ Defines default methods for arithmetic classes.
    """

    def try_power(self, exponent):
        """ Try evaluating power self ** exponent.
        Return None if no evaluation is carried out.
        Caller code must ensure that exponent is
        a Basic instance.
        """
        return

    def expand(self, *args, **kwargs):
        """Expand an expression based on different hints. Currently
           supported hints are basic, power, complex, trig and func.
        """
        return self

    def split(self, cls=None):
        if cls is None:
            cls = self.__class__
        if cls is classes.Add:
            return (cls, self.iterAdd())
        if cls is classes.Mul:
            return (cls, self.iterMul())
        if cls is classes.Pow:
            return (cls, self.iterPow())
        raise TypeError('Expressions can be split only with respect to Add, Mul, Pow classes, got %s' % (cls.__name__))

    @UniversalMethod
    def fdiff(obj, index=1):
        """ Return derivative function with respect to index-th argument.
        """
        assert not isinstance(obj, BasicType),`obj`
        return classes.Number(0)

    def try_derivative(self, s):
        if not self.has(s):
            return objects.zero
        return None

    def try_antiderivative(self, s):
        if not self.has(s):
            return self * s
        return None

    def diff(self, *symbols):
        """ Return derivative with respect to symbols. If symbols contains
        positive integer then differentation is repeated as many times as
        is the value with respect to preceding symbol in symbols.
        """
        new_symbols = []
        for s in symbols:
            s = sympify(s)
            if isinstance(s, classes.Integer) and new_symbols and s.is_positive:
                last_s = new_symbols.pop()
                new_symbols += [last_s] * int(s)
            elif isinstance(s, classes.Symbol):
                new_symbols.append(s)
            else:
                raise TypeError(".diff() argument must be Symbol|Integer instance (got %s)"\
                                % (s.__class__.__name__))
        return classes.Derivative(self, *new_symbols)

    def integrate(self, *symbols):
        return classes.Integral(self, *symbols)

    def iterAdd(self):
        return iter([self])

    def iterMul(self):
        return iter([self])

    def iterPow(self):
        return iter([self])

    def iterLogMul(self):
        iterator = self.iterBaseExp()
        def itercall():
            b,e = iterator.next()
            if e.is_one:
                return classes.Log(b)
            return e * classes.Log(b)
        return iter(itercall, False)

    def iterTermCoeff(self):
        return iter([self.as_term_coeff()])

    def iterBaseExp(self):
        return iter([self.as_base_exponent()])

    def match(self, pattern):
        pattern = sympify(pattern)
        if isinstance(pattern, bool): return
        return pattern.matches(self, {})

    def as_base_exponent(self):
        """ Return (b,e) such that self==b**e.
        """
        return self, classes.Integer(1)

    def as_term_coeff(self):
        """ Return (t,c) such that self==c*t.
        """
        return self, classes.Integer(1)

    def try_get_coefficient(self, expr):
        """
        Extracts symbolic coefficient at the given expression. In
        other words, this functions separates 'self' into product
        of 'expr' and 'expr'-free coefficient. If such separation
        is not possible it will return None.
        """
        expr = sympify(expr)
        if isinstance(expr, classes.Add): return
        w = classes.Wild()
        coeff = self.match(w * expr)
        if coeff is not None:
            coeff = coeff[w]
        return coeff

    def as_coeff_term(self):
        """ Return (c,t) such that self==c*t and c is Rational.
        """
        t,c = self.as_term_coeff()
        return c,t
