
import os
import sys
from time import ctime
from timeit import default_timer as clock
from random import randint

thisdir = os.path.dirname(__file__)

def cacheit(func):
    cache = {}
    def wrap(module):
        f = module.__file__
        r = cache.get(f)
        if r is None:
            cache[f] = r = func(module)
        return r
    wrap.__doc__ = func.__doc__
    return wrap

def unload_sympy(name='sympy'):
    for n,m in sys.modules.items():
        if n.startswith(name):
            del sys.modules[n]    

def import_sympy_trunk():
    "sympy (no caching)"
    raise "needs update!"
    unload_sympy()
    sys.path.insert(0,os.path.abspath(os.path.join(thisdir,'..','..','..','hg','sympy','trunk')))
    import sympy
    del sys.path[0]
    return sympy

def import_sympy_trunk_caching():
    "sympy (with caching)"
    unload_sympy()
    sys.path.insert(0,os.path.abspath(os.path.join(thisdir,'..','..','..','hg','sympy','trunk')))
    import sympy
    del sys.path[0]
    return sympy

def import_sympycore_trunk():
    "sympycore"
    #unload_sympy('sympycore')
    sys.path.insert(0,os.path.abspath(os.path.join(thisdir,'..','trunk')))
    import sympycore as sympy
    del sys.path[0]
    sympy.sympify = sympy.Calculus.convert
    return sympy

def import_swiginac():
    "swiginac"
    unload_sympy('swiginac')
    import swiginac
    swiginac.Symbol = swiginac.symbol
    swiginac.pi = swiginac.Pi
    swiginac.Add = lambda *args: reduce(swiginac.add,args,0)
    swiginac.Mul = lambda *args: reduce(swiginac.mul,args,0)
    x,y,z = map(swiginac.symbol,'xyz')
    swiginac.sympify = lambda expr: swiginac.parse_string(expr,[x,y,z])
    return swiginac

@cacheit
def test_mul_performace(sympy):
    """`Mul(x,<random integer>,y)`, 2000x"""
    x = sympy.Symbol('x')
    y = sympy.Symbol('y')
    Mul = sympy.Mul
    i = 2000
    t1 = clock()
    while i:
        i -= 1
        Mul(x,randint(0,1000000),y)
    t2 = clock()
    return t2-t1

@cacheit
def test_add_performace(sympy):
    """`Add(x,<random integer>,y)`, 2000x"""
    x = sympy.Symbol('x')
    y = sympy.Symbol('y')
    Add = sympy.Add
    i = 2000
    t1 = clock()
    while i:
        i -= 1
        Add(x,randint(0,1000000),y)
    t2 = clock()
    return t2-t1

@cacheit
def test_summation_performance(sympy):
    """`sum(x**i/i,i=1..400)`"""
    s = getattr(sympy,'Integer', int)(0)
    x = sympy.Symbol('x')
    i = 401
    t1 = clock()
    while i:
        s += x**i/i
        i -= 1
    t2 = clock()
    return t2-t1

@cacheit
def test_expand_performance(sympy):
    """`expand((x+z+y)**20 * (z+x)**9)`"""
    if sympy.__name__ == 'swiginac':
        e = sympy.sympify('(x+z+y)^20 * (z+x)^9')
    else:
        e = sympy.sympify('(x+z+y)**20 * (z+x)**9')
    t1 = clock()
    e = e.expand()
    t2 = clock()
    return t2-t1

@cacheit
def test_complex_power(sympy):
    """`expand((2+3*I)**1000)`"""
    e = 2 + 3*sympy.I
    t1 = clock()
    e = (e**1000).expand()
    t2 = clock()
    return t2-t1

@cacheit
def test_rat_complex_power(sympy):
    """`expand((2+3*I/4)**1000)`"""
    e = 2 + 3*sympy.I/4
    t1 = clock()
    e = (e**1000).expand()
    t2 = clock()
    return t2-t1

@cacheit
def test_trig_evaluation(sympy):
    """`sin(n*pi/6), n=0...100`"""
    pi = sympy.pi
    sin = sympy.sin
    t1 = clock()
    for n in xrange(101):
        sin(n*pi/6)
    t2 = clock()
    return t2-t1

@cacheit
def test_polynomial_subs(sympy):
    """`e.subs(x,z).subs(y,z) where e = expand((x+2*y+3*z)**20)`"""
    x,y,z = map(sympy.Symbol,'xyz')
    e = ((x+2*y+3*z)**20).expand()
    if sympy.__name__=='swiginac':
        t1 = clock()
        e.subs(x==z).subs(y==z)
        t2 = clock()
    else:
        t1 = clock()
        e.subs(x,z).subs(y,z)
        t2 = clock()
    return t2-t1

@cacheit
def test_str(sympy):
    """`str(e) where e = expand((x+2*y+3*z)**50)`"""
    x,y,z = map(sympy.Symbol,'xyz')
    e = ((x+2*y+3*z)**50).expand()
    t1 = clock()
    str(e)
    t2 = clock()
    return t2-t1

@cacheit
def test_str_small(sympy):
    """`str(e) where e = <randint> * (x+2*y+3*z), 1000x`"""
    x,y,z = map(sympy.Symbol,'xyz')
    e = x+2*y+3*z
    l = [randint(0,1000000)*e for i in xrange(1000)]
    t1 = clock()
    while l:
        str(l.pop())
    t2 = clock()
    return t2-t1

@cacheit
def test_evalf_small(sympy):
    """`(sin(1+pi)**2 + 3**sqrt(1+pi**2)).evalf(30)`"""
    a = sympy.sin(1+sympy.pi)**2 + sympy.cos(1+sympy.pi**2)**2
    t1 = clock()
    a.evalf(30)
    t2 = clock()
    return t2-t1

@cacheit
def test_evalf_big(sympy):
    """`(sin(1+pi)**2 + 3**sqrt(1+pi**2)).evalf(300)`"""
    if sympy.__name__=='swiginac':
        # the evalf argument seems to have no effect
        return
    a = sympy.sin(1+sympy.pi)**2 + sympy.cos(1+sympy.pi**2)**2
    t1 = clock()
    a.evalf(300)
    t2 = clock()
    return t2-t1

@cacheit
def test_integrate(sympy):
    """`f=4*x**3+y**2*x**2+x+1, f=integrate(f) for i=1...10`"""
    if sympy.__name__=='swiginac':
        return
    x, y = map(sympy.Symbol, 'xy')
    f = 4*x**3 + y**2*x**2 + x + 1
    t1 = clock()
    for i in range(10):
        f = sympy.integrate(f, x)
    t2 = clock()
    return t2-t1

@cacheit
def test_diff(sympy):
    """`f=(x/(1+sin(x**(y+x**2)))**2), f=f.diff(x) for i=1...5`"""
    x, y = map(sympy.Symbol, 'xy')
    f = (x / (1+sympy.sin(x**(y+x**2)))**2)
    t1 = clock()
    for i in range(5):
        f = f.diff(x)
    t2 = clock()
    return t2-t1

@cacheit
def test_match(sympy):
    """`expr.match(pattern), where expr=(x*y**2)**sin(x+y**2), pattern=(v*w)**sin(v+w)`"""
    if sympy.__name__=='swiginac':
        return
    if sympy.__name__=='sympycore':
        x,y,z,v,w = map(sympy.Symbol,'xyzvw')
        args = (v,w)
    else:
        x,y,z = map(sympy.Symbol,'xyz')
        v,w = map(sympy.Wild,'vw')
        args = ()
    pattern = (v*w)**sympy.sin(v+w)
    expr = (x*y**2)**sympy.sin(x+y**2)
    t1 = clock()
    m = expr.match(pattern,*args)
    t2 = clock()
    assert m=={w:y**2,v:x} or m=={w:x, v:y**2},`m`
    return t2-t1

@cacheit
def test_polynomial_division(sympy):
    """polynomial division P/Q, P,Q have roots (1,2,3,4,5), (1,2,3/4)"""
    if sympy.__name__=='swiginac':
        return
    if sympy.__name__ == 'sympy':
        x = x1 = sympy.Symbol('x')
        x = x + x**2
        w = sympy.Rational(3,4)
        divide = sympy.div
        P = lambda e: sympy.Poly(e,x1)#nomial
    if sympy.__name__ == 'sympycore':
        x = sympy.polynomials.poly([0, 1, 1])
        #x = sympy.polynomials.PolynomialRing[1]([0, 1, 1])
        w = sympy.mpq((3,4))
        divide = divmod
        P = lambda p: p
    a = P((x-1)*(x-2)*(x-3)*(x-4)*(x-5))
    r = 0
    for i in range(1,5):
        b = P((x-1)*(x-2)*(x-w/i))
        t1 = clock()
        c = divide(a,b)
        t2 = clock()
        r += t2 - t1
    return r

@cacheit
def test_fem(sympy):
    """Run sympy/examples/fem_test.py."""
    if sympy.__name__=='swiginac':
        return
    if sympy.__name__ == 'sympy':
        unload_sympy('fem')
        import fem_sympy as fem
        zeronm = sympy.zeronm
        return # Polynomial interface in sympy has changed and seems broken at the moment    
    if sympy.__name__ == 'sympycore':
        import fem
        zeronm = lambda d1,d2: sympy.Matrix(d2,d2)
    t1 = clock()
    t = fem.ReferenceSimplex(2)
    fe = fem.Lagrange(2,2)

    u = 0
    us = []
    for i in range(0, fe.nbf()):
        ui = sympy.Symbol("u_%d" % i)
        us.append(ui)
        u += ui*fe.N[i]


    J = zeronm(fe.nbf(), fe.nbf())

    for i in range(0, fe.nbf()):
        Fi = u*fe.N[i]
        for j in range(0, fe.nbf()):
            uj = us[j]
            integrands = Fi.diff(uj)
            J[j,i] = t.integrate(integrands)
    t2 = clock()
    return t2 - t1

def generate_table(stream, import_functions, test_functions):

    columns = [['*Executed code*']]

    for test_func in test_functions:
        lines = test_func.__doc__.splitlines()
        columns[0].append('%s' % (lines[0]))

    for import_func in import_functions:
        columns.append(['*%s*' % (import_func.__doc__)])

    i = 0
    for import_func in import_functions:
        print 'importing',import_func.__doc__
        i += 1
        column = columns[i]
        sympy = import_func()
        for test_func in test_functions:
            print '  running',test_func.__doc__.splitlines()[0],
            sys.stdout.flush()
            if 0 and sympy.__name__=='sympycore':
                sympy.profile_expr('test_func(sympy)')
            d = test_func(sympy)
            print d,'secs'
            column.append(d)
    speedup_column = ['*Speed-up*']
    sort_list = []
    for i in range(1,len(columns[0])):
        row = [column[i] for column in columns[1:]]
        if row[-1]:
            r = min([r for r in row[:-1] if r is not None] or [0])/row[-1]
        else:
            r = 0
        if r==0:
            speedup_column.append('N/A')
        else:
            speedup_column.append('%.4fx' % (r))
        sort_list.append((r,i))
        for column in columns[1:]:
            c = column[i]
            if c is None:
                column[i] = 'N/A'
            else:
                column[i] = '%.4f secs' % (c)
    columns.append(speedup_column)
    formats = []
    for column in columns:
        formats.append(' %'+str(max(map(len,map(str,column))))+'s ')

    #sort_list.sort()
    #sort_list.reverse()
    for (r,i) in [(None,0)] + sort_list:
        row = [format % column[i] for format, column in zip(formats,columns)]
        print >> stream, '||'.join(['']+row+[''])

    print >> stream, ''

def main(stream):
    import_functions = [import_sympy_trunk_caching,
                        #import_sympy_trunk,
                        import_swiginac,
                        import_sympycore_trunk]
    test_functions = [\
                    test_add_performace,
                    test_mul_performace,
                    test_summation_performance,
                    test_expand_performance,
                    test_complex_power,
                    test_rat_complex_power,
                    test_trig_evaluation,
                    test_polynomial_subs,
                    test_evalf_small,
                    test_evalf_big,
                    test_str_small,
                    test_str,
                    test_integrate,
                    test_diff,
                    test_match,
                    test_polynomial_division,
                    test_fem,
                    ]
    speedup_index = 2

    print >> stream, '#summary Performance benchmarks'
    print >> stream, ''
    print >> stream, '_This page is automatically generated. Do not edit this page!_\n'
    print >> stream, 'See http://sympycore.googlecode.com/svn/tools/gen_performance_page.py .'
    print >> stream, ''
    print >> stream, 'Last update: %s' % (ctime())
    print >> stream, ''

    generate_table(stream, [import_sympy_trunk_caching, import_sympycore_trunk], test_functions)
    generate_table(stream, [import_swiginac, import_sympycore_trunk], test_functions)
    #generate_table(stream, [import_sympy_trunk, import_sympy_trunk_caching], test_functions)

    print >> stream, 'Notes:'
    print >> stream, '  # Speed-up is inverse ratio between the last column timing and the minimum of rest of columns.'
    print >> stream, '  # swiginac does not support precision parameter in evalf'
    print >> stream, '  # swiginac objects don not have integrate method'
    print >> stream, '  # swiginac match does not handle given case'

if __name__=='__main__':
    f = open(os.path.join(thisdir,'../wiki/Performance.wiki'),'w')
    main(f)
    f.close()
