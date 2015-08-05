#
# Run given test case.
#
# Author: Pearu Peterson
# Created: December 2007
#

import timeit
import sys

def timer(stmt, setup='pass',n=500):
    t = timeit.Timer(stmt=stmt, setup=setup)
    try:
        c = int(n/min(t.repeat(repeat=3, number=n)))
        print "(%r statements)/second: %s" % (stmt,c)
        # (<statement>, <setup code>): <how many statements can be executed in 1 sec>)
    except:
        t.print_exc()
        sys.exit(1)

def main(case):
    if case=='sympy':
        import os
        os.environ["SYMPY_USE_CACHE"] = "no"
        setup = '''
from sympy import Symbol, Rational
x,y,z = map(Symbol,'xyz')
a,b,c = Rational(1,2), Rational(2,3), Rational(4,5)
stmt = (3*(a*x + b*y + c*z))
print "stmt:",stmt
print "stmt.expand:",stmt.expand()
if stmt!=stmt.expand():
    print "STOP ME and fix stmt: add expand!!!"
    sys.exit(1)
if stmt is (3*(a*x + b*y + c*z)):
    print "STOP ME and fix stmt: disable caching!!!"
    sys.exit(3)
'''
        stmt = '''3*(a*x + b*y + c*z)'''
    elif case=='swiginac':
        setup = '''
from swiginac import symbol
from swiginac import numeric as rational
x,y,z = map(symbol,'xyz')
a,b,c = rational(1,2), rational(2,3), rational(4,5)
stmt = (3*(a*x + b*y + c*z))
print "stmt:",stmt
print "stmt.expand:",stmt.expand()
if stmt!=stmt.expand():
    print "STOP ME and fix stmt: add expand!!!"
    sys.exit(1)
if stmt is (3*(a*x + b*y + c*z)):
    print "STOP ME and fix stmt: disable caching!!!"
    sys.exit(3)
'''
        stmt = '''3*(a*x + b*y + c*z)'''
    elif case=='pyginac':
        setup = '''
from ginac import symbol
from ginac import numeric as rational
x,y,z = map(symbol,'xyz')
a,b,c = rational(1,2), rational(2,3), rational(4,5)
stmt = (3*(a*x + b*y + c*z))
print "stmt:",stmt
print "stmt.expand:",stmt.expand()
if stmt!=stmt.expand():
    print "STOP ME and fix stmt: add expand!!!"
    sys.exit(1)
if stmt is (3*(a*x + b*y + c*z)):
    print "STOP ME and fix stmt: disable caching!!!"
    sys.exit(3)
'''
        stmt = '''3*(a*x + b*y + c*z)'''
    elif case=='symbolic':
        setup = '''
from symbolic.api import Symbol
from symbolic.api import Rational
x,y,z = map(Symbol,'xyz')
a,b,c = Rational(1,2), Rational(2,3), Rational(4,5)
stmt = (3*(a*x + b*y + c*z))
print "stmt:",stmt
print "stmt.expand:",stmt.expand()
if stmt!=stmt.expand():
    print "STOP ME and fix stmt: add expand!!!"
    sys.exit(1)
if stmt is (3*(a*x + b*y + c*z)):
    print "STOP ME and fix stmt: disable caching!!!"
    sys.exit(3)
'''
        stmt = '''3*(a*x + b*y + c*z)'''
    elif case=='sympycore':
        setup = '''
from sympycore import Symbol, Number
x,y,z = map(Symbol,'xyz')
a = Number(1,2)
b = Number(2,3)
c = Number(4,5)
stmt = 3*(a*x + b*y + c*z)
print "stmt:",stmt
print "stmt.expand:",stmt.expand()
if 0 and stmt!=stmt.expand():
    print "STOP ME and fix stmt: add expand!!!"
    sys.exit(1)
if stmt is (3*(a*x + b*y + c*z)):
    print "STOP ME and fix stmt: disable caching!!!"
    sys.exit(3)
'''
        stmt = '''3*(a*x + b*y + c*z)'''
    elif case=='sage':
        # runme: sage -python run1test.py
        setup = '''
from sage.all import var, QQ, PolynomialRing, RationalField
R, (x, y, z) = PolynomialRing(RationalField(), 3, 'xyz').objgens()
a,b,c = QQ('1/2'), QQ('2/3'), QQ('4/5')
stmt = 3*(a*x + b*y + c*z)
print "stmt:",stmt
#print "stmt.expand:",stmt.expand()
        '''
        stmt = '''(3*(a*x + b*y + c*z))'''
    elif case=='sage2':
        # runme: sage -python run1test.py
        # WARNING: this leaves a lisp process running that
        #          must be killed manually. 
        setup = '''
from sage.all import var, QQ
x,y,z = map(var, "xyz")
a,b,c = QQ('1/2'), QQ('2/3'), QQ('4/5')
stmt = 3*(a*x + b*y + c*z)
print "stmt:",stmt
print "stmt.expand:",stmt.expand()
        '''
        stmt = '''(3*(a*x + b*y + c*z)).expand()'''
    else:
        print 'Unknown case: %r' % (case)
        return
    timer(stmt, setup)

if __name__=='__main__':
    
    #main('sympy')
    #main('swiginac')
    main(sys.argv[1])
    #main('symbolic')
    #main('sage')
    #main('sage2')
    #main('sympycore')
