
from sympycore import Polyhedron

def test_Av98a():
    constraints = '''\
1+x1>=0
1+x2>=0
1-x1>=0
1-x2>=0
1-x1+x3>=0
1-x2+x3>=0
1+x1+x3>=0
1+x2+x3>=0'''
    p = Polyhedron(*constraints.split('\n'))
    p.show ()
    vertices = [(1,1,0),(-1,1,0),(1,-1,0),(-1,-1,0),(0,0,-1)]
    rays = [(0,0,1)]
