""" Provides the implementation of differentation methods.
"""
__docformat__ = "restructuredtext"
__all__ = ['diff']

from ..utils import SYMBOL, NUMBER, FACTORS, TERMS
from ..heads import APPLY, CALLABLE
from ..arithmetic.numbers import inttypes
from ..basealgebra import Algebra
from ..basealgebra.pairs import inplace_add2, inplace_add, return_terms
from .algebra import Calculus, algebra_numbers, zero, one
from .functions import Log

cache_generic = {}
cache_factors = {}

def is_integer(expr):
    return expr.is_Number and isinstance(expr.data, (int, long))

def is_constant(expr, xdata):
    return xdata not in expr._get_symbols_data()

def is_constant_exponent(exp, xdata):
    return isinstance(exp, algebra_numbers) or (xdata not in exp._get_symbols_data())

monomial_msg = ("symbolic or fractional differentiation of a monomial (requires"
    "symbolic gamma or Pochhammer, with conditions")

# This is generally slow, so we try to avoid it when shortcuts
# are available for high-order derivatives
def diff_repeated(expr, xdata, order):
    if not is_integer(order):
        raise NotImplementedError('symbolic differentiation of %s' % expr)
    for k in xrange(order):
        expr = diff_generic(expr, xdata, one)
        if expr == zero:
            break
    return expr

def partial_derivative(func, n):
    if isinstance(func, Algebra):
        dname = '%s_%s' % (func, n)
    else:
        dname = '%s_%s' % (func.__name__, n)
    def dfunc(*args):
        raise NotImplementedError('%s%s' % (dname, str(args)))
    dfunc.__name__ = dname
    return dfunc

def diff_callable(f, arg, xdata, order):
    if f is APPLY:
        h, d = arg[0].pair
        assert h is CALLABLE,`f, arg` # todo: support for symbolic functions
        f = d
        arg = arg[1:]
        if len(arg)==1:
            arg = arg[0]
        else:
            arg = tuple(arg)

    if order != 1:
        # D^n f(a*x+b) -> a**n * [D^n f](a*x+b)]
        if hasattr(f, 'nth_derivative'):
            a = diff_generic(arg, xdata, one)
            if a == zero:
                return zero
            if is_constant(a, xdata):
                return a**order * f.nth_derivative(arg, order)
        raise NotImplementedError(`f,arg`)
    if type(arg) is tuple:
        terms = []
        for i, a in enumerate(arg):
            da = diff_generic(a, xdata, one)
            if da == zero:
                continue
            df = Calculus.Apply(partial_derivative(f, i+1), *arg)
            terms.append(da * df)
        return Calculus.Add(*terms)
    da = diff_generic(arg, xdata, one)
    if da == zero:
        return zero
    if hasattr(f, 'derivative'):
        return diff_repeated(da * f.derivative(arg), xdata, order-1)
    df = Calculus.Apply(partial_derivative(f, one), arg)
    return df * da

def diff_factor(base, exp, xdata, order):
    key = (base, exp, order)
    c = cache_factors.get(key)
    if c is not None:
        return c
    # Handle f(x)**r where r is constant
    if is_constant_exponent(exp, xdata):
        # Generalized monomials x**r
        head, data = base.pair
        if head is SYMBOL:
            # Note: this shouldn't be reached, but just to be sure...
            if data != xdata:
                res = zero
            elif order == one:
                res = exp * base**(exp-1)
            # Don't waste time if someone tries to calculate the 1 millionth
            # derivative of x**3
            elif is_integer(order):
                if isinstance(exp, inttypes) and exp > 0 and order > exp:
                    res = zero
                # Repeatedly apply D(x**r) = r * x**(r-1)
                # (Could be calculated for symbolic orders using Pochhammer.)
                else:
                    p = 1
                    for i in xrange(order):
                        p *= exp
                        exp -= 1
                    res = p * base ** exp
            else:
                raise NotImplementedError(monomial_msg)
        # f(x)**r
        else:
            d = exp * base**(exp-1) * diff_generic(base, xdata, one)
            res = diff_repeated(d, xdata, order-1)
    # Handle a**f(x) where a is constant
    elif xdata not in base._get_symbols_data():
        # a**x
        if exp.head is SYMBOL:
            # Should not happen
            if exp.data != xdata:
                res = zero
            else:
                res = base**exp * Log(base)**order
        # a**f(x)
        else:
            de = diff_generic(exp, xdata, one)
            # Special case:
            # D^n a**(b*x+c) = a**(b*x+c) * b**n * log(a)**10
            if is_constant(de, xdata):
                res = base**exp * de**order * Log(base)**order
            else:
                # TODO: maybe use the formula http://functions.wolfram.com/..
                # ..ElementaryFunctions/Power/20/02/01/0003/ for high order
                d = base**exp * Log(base) * de
                res = diff_repeated(d, xdata, order-1)
    # General case, f(x)**g(x)
    else:
        db = diff_generic(base, xdata, one)
        de = diff_generic(exp, xdata, one)
        res = diff_repeated(base**exp * (exp*db / base + Log(base)*de), xdata, order-1)
    cache_factors[key] = res
    return res

def diff_product(pairs, xdata, order=one):
    l = len(pairs)
    args = pairs.items()
    if l == 1:
        base, exp = args[0]
        return diff_factor(base, exp, xdata, order)
    if l == 2:
        b1, e1 = args[0]
        b2, e2 = args[1]
        dt1 = diff_factor(b1, e1, xdata, one)
        dt2 = diff_factor(b2, e2, xdata, one)
        if e1 == 1: t1 = b1
        else:       t1 = b1 ** e1
        if e2 == 1: t2 = b2
        else:       t2 = b2 ** e2
        return diff_repeated(t1*dt2 + t2*dt1, xdata, order-1)
    else:
        s = zero
        for i in xrange(l):
            b, e = args[i]
            dt = diff_factor(b, e, xdata, one)
            if dt != zero:
                d1 = Calculus(FACTORS, dict(args[:i] + args[i+1:]))
                s += dt * d1
        return diff_repeated(s, xdata, order-1)

def diff_generic(expr, xdata, order, NUMBER=NUMBER, SYMBOL=SYMBOL, TERMS=TERMS, FACTORS=FACTORS):
    key = (expr, xdata, order)
    c = cache_generic.get(key)
    if c is not None:
        return c
    if xdata not in expr._get_symbols_data():
        return zero
    head, data = expr.pair
    if head is NUMBER:
        if is_integer(order):
            r = zero
        else:
            raise NotImplementedError(monomial_msg)
    elif head is SYMBOL:
        if data == xdata and order == one:
            r = one
        elif is_integer(order):
            r = zero
        else:
            raise NotImplementedError(monomial_msg)
    elif head is TERMS:
        # Differentiate term by term. Note that coefficients are constants.
        s = zero
        d = {}
        cls = type(expr)
        d_get = d.get
        for term, coeff in data.iteritems():
            # Inline common cases
            th, td = term.pair
            if th is NUMBER:
                continue
            elif th is SYMBOL:
                if td == xdata:
                    if not is_integer(order):
                        raise NotImplementedError(monomial_msg)
                    if order == one:
                        inplace_add(cls, coeff, d, d_get, one)
                # else: zero
                continue
            if th is FACTORS:
                dterm = diff_product(term.data, xdata, order)
            # General case
            else:
                dterm = diff_generic(term, xdata, order)
            inplace_add2(cls, dterm, coeff, d, d_get, one)
        r = return_terms(cls, d)
    elif head is FACTORS:
        r = diff_product(data, xdata, order)
    else:
        r = diff_callable(head, data, xdata, order)
    cache_generic[key] = r
    return r


def diff(expr, symbol, order=one):
    """ Return derivative of the expression with respect to symbols.

    Examples::

      expr.diff(x,y) - 2nd derivative with respect to x and y
      expr.diff(x,4) is equivalent to expr.diff(x,x,x,x).
    """
    expr = Calculus.convert(expr)
    symbol = Calculus.convert(symbol)
    order = Calculus.convert(order)
    try:
        if not order:
            return expr
        return diff_generic(expr, symbol.data, order)
    finally:
        #print len(cache)
        cache_generic.clear()
        cache_factors.clear()
