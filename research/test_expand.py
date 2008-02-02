
# use time() instead on unix
import sys
if sys.platform=='win32':
    from time import clock
else:
    from time import time as clock

from sympycore import profile_expr

def time1(n=1):
    from sympycore import Symbol
    x,y,z = map(Symbol,'xyz')
    e1 = ((x+y+z)**20).expand()
    e2 = ((x+y)**19).expand()
    expr = e1 * e2
    expr = ((x+y+z)**20) * ((x+y)**19)
    t1 = clock()
    while n:
        expr.expand()
        n -= 1
    t2 = clock()
    return 100 / (t2-t1)

def time2(n=1):
    from sympy import Symbol
    x,y,z = map(Symbol,'xyz')
    e1 = ((x+y+z)**20).expand()
    e2 = ((x+y)**19).expand()
    expr = e1 * e2
    #expr = ((x+y+z)**20) * ((x+y)**19)
    t1 = clock()
    while n:
        expr.expand()
        n -= 1
    t2 = clock()
    #print 'time2:',t2-t1
    return 100 / (t2-t1)

def time3(n=1):
    import swiginac
    x,y,z = map(swiginac.symbol,'xyz')
    e1 = ((x+y+z)**20).expand()
    e2 = ((x+y)**19).expand()
    expr = e1 * e2
    expr = ((x+y+z)**20) * ((x+y)**19)
    t1 = clock()
    while n:
        expr.expand()
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

profile_expr('time1(1)')
