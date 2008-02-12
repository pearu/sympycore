from sympycore import Number, Symbol

a = Number(1,2)
b = Number(-1,2)
c = Number(3,4)
d = Number(-7,6)
e = Number(0,1)
f = Number(1,1)
g = Number(-5,1)
h = Number(36,1)

numbers = [a,b,c,d,e,f,g,h]

x = Symbol('x')

def test_compare():
    """comparison of small fractions and integers, 256x"""
    for s in numbers:
        for t in numbers:
            s < t
            s > t
            s >= t
            s <= t

def test_equality():
    """equality test of small fractions and integers, 256x"""
    for s in numbers:
        for t in numbers:
            s == t
            s == t
            s != t
            s != t

def test_add():
    """addition of small fractions and integers, 64x"""
    for s in numbers:
        for t in numbers:
            s + t

def test_sub():
    """subtraction of small fractions and integers, 64x"""
    for s in numbers:
        for t in numbers:
            s - t

def test_mul():
    """multiplication of small fractions and integers, 64x"""
    for s in numbers:
        for t in numbers:
            s * t

def test_div():
    """division of small fractions and integers, 64x"""
    for s in numbers:
        for t in numbers:
            s / t

def test_pow():
    """powers of small fractions and integers, 64x"""
    for s in numbers:
        for t in numbers:
            s ** t

def test_mixed_symbolic():
    """Mixed arithmetic with symbols and small integers / fractions"""
    a+x; a+x+b; a+x+x+x; a+x+b+x+c; a+x+x+b+x+c;
    b+x; b+x+c; b+x+x+x; b+x+c+x+d; b+x+x+c+x+d;
    c+x; c+x+b; c+x+x+x; c+x+d+x+e; c+x+x+d+x+e;
    d+x; d+x+c; d+x+x+x; d+x+e+x+f; d+x+x+e+x+f;
    a*x
    a*x*a
    a*x + b*x
    a*x - b*x
    a*x + b*x - a*x - b*x
    a*x**2 + a*x + b*x**2 - a*x**2 - b*x**2
    x/a + x/b + x/c
    x/e + x/f + x/g

if __name__=='__main__':
    from func_timeit import run_tests
    run_tests([test_compare, test_equality, test_add, test_sub, test_mul,
               test_div, test_pow, test_mixed_symbolic])
