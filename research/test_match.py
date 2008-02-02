
# use time() instead on unix
import sys
if sys.platform=='win32':
    from time import clock
else:
    from time import time as clock

from sympycore import profile_expr

def time1(n=1):
    from sympycore import Symbol, sin
    x,y,z,v,w = map(Symbol,'xyzvw')
    pattern = (2+v)*(v*w)**sin(x+w)
    expr = (2+x)*(x*y**2)**sin(x+y**2)
    t1 = clock()
    while n:
        m=expr.match(pattern,v,w)
        n -= 1
    t2 = clock()
    assert m=={w:y**2,v:x},`m`
    return 100 / (t2-t1)

def time2(n=1):
    from sympy import Symbol, sin, Wild
    x,y,z = map(Symbol,'xyz')
    v,w = map(Wild,'vw')
    pattern = (2+v)*(v*w)**sin(x+w)
    expr = (2+x)*(x*y**2)**sin(x+y**2)
    t1 = clock()
    while n:
        m=expr.match(pattern)
        n -= 1
    t2 = clock()
    assert m=={w:y**2,v:x},`m`
    #print 'time2:',t2-t1
    return 100 / (t2-t1)

def time3(n=5):
    import swiginac
    x,y,z = map(swiginac.symbol,'xyz')
    v,w = map(swiginac.wild,[1,2])
    pattern = (v*w)**swiginac.sin(x+w)
    expr = (x*y**2)**swiginac.sin(x+y**2)
    pattern = (v*w)
    expr = (x*y**2)
    l = []
    t1 = clock()
    while n:
        m=expr.match(pattern,l)
        n -= 1
    t2 = clock()
    print l,m
    assert m=={w:y**2,v:x},`m`
    print 'time3:',t2-t1
    return 100 / (t2-t1)

def timing():
    t1 = time1()
    t2 = time2()
    return t1, t2, t1/t2

print timing()
print timing()
print timing()

#time3(1)
#profile_expr('time1(1)')
