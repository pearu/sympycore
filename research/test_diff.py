
# use time() instead on unix
import sys
if sys.platform=='win32':
    from time import clock
else:
    from time import time as clock

from sympycore import profile_expr

def time1(n=5):
    from sympycore import Symbol, sin
    x,y,z = map(Symbol,'xyz')
    f = (x / (1+sin(x**(y+x**2)))**2)
    t1 = clock()
    while n:
        f = f.diff(x)
        n -= 1
    t2 = clock()
    return 100 / (t2-t1)

def time2(n=5):
    from sympy import Symbol, sin
    x,y,z = map(Symbol,'xyz')
    f = (x / (1+sin(x**(y+x**2)))**2)
    t1 = clock()
    while n:
        f = f.diff(x)
        n -= 1
    t2 = clock()
    #print 'time2:',t2-t1
    return 100 / (t2-t1)

def time3(n=5):
    import swiginac
    x,y,z = map(swiginac.symbol,'xyz')
    f = (x / (1+swiginac.sin(x**(y+x**2)))**2)
    t1 = clock()
    while n:
        f = f.diff(x)
        n -= 1
    t2 = clock()
    print 'time3:',t2-t1
    return 100 / (t2-t1)

def timing():
    t1 = time1()
    t2 = time3()
    return t1, t2, t1/t2

print timing()
print timing()
print timing()

profile_expr('time1(5)')
