
from sympycore import CommutativeRing, heads

def test_add():
    x,y,z = map(CommutativeRing, 'xyz')
    assert x+y == y+x
    assert x+2 == 2+x
    assert str(x+y) in ['x + y', 'y + x'],str(x+y)
    assert str(2+x) in ['2 + x', 'x + 2'], str(2+x)

def test_mul():
    x,y,z = map(CommutativeRing, 'xyz')
    assert x*y == y*x
    assert x*2 == 2*x
    assert str(x*y) in ['x*y', 'y*x'],str(x*y)
    assert str(2*x) == '2*x', str(2*x)
    assert str(x*2) == '2*x', str(x*2)

    assert y*(2*x)==(y*2)*x
    assert str(y*(2*x)) in ['2*x*y','2*y*x'], str(y*(2*x))

    assert x*(y*z)==(x*y)*z
    assert str(x*y*z) in ['x*y*z','y*x*z'], str(x*y*z)

    assert (2*x)*(y*z)==(x*y)*(2*z)
    assert str((2*x)*(y*z)) in ['2*x*y*z', '2*y*x*z'], str((2*x)*(y*z))
    
    assert (y*x)*(y*z)==x*y*z*y
    assert (y*y)*(x*z)==x*y**2*z
    assert str(x*y*z*y) in ['y**2*x*z'], str(x*y*z*y)

    assert (y*y)*y==y*(y*y)
    assert (y*y)*(y*y)==y*(y*y)*y
    assert str(y*y*y)=='y**3',str(y*y*y)

    assert (x*x)*(y*y)==x*(x*y)*y
    assert str((x*x)*(y*y))=='y**2*x**2',str((x*x)*(y*y))
