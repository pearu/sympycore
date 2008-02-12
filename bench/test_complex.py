
from sympycore import I, Number

def Complex(r,i):
    return r+I*i

a = Complex(1,2)
b = Complex(Number(-1,3),2)
c = Complex(3,4)
d = Complex(Number(-7,9),6)
e = Complex(0,1)
f = Complex(1,1)
g = Complex(-5,1)
h = Complex(Number(36,109),1)

numbers = [a,b,c,d,e,f,g,h]
intnumbers = [2, 3, -2, 5, 6, 7, 11, -9]

def test_add():
    """addition of complexes, 64x"""
    for s in numbers:
        for t in numbers:
            s + t

def test_sub():
    """subtraction of complexes, 64x"""
    for s in numbers:
        for t in numbers:
            s - t

def test_mul():
    """multiplication of complexes, 64x"""
    for s in numbers:
        for t in numbers:
            s * t

def test_div():
    """division of complexes, 64x"""
    for s in numbers:
        for t in numbers:
            s / t

def test_pow():
    """complex integer power, 64x"""
    for s in numbers:
        for t in intnumbers:
            s ** t

if __name__=='__main__':
    from func_timeit import run_tests
    run_tests([test_add, test_sub, test_mul,
               test_div, test_pow])
