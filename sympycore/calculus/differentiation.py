""" Provides the implementation of differentation methods.
"""
__docformat__ = "restructuredtext"
__all__ = ['diff']

from ..core import init_module

init_module.import_heads()
init_module.import_numbers()
init_module.import_lowlevel_operations()

from ..basealgebra import Algebra
from .algebra import Calculus, algebra_numbers, zero, one
from .functions import Log

cache_generic = {}
cache_factors = {}

def is_integer(expr):
    head, data = expr.pair
    return head is NUMBER and isinstance(data, inttypes)

def is_constant(expr, xdata):
    return xdata not in expr.symbols_data

def is_constant_exponent(exp, xdata):
    return isinstance(exp, algebra_numbers) or is_constant(exp, xdata)

monomial_msg = ("symbolic or fractional differentiation of a monomial (requires"
    "symbolic gamma or Pochhammer, with conditions")

# This is generally slow, so we try to avoid it when shortcuts
# are available for high-order derivatives
def diff_repeated(expr, xdata, order):
    if not is_integer(order):
        raise NotImplementedError('symbolic differentiation of %s' % expr)
    for k in xrange(order.data):
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
        arg = arg[1]
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
                    for i in xrange(order.data):
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
    elif xdata not in base.symbols_data:
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
                d1 = Calculus(BASE_EXP_DICT, dict(args[:i] + args[i+1:]))
                s += dt * d1
        return diff_repeated(s, xdata, order-1)

def diff_generic(expr, xdata, order):
    key = (expr, xdata, order)
    c = cache_generic.get(key)
    if c is not None:
        return c
    head, data = expr.pair
    if xdata not in expr.symbols_data:
        return zero
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
    elif head is TERM_COEFF_DICT:
        # Differentiate term by term. Note that coefficients are constants.
        s = zero
        cls = type(expr)
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
                        s += coeff
                # else: zero
                continue
            if th is BASE_EXP_DICT:
                dterm = diff_product(td, xdata, order)
            # General case
            else:
                dterm = diff_generic(term, xdata, order)
            s += dterm * coeff
        r = s
    elif head is TERM_COEFF:
        term, coeff = data
        return diff_generic(term, xdata, order) * coeff
    elif head is BASE_EXP_DICT:
        r = diff_product(data, xdata, order)
    elif head is POW:
        base, exp = data
        r = diff_factor(base, exp, xdata, order)
    elif head is ADD:
        r = zero
        for op in data:
            dop = diff_generic(op, xdata, order)
            if dop==0:
                continue
            r += dop
        return r
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

def diff(expr, symbol, order=1):
    if order==0:
        return expr
    cls = type(expr)
    if type(symbol) is cls:
        symbol = symbol.data
    elif isinstance(symbol, str):
        pass
    else:
        raise TypeError('diff(symbol, order) first argument must be str or %s instance but got %s instance' % (cls.__name__, type(symbol).__name__))
    try:
        cache = {}
        result = expr.head.diff(cls, expr.data, expr, symbol, order, cache=cache)
    finally:
        cache.clear()
    return result

