from ..core.utils import memoizer_immutable_args
from ..core import Basic, Atom, sympify, objects
from .methods import NumberMethods

from .basic import BasicArithmetic

Basic.is_zero = None
Basic.is_one = None
Basic.is_half = None
Basic.is_two = None
Basic.is_even = None
Basic.is_odd = None
Basic.is_negative = None
Basic.is_positive = None
Basic.is_nonnegative = None
Basic.is_nonpositive = None
Basic.is_real = None
Basic.is_integer = None
Basic.is_rational = None
Basic.is_finite = None
Basic.is_bounded = None
Basic.is_commutative = None
Basic.is_prime = None

class Number(BasicArithmetic, Atom):
    """A Number is an atomic object with a definite numerical value
    that gives a Number when added or multiplied to another Number.
    Examples include rational numbers (-25, 2/3, ...) via the Rational
    class and floating-point numbers via the Float class."""

    is_negative = None
    is_positive = None
    is_finite = True
    is_bounded = True
    is_commutative = True
    
    def __new__(cls, x, **options):
        if isinstance(x, Basic): return x
        if isinstance(x, (int, long)): return Integer(x, **options)
        return Basic.__new__(cls, x, **options)

    @property
    def as_Interval(self):
        if self.is_Interval: return self
        return Interval.make(self, self)

    @property
    def as_Float(self):
        if self.is_Float: return self
        if self.is_Interval: return self.mid.as_Float
        if self.is_Rational: return Float.make_from_fraction(self.p, self.q)
        raise NotImplementedError(`self`)

    @property
    def as_Fraction(self):
        if self.is_Fraction: return self
        if self.is_Integer: return Fraction.make(self.p, self.q)
        if self.is_Float: return Fraction.make_from_man_exp(self.man, self.exp)
        if self.is_Interval: return self.mid.as_Fraction
        raise NotImplementedError(`self`)

    @property
    def as_Integer(self):
        if self.is_Integer: return self
        raise NotImplementedError(`self`)

    @memoizer_immutable_args('Number.try_power')
    def try_power(self, other):
        r = self.__pow__(other)
        if r is not NotImplemented:
            return r
        if other.is_Number:
            s = eval('self.as_%s' % (other.__class__.__name__))
            r = s.__pow__(other)
            if r is not NotImplemented:
                return r
        return

    def try_derivative(self, s):
        return Basic.zero

    def __call__(self, *args):
        """ Number as a constant function.
        (n)(x) -> n
        """
        return self

    def fdiff(self, index=1):
        return Basic.zero

    def as_coeff_term(self):
        return self, Basic.Integer(1)

    def as_term_coeff(self):
        return Basic.Integer(1), self

class Real(Number):

    """
    The implementation of a floating point number must
    derive from Real class and have the methods defined
    in the following template class:
    
    class Float(Real, <floating point implementation class>):

        def __new__(cls, f):
            if isinstance(f, Basic):
                return f.evalf()
            # f can be python int/long, float, str and
            # any other object that the implementation
            # can handle.
            obj = <floating point implementation class>.__new__(cls,..)
            return obj

        def __float__(self):
            return <python float instance>

        def __int__(self):
            return <python int instance>
    """
    is_real = True

    def __new__(cls, f):
        return Float(f)

    @property
    def is_nonpositive(self):
        return self.is_negative or self.is_zero

    @property
    def is_nonnegative(self):
        return self.is_positive or self.is_zero

    def __nonzero__(self):
        return self!=0

class Rational(Real):

    """ Base class for Integer and Fraction.
    
    Rational subclasses must define attributes p and q that
    hold integer instances of numerator and denominator.

    The type of p and q must support arithmetics and comparsions
    with python integer types and they should return instances
    of integer implementation classes.

    Integer must define staticmethod gcd(a,b) and probably
    also redefine __int__,__long__,__float__ methods.
    """

    is_rational = True

    def __new__(cls, p, q=1):
        return Fraction(p, q)

    def torepr(self):
        p = repr(self.p)
        if p.endswith('L'): p = p[:-1]
        q = repr(self.q)
        if q.endswith('L'): q = q[:-1]
        if self.q==1:
            return '%s(%s)' % (self.__class__.__name__, p)
        return '%s(%s, %s)' % (self.__class__.__name__, p, q)

    def tostr(self, level=0):
        p = str(self.p)
        if p.endswith('L'): p = p[:-1]
        q = str(self.q)
        if q.endswith('L'): q = q[:-1]
        if self.q==1:
            return p
        r = '%s/%s' % (p, q)
        if self.precedence<=level:
            r = '(%s)' % (r)
        return r

    @property
    def precedence(self):
        if self.q==1:
            return Basic.Atom_precedence
        return Basic.Mul_precedence

    @property
    def is_positive(self):
        return self.p > 0

    @property
    def is_negative(self):
        return self.p < 0

    def instance_compare(self, other):
        return cmp(self.p*other.q, self.q*other.p) 

    def __eq__(self, other):
        other = sympify(other)
        if self is other: return True
        return self.p*other.q==self.q*other.p

    def evalf(self):
        return Basic.Float(self.p) / Basic.Float(self.q)

    def __int__(self):
        return int(self.p // self.q)

    def __long__(self):
        return long(self.p // self.q)

    def __float__(self):
        return float(self.evalf())

    def as_factors(self, expand=False):
        dp = Integer.factor_trial_division(self.p)
        dq = Integer.factor_trial_division(self.q)
        eb = {}
        for (b,e) in dp.items():
            eb[e] = Integer(b)
        for (b,e) in dq.items():
            eb[e] = Fraction(eb.get(e,1),b)
        if len(eb)>1 and eb.get(1)==1:
            del eb[1]
        return [(b,Integer(e)) for (e,b) in eb.items()]

    def as_terms(self, expand=False):
        return [(Integer(1), self)]
        
from .integer import Integer
from .fraction import Fraction
from .float import Float
from .interval import Interval

Basic.one = Integer(1)
Basic.zero = Integer(0)

objects.one = Integer(1)
objects.zero = Integer(0)
