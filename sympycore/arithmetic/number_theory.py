"""Provides algorithms from number theory.
"""
from .numbers import mpq, normalized_fraction, Complex, Float, div

__all__ = ['gcd', 'lcm', 'factorial',
           'integer_digits', 'real_digits',
           'multinomial_coefficients']

__docformat__ = "restructuredtext en"

def factorial(n, memo=[1, 1]):
    """Return n factorial (for integers n >= 0 only)."""
    if n < 0:
        raise ValueError
    k = len(memo)
    if n < k:
        return memo[n]
    p = memo[-1]
    while k <= n:
        p *= k
        k += 1
        if k < 100:
            memo.append(p)
    return p

def gcd(*args):
    """Calculate the greatest common divisor (GCD) of the arguments."""
    L = len(args)
    if L == 0: return 0
    if L == 1: return args[0]
    if L == 2:
        a, b = args
        while b:
            a, b = b, a % b
        return a
    return gcd(gcd(args[0], args[1]), *args[2:])

def lcm(*args):
    """Calculate the least common multiple (LCM) of the arguments."""
    L = len(args)
    if L == 0: return 0
    if L == 1: return args[0]
    if L == 2: return div(args[0], gcd(*args))*args[1]
    return lcm(lcm(args[0], args[1]), *args[2:])

# TODO: this could use the faster implementation in mpmath
def integer_digits(n, base=10):
    """Return a list of the digits of abs(n) in the given base."""
    assert base > 1
    assert isinstance(n, (int, long))
    n = abs(n)
    if not n:
        return [0]
    L = []
    while n:
        n, digit = divmod(n, base)
        L.append(int(digit))
    return L[::-1]

# TODO: this could (also?) be implemented as an endless generator
def real_digits(x, base=10, truncation=10):
    """Return ``(L, d)`` where L is a list of digits of ``abs(x)`` in
    the given base and ``d`` is the (signed) distance from the leading
    digit to the radix point.

    For example, 1234.56 becomes ``([1, 2, 3, 4, 5, 6], 4)`` and 0.001
    becomes ``([1], -2)``. If, during the generation of fractional
    digits, the length reaches `truncation` digits, the iteration is
    stopped."""
    assert base > 1
    assert isinstance(x, (int, long, mpq))
    if x == 0:
        return ([0], 1)
    x = abs(x)
    exponent = 0
    while x < 1:
        x *= base
        exponent -= 1
    integer, fraction = divmod(x, 1)
    L = integer_digits(integer, base)
    exponent += len(L)
    if fraction:
        p, q = fraction
        for i in xrange(truncation - len(L)):
            p = (p % q) * base
            if not p:
                break
            L.append(int(p//q))
    return L, exponent

def binomial_coefficients(n):
    """Return a dictionary containing pairs {(k1,k2) : C_kn} where
    C_kn are binomial coefficients and n=k1+k2."""
    d = {(0, n):1, (n, 0):1}
    a = 1
    for k in xrange(1, n//2+1):
        a = (a * (n-k+1))//k
        d[k, n-k] = d[n-k, k] = a
    return d

def binomial_coefficients_list(n):
    d = [1] * (n+1)
    a = 1
    for k in xrange(1, n//2+1):
        a = (a * (n-k+1))//k
        d[k] = d[n-k] = a
    return d

def multinomial_coefficients(m, n, _tuple=tuple, _zip=zip):
    """Return a dictionary containing pairs ``{(k1,k2,..,km) : C_kn}``
    where ``C_kn`` are multinomial coefficients such that
    ``n=k1+k2+..+km``.

    For example:

    >>> print multinomial_coefficients(2,5)
    {(3, 2): 10, (1, 4): 5, (2, 3): 10, (5, 0): 1, (0, 5): 1, (4, 1): 5}

    The algorithm is based on the following result:
    
       Consider a polynomial and it's ``m``-th exponent::
       
         P(x) = sum_{i=0}^m p_i x^k
         P(x)^n = sum_{k=0}^{m n} a(n,k) x^k

       The coefficients ``a(n,k)`` can be computed using the
       J.C.P. Miller Pure Recurrence [see D.E.Knuth, Seminumerical
       Algorithms, The art of Computer Programming v.2, Addison
       Wesley, Reading, 1981;]::
       
         a(n,k) = 1/(k p_0) sum_{i=1}^m p_i ((n+1)i-k) a(n,k-i),

       where ``a(n,0) = p_0^n``.
    """

    if m==2:
        return binomial_coefficients(n)
    symbols = [(0,)*i + (1,) + (0,)*(m-i-1) for i in range(m)]
    s0 = symbols[0]
    p0 = [_tuple(aa-bb for aa,bb in _zip(s,s0)) for s in symbols]
    r = {_tuple(aa*n for aa in s0):1}
    r_get = r.get
    r_update = r.update
    l = [0] * (n*(m-1)+1)
    l[0] = r.items()
    for k in xrange(1, n*(m-1)+1):
        d = {}
        d_get = d.get
        for i in xrange(1, min(m,k+1)):
            nn = (n+1)*i-k
            if not nn:
                continue
            t = p0[i]
            for t2, c2 in l[k-i]:
                tt = _tuple([aa+bb for aa,bb in _zip(t2,t)])
                cc = nn * c2
                b = d_get(tt)
                if b is None:
                    d[tt] = cc
                else:
                    cc = b + cc
                    if cc:
                        d[tt] = cc
                    else:
                        del d[tt]
        r1 = [(t, c//k) for (t, c) in d.iteritems()]
        l[k] = r1
        r_update(r1)
    return r
