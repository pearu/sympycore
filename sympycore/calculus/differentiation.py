from ..utils import SYMBOL, NUMBER, ADD, MUL
from ..arithmetic.numbers import inttypes
from .algebra import Calculus, algebra_numbers, zero, one
from .functions import log

cache_generic = {}
cache_factors = {}

def is_constant(expr, xdata):
    return xdata not in expr._get_symbols_data()

def is_constant_exponent(exp, xdata):
    return isinstance(exp, algebra_numbers) or (xdata not in exp._get_symbols_data())

# This is generally slow, so we try to avoid it when shortcuts
# are available for high-order derivatives
def diff_repeated(expr, xdata, order):
    for k in xrange(order):
        expr = diff_generic(expr, xdata, 1)
        if expr == 0:
            break
    return expr

def diff_callable(f, arg, xdata, order):
    if order != 1:
        # D^n f(a*x+b) -> a**n * [D^n f](a*x+b)]
        if hasattr(f, 'nth_derivative'):
            a = diff_generic(arg, xdata, 1)
            if a == zero:
                return zero
            if is_constant(a, xdata):
                return a**order * f.nth_derivative(arg, order)
        raise NotImplementedError
    if hasattr(f, 'derivative'):
        a = diff_generic(arg, xdata, 1)
        if a == zero:
            return zero
        return diff_repeated(a * f.derivative(arg), xdata, order-1)
    raise NotImplementedError

def diff_factor(base, exp, xdata, order):
    key = (base, exp, order)
    c = cache_factors.get(key)
    if c is not None:
        return c
    # Handle f(x)**r where r is constant
    if is_constant_exponent(exp, xdata):
        # Generalized monomials x**r
        if base.head is SYMBOL:
            # Note: this shouldn't be reached, but just to be sure...
            if base.data != xdata:
                res = zero
            elif order == 1:
                res = exp * base**(exp-1)
            # Don't waste time if some tries to calculate the 1 millionth
            # derivative of x**3
            elif isinstance(exp, inttypes) and exp > 0 and order > exp:
                res = zero
            # Repeatedly apply D(x**r) = r * x**(r-1)
            # (Could be calculated for symbolic orders using Pochhammer.)
            else:
                p = 1
                for i in xrange(order):
                    p *= exp
                    exp -= 1
                res = p * base ** exp
        # f(x)**r
        else:
            d = exp * base**(exp-1) * diff_generic(base, xdata, 1)
            res = diff_repeated(d, xdata, order-1)
    # Handle a**f(x) where a is constant
    elif xdata not in base._get_symbols_data():
        # a**x
        if exp.head is SYMBOL:
            # Should not happen
            if exp.data != xdata:
                res = zero
            else:
                res = base**exp * log(base)**order
        # a**f(x)
        else:
            de = diff_generic(exp, xdata, 1)
            # Special case:
            # D^n a**(b*x+c) = a**(b*x+c) * b**n * log(a)**10
            if is_constant(de, xdata):
                res = base**exp * de**order * log(base)**order
            else:
                # TODO: maybe use the formula http://functions.wolfram.com/..
                # ..ElementaryFunctions/Power/20/02/01/0003/ for high order
                d = base**exp * log(base) * de
                res = diff_repeated(d, xdata, order-1)
    # General case, f(x)**g(x)
    else:
        db = diff_generic(base, xdata, 1)
        de = diff_generic(exp, xdata, 1)
        res = diff_repeated(base**exp * (exp*db / base + log(base)*de), xdata, order-1)
    cache_factors[key] = res
    return res

def diff_product(pairs, xdata, order=1, NUMBER=NUMBER, SYMBOL=SYMBOL, ADD=ADD, MUL=MUL):
    l = len(pairs)
    args = pairs.items()
    if l == 1:
        base, exp = args[0]
        return diff_factor(base, exp, xdata, order)
    if l == 2:
        b1, e1 = args[0]
        b2, e2 = args[1]
        dt1 = diff_factor(b1, e1, xdata, 1)
        dt2 = diff_factor(b2, e2, xdata, 1)
        if e1 == 1: t1 = b1
        else:       t1 = b1 ** e1
        if e2 == 1: t2 = b2
        else:       t2 = b2 ** e2
        return diff_repeated(t1*dt2 + t2*dt1, xdata, order-1)
    else:
        s = zero
        for i in xrange(l):
            b, e = args[i]
            dt = diff_factor(b, e, xdata, 1)
            if dt != zero:
                d1 = Calculus(dict(args[:i] + args[i+1:]), head=MUL)
                s += dt * d1
        return diff_repeated(s, xdata, order-1)

def diff_generic(expr, xdata, order, NUMBER=NUMBER, SYMBOL=SYMBOL, ADD=ADD, MUL=MUL):
    key = (expr, xdata, order)
    c = cache_generic.get(key)
    if c is not None:
        return c
    if xdata not in expr._get_symbols_data():
        return zero
    head = expr.head
    data = expr.data
    if head is NUMBER:
        r = zero
    elif head is SYMBOL:
        if data == xdata and order == 1:
            r = one
        else:
            r = zero
    elif head is ADD:
        # Differentiate term by term. Note that coefficients are constants.
        # TODO: build dict on the spot
        s = zero
        for term, coeff in data.iteritems():
            # Inline common cases
            th = term.head
            td = term.data
            if th is NUMBER:
                continue
            elif th is SYMBOL:
                if td == xdata and order == 1:
                    s += coeff
                # else: zero
            elif th is MUL:
                s += coeff * diff_product(term.data, xdata, order)
            # General case
            else:
                s += coeff * diff_generic(term, xdata, order)
        r = s
    elif head is MUL:
        r = diff_product(data, xdata, order)
    else:
        r = diff_callable(head, data, xdata, order)
    cache_generic[key] = r
    return r

def diff(expr, symbol, order=1):
    # It should eventually be possible to support symbolic orders
    try:
        order = int(order)
        if not order:
            return expr
        return diff_generic(expr, symbol.data, order)
    finally:
        #print len(cache)
        cache_generic.clear()
        cache_factors.clear()

__all__ = ['diff']
