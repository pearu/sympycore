
from sympy import *

def test_union():
    assert Union(Set(1,2),Set(2,3))==Set(1,2,3)


def test_intersection():
    assert Intersection(Set(1,2),Set(2,3))==Set(2)

    
def test_minus():
    assert Minus(Set(1,2),Set(2,3))==Set(1)

def test_set_subset():
    assert Subset(Set(1,2), Set(1,2))==True
    assert Subset(Set(1,2), Set(1,2,3))==True
    assert Subset(Set(1,2), Set(1))==False

if __name__=='__main__':
    pass
