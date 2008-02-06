
# use time() instead on unix
import sys
if sys.platform=='win32':
    from time import clock
else:
    from time import time as clock

from sympycore import profile_expr

def time1(n=500):
    import sympycore as sympy
    w = sympy.Fraction(3,4)
    x = sympy.polynomials.poly([0, 1, 1])
    b = (x-1)*(x-2)*(x-w)
    a = (x-1)*(x-2)*(x-3)*(x-4)*(x-5)# + (x-1)*(x-2)*x**10

    t1 = clock()
    while n:
        divmod(a, b)
        n -= 1
    t2 = clock()
    return 100 / (t2-t1)

def time2(n=500):
    import sympycore as sympy
    w = sympy.Fraction(3,4)
    x = sympy.polynomials.PolynomialRing[1]([0, 1, 1])
    b = (x-1)*(x-2)*(x-w)
    a = (x-1)*(x-2)*(x-3)*(x-4)*(x-5)# + (x-1)*(x-2)*x**10
    t1 = clock()
    while n:
        divmod(a, b)
        n -= 1
    t2 = clock()
    return 100 / (t2-t1)

def timing():
    t1 = time1()
    t2 = time2()
    return t1, t2, t1/t2

print timing()
print timing()
print timing()

profile_expr('time2(50)')
