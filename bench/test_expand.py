START_REVISION=418

from sympycore import Symbol, Number
x,y,z = map(Symbol,'xyz')

bina1 = (3*x+2*y)**2
binb1 = (3*x+2)**2
binc1 = (3*x+2*y)**4

bina2 = (Number(3,4)*x + Number(1,2)*y)**2
binb2 = (Number(3,4)*x + Number(1,2))**2
binc2 = (Number(3,4)*x + Number(1,2)*y)**4

bin50a = (x+y)**50
bin50b = (x+3)**50

quad2 = (x+y+z+1)**2
quad8 = (x+y+z+1)**8

mixed1 = (x+1) * (y+1)
mixed2 = (x+y) * (y+1)**2
mixed3 = (x+y)**3 * (x+1)**2
mixed4 = (x+y+1)**2 * (x+1)**2
mixed5 = (x+y+3)**2 * (x+y+1)

mixed6 = (x+y+1)**8 * (x+z)**4

nested = (1+(x+2*z+(y+(1+y+z))**2)**2)

def test_bin_1():
    """Expand small binomials with int coeffs, 30x"""
    for i in range(10):
        bina1.expand()
        binb1.expand()
        binc1.expand()

def test_bin_2():
    """Expand small binomials with fractional coeffs, 30x"""
    for i in range(10):
        bina2.expand()
        binb2.expand()
        binc2.expand()

def test_bin_3():
    """Expand big binomials, 2x"""
    bin50a.expand()
    bin50b.expand()

def test_quad_1():
    """Expand small quadrinomial, 5x"""
    for i in range(5):
        quad2.expand()

def test_quad_2():
    """Expand large quadrinomial"""
    quad8.expand()

def test_mixed_1():
    """Expand small mixed products, 8x"""
    mixed1.expand(); mixed1.expand(); mixed1.expand()
    mixed2.expand(); mixed2.expand(); 
    mixed3.expand()
    mixed4.expand()
    mixed5.expand()

def test_mixed_2():
    """Expand large mixed product"""
    mixed6.expand()

def test_nested():
    """Expand deeply nested expression"""
    nested.expand()

if __name__=='__main__':
    from func_timeit import run_tests
    run_tests([
        test_bin_1, test_bin_2, test_bin_3,
        test_quad_1, test_quad_2,
        test_mixed_1, test_mixed_2, test_nested
        ])
