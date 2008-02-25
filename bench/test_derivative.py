START_REVISION=300

from sympycore import Symbol, Add, sin
x,y,z = map(Symbol,'xyz')

f1 = 4*x**3 + sin(y)**2*x**2 + x + 1
f2 = (x / (1+sin(x**(y+x**2)))**2)

def test_diff1():
    """ f=f.diff(x), 5x, f=(x/(1+sin(x**(y+x**2)))**2)
    """
    i = 5
    f = f2
    while i:
        f = f.diff(x)
        i -= 1

def test_diff2():
    """ f.diff(x, 5), f=(x/(1+sin(x**(y+x**2)))**2)
    """
    i = 5
    f = f2
    while i:
        i -= 1
    f = f.diff(x, 5)

def test_integrate():
    """ f = f.integrate(), 100x, f=4*x**3+sin(y)**2*x**2+x+1
    """
    i = 100
    ff = f1
    while i:
        ff = ff.integrate(x)
        i -= 1

def test_integrate_defined1(f1=f1):
    """ f.integrate((x,2,3)), 100x, f=4*x**3+sin(y)**2*x**2+x+1
    """
    i = 100
    while i:
        f = f1.integrate((x, 2, 3))
        i -= 1

def test_integrate_defined2(f1=f1):
    """ r=f.integrate(x); r.subs(x,3)-r.subs(x,2), 100x, f=4*x**3+sin(y)**2*x**2+x+1
    """
    i = 100
    while i:
        f = f1.integrate(x)
        f = f.subs(x, 3) - f.subs(x, 2)
        i -= 1

if __name__=='__main__':
    from func_timeit import run_tests
    run_tests([test_diff1, test_diff2, test_integrate,
               test_integrate_defined1, test_integrate_defined2
               ])
