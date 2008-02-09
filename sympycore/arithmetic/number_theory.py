from .numbers import Fraction, normalized_fraction, Complex, Float, div

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
    if L == 2: return div(args[0]*args[1], gcd(*args))
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
    """Return (L, d) where L is a list of digits of abs(x) in the given
    base and d is the (signed) distance from the leading digit to the
    radix point. For example, 1234.56 becomes ([1, 2, 3, 4, 5, 6], 4)
    and 0.001 becomes ([1], -2). If, during the generation of
    fractional digits, the length reaches `truncation` digits, the
    iteration is stopped."""
    assert base > 1
    assert isinstance(x, (int, long, Fraction))
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

class _exp_tuple(tuple):
    def __div__(self, other):
        return self * other**-1

    def __mul__(self, other):
        assert isinstance(other, type(self)),`other`
        return self.__class__([i+j for i,j in zip(self,other)])

    def __pow__(self, e):
        assert isinstance(e, int),`e`
        return self.__class__([i*e for i in self])

def binomial_coefficients(n):
    """Return a dictionary containing pairs {(k1,k2) : C_kn} where
    C_kn are binomial coefficients and n=k1+k2.
    """
    d = {_exp_tuple((0, n)):1}
    a = 1
    for k in xrange(1, n+1):
        a = (a * (n-k+1))//k
        d[_exp_tuple((k, n-k))] = a
    return d

def multinomial_coefficients(m, n):
    """Return a dictionary containing pairs {(k1,k2,..,km) : C_kn}
    where C_kn are multinomial coefficients and n=k1+k2+..+km.
    """
    ## Consider polynomial
    ##   P(x) = sum_{i=0}^m p_i x^k
    ## and its m-th exponent
    ##   P(x)^n = sum_{k=0}^{m n} a(n,k) x^k
    ## The coefficients a(n,k) can be computed using the
    ## J.C.P. Miller Pure Recurrence [see D.E.Knuth,
    ## Seminumerical Algorithms, The art of Computer
    ## Programming v.2, Addison Wesley, Reading, 1981;]:
    ##  a(n,k) = 1/(k p_0) sum_{i=1}^m p_i ((n+1)i-k) a(n,k-i),
    ## where a(n,0) = p_0^n.
    if m==2:
        return binomial_coefficients(n)
    symbols = [_exp_tuple((0,)*i + (1,) +(0,)*(m-i-1)) for i in range(m)]
    s0 = symbols[0]
    p0 = [s/s0 for s in symbols]
    r = {s0**n:1}
    r_get = r.get
    l = [r.items()]
    for k in xrange(1, n*(m-1)+1):
        d = {}
        d_get = d.get
        for i in xrange(1, min(m,k+1)):
            nn = (n+1)*i-k
            if nn:
                t = p0[i]
                for t2, c2 in l[k-i]:
                    tt = t2 * t
                    cc = normalized_fraction(nn * c2, k)
                    b = d_get(tt)
                    if b is None:
                        d[tt] = cc
                    else:
                        cc = b + cc
                        if cc:
                            d[tt] = cc
                        else:
                            del d[tt]
        r1 = d.items()
        l.append(r1)
        for t, c in r1:
            b = r_get(t)
            if b is None:
                r[t] = c
            else:
                c = b + c
                if c:
                    r[t] = c
                else:
                    del r[t]
    return r
