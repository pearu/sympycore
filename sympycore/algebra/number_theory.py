from numberlib import *

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
