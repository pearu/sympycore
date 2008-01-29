
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
    e = ((x+2*y+3*z)**20).expand()
    t1 = clock()
    while n:
        e.subs(x,z).subs(y,z)
        n -= 1
    t2 = clock()
    return 100 / (t2-t1)

def time2(n=5):
    from sympy import Symbol, sin
    x,y,z = map(Symbol,'xyz')
    e = ((x+2*y+3*z)**20).expand()
    t1 = clock()
    while n:
        e.subs(x,z).subs(y,z)
        n -= 1
    t2 = clock()
    #print 'time2:',t2-t1
    return 100 / (t2-t1)

def time3(n=5):
    import swiginac
    x,y,z = map(swiginac.symbol,'xyz')
    e = ((x+2*y+3*z)**20).expand()
    t1 = clock()
    while n:
        e.subs(x==z).subs(y==z)
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
