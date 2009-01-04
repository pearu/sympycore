
from sympycore import Ring, heads

def test_symbol():
    x,y = map(Ring, 'xy')
    assert str(x)=='x'
    assert repr(x)=="Ring('x')", repr(x)

def test_number():
    n = Ring(2)
    assert str(Ring(2))=='2'
    assert repr(Ring(2))=="Ring('2')", repr(Ring(2))
    assert str(Ring(-2))=='-2'
    assert repr(Ring(-2))=="Ring('-2')", repr(Ring(-2))

def test_neg():
    x,y,z = map(Ring, 'xyz')
    assert str(-x)=='-x', str(-x)
    assert str(-Ring(2))=='-2', str(-Ring(2))
    assert str(-(x+y))=='-x - y', str(-(x+y))

def test_add():
    x,y,z = map(Ring, 'xyz')
    assert str(x + y)=='x + y', str(x+y)
    assert repr(x + y)=="Ring('x + y')", repr(x+y)
    assert str(x + y + z)=='x + y + z', str(x + y + z)
    assert str(x + y + 1)=='x + y + 1', str(x + y + 1)
    assert str(x + y + y)=='x + 2*y', str(x + y + y)
    assert str(x + y + x)=='2*x + y', str(x + y + x)
    assert str(x + 1 + 2)=='x + 3', str(x + 1 + 2)
    assert str(x + 1 + y)=='x + 1 + y', str(x + 1 + y)

    assert str(Ring(1) + Ring(2))=='3', str(Ring(1) + Ring(2))
    assert str(2 + x) == 'x + 2', str(2+x)
    assert str(2 + x + y) == 'x + 2 + y', str(2+x + y)

def test_ncmul():
    x,y,z = map(Ring, 'xyz')
    assert str(x*y)=='x*y', str(x*y)
    assert str(x*y*x)=='x*y*x', str(x*y*x)
    assert str(x*(y*x))=='x*y*x', str(x*(y*x))
    assert str(x*y*x*x)=='x*y*x**2', str(x*y*x*x)
    assert str(x*(y*x)*x)=='x*y*x**2', str(x*(y*x)*x)
    assert str(x*y*(x*x))=='x*y*x**2', str(x*y*(x*x))
    assert str((x*y)*(x*x))=='x*y*x**2', str((x*y)*(x*x))

    assert str(2*x*y)=='2*x*y', str(2*x*y)
    assert str(x*2*y)=='2*x*y', str(x*2*y)
    assert str(x*y*2)=='2*x*y', str(x*y*2)
    assert str(3*x*y*2)=='6*x*y', str(3*x*y*2)
    assert str(3*(x*y)*2)=='6*x*y', str(3*(x*y)*2)
    assert str(3*(x*x)*2)=='6*x**2', str(3*(x*x)*2)

def test_pow():
    x,y,z = map(Ring, 'xyz')
    assert str(x**2)=='x**2', str(x**2)
    assert str(x*x)=='x**2', str(x*x)
    assert str(x**y)=='x**y', str(x**y)
    assert str(2**x)=='2**x', str(2**x)
