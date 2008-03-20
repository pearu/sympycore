
from sympycore import *

def test_Matrix1():
    a = Matrix(2)
    assert a.rows==2
    assert a.cols==2
    assert a.tolist()==[[0,0], [0,0]]

    a = Matrix([1,2])
    assert a.rows==2
    assert a.cols==1
    assert a.tolist()==[[1], [2]]

    a = Matrix([1,2], diagonal=True)
    assert a.rows==2
    assert a.cols==2
    assert a.tolist()==[[1,0], [0,2]]

    a = Matrix([0,1], permutation=True)
    assert a.rows==2
    assert a.cols==2
    assert a.tolist()==[[1,0], [0,1]]

    a = Matrix([1,0], permutation=True)
    assert a.rows==2
    assert a.cols==2
    assert a.tolist()==[[0,1], [1,0]]

    a = Matrix([1,[2]])
    assert a.rows==2
    assert a.cols==1
    assert a.tolist()==[[1], [2]]

    a = Matrix([[1,2], [3,4]])
    assert a.rows==2
    assert a.cols==2
    assert a.tolist()==[[1,2], [3,4]]

    a = Matrix([[1,2,3], [4,5,6]])
    assert a.rows==2
    assert a.cols==3
    assert a.tolist()==[[1,2,3], [4,5,6]]

def test_Matrix2():
    a = Matrix(2, 3)
    assert a.rows==2
    assert a.cols==3
    assert a.tolist()==[[0,0,0], [0,0,0]]

def test_Matrix3():
    a = Matrix(2, 3, {(0,0):1, (1,2):2})
    assert a.rows==2
    assert a.cols==3
    assert a.tolist()==[[1,0,0], [0,0,2]]

def test_T():
    a = Matrix([[1,2], [3,4]]).T
    assert a.tolist()==[[1,3],[2,4]]

def test_get_items():
    a = Matrix([[1,2], [3,4]])
    assert a[0,0]==1
    assert a[0,1]==2
    assert a[1,0]==3
    assert a[1,1]==4
    assert a[0].tolist()==[[1,2]]
    assert a[1].tolist()==[[3,4]]
    assert a.T[0].tolist()==[[1,3]]
    assert a.T[1].tolist()==[[2,4]]
    assert a.T[0].T.tolist()==[[1],[3]]
    assert a.T[1].T.tolist()==[[2],[4]]

def test_get_row_slice():
    a = Matrix([[1,2], [3,4]])
    assert a[:].tolist()==[[1,2], [3,4]]
    assert a[:2].tolist()==[[1,2], [3,4]]
    assert a[:1].tolist()==[[1,2]]
    assert a[1:2].tolist()==[[3,4]]
    assert a[1:].tolist()==[[3,4]]
    assert a[:-1].tolist()==[[1,2]]

def test_get_column_slice():
    a = Matrix([[1,2], [3,4]])
    assert a[:,0].tolist()==[[1],[3]]
    assert a[:,1].tolist()==[[2],[4]]
    assert a[:,:].tolist()==[[1,2],[3,4]]

def test_get_slice():
    a = Matrix([[1,2,3], [4,5,6], [7,8,9]])
    assert a[:2,:2].tolist()==[[1,2],[4,5]]
    assert a[1:,1:].tolist()==[[5,6],[8,9]]
    assert a.T[:2,:2].tolist()==[[1,4],[2,5]]
    assert a[:2,1:].tolist()==[[2,3],[5,6]]

def test_set_item():
    a = Matrix(3,3)
    a[0,0] = 1
    a[0,1] = 2
    a[0,2] = 3
    assert a.tolist()==[[1,2,3],[0,0,0],[0,0,0]]

    a = Matrix(3,3)
    a[0,:] = [[1,2,3]]
    a[2,:] = [[7,8,9]]
    assert a.tolist()==[[1,2,3],[0,0,0],[7,8,9]]

    a = Matrix(3,3)
    a.T[0,:] = [[1,2,3]]
    a.T[2,:] = [[7,8,9]]
    assert a.tolist()==[[1,0,7],[2,0,8],[3,0,9]]

    a = Matrix(3,3)
    a[:,0] = [[1],2,3]
    a[:,2] = [[7],8,9]
    assert a.tolist()==[[1,0,7],[2,0,8],[3,0,9]]

    a = Matrix(3,3)
    b = Matrix([[1,2,3],[7,8,9]])
    a[::2] = b
    assert a.tolist()==[[1,2,3],[0,0,0],[7,8,9]]
    a[:2,:] = 0*b
    assert a.tolist()==[[0,0,0],[0,0,0],[7,8,9]]
    a.T[0,:] = [[1,0,0]]
    assert a.tolist()==[[1,0,0],[0,0,0],[0,8,9]]
    
    a = Matrix([[1,2],[3,4]])
    a.T[1,0] = 22
    a.T[0,1] = 0
    assert a.tolist()==[[1,22],[0,4]]
    a.T[0,1] = 0
    assert a.tolist()==[[1,22],[0,4]]

    a = Matrix([[1,2,3],[4,5,6],[7,8,9]])
    a[:2,:2] = 11
    assert a.tolist()==[[11,11,3],[11,11,6],[7,8,9]]
    a[1:,:] = 0
    assert a.tolist()==[[11,11,3],[0,0,0],[0,0,0]]
    a[:,:1] = 0
    assert a.tolist()==[[0,11,3],[0,0,0],[0,0,0]]
    a.T[::2,1] = 22
    assert a.tolist()==[[0,11,3],[22,0,22],[0,0,0]]
    a.T[:,0] = 0
    assert a.tolist()==[[0,0,0],[22,0,22],[0,0,0]]
    a.T[:1,:] = 0
    assert a.tolist()==[[0,0,0],[0,0,22],[0,0,0]]
    
def test_iadd():
    a = a2 = Matrix([[1,2], [3,4]])
    a += 1
    assert a.tolist()==[[2,3],[4,5]]
    assert a.data is a2.data

    a = a2 = Matrix([[1,2], [3,4]])
    hash(a)
    a += 1
    assert a.tolist()==[[2,3],[4,5]]
    assert a2.tolist()==[[1,2],[3,4]]
    assert a.data is not a2.data

    a = a2 = Matrix([[1,2], [3,4]])
    b = Matrix([[1,-2], [-3,4]])
    a += b
    assert a.tolist()==[[2,0],[0,8]]
    assert a.data is a2.data

    a = a2 = Matrix([[1,2], [3,4]])
    b = Matrix([[1,-2], [-3,4]])
    hash(a)
    a += b
    assert a.tolist()==[[2,0],[0,8]]
    assert a2.tolist()==[[1,2],[3,4]]
    assert a.data is not a2.data

    a = 1
    a2 = Matrix([[1,2], [3,4]])
    a += a2
    assert a.tolist()==[[2,3],[4,5]]

    a += a.T
    assert a.tolist()==[[4,7],[7,10]]

def test_add():
    a = Matrix([[1,2], [3,4]])
    assert (a+1).tolist()==[[2,3],[4,5]]
    assert (1+a).tolist()==[[2,3],[4,5]]

    b = Matrix([[1,-2], [-3,4]])
    assert (a+b).tolist()==[[2,0],[0,8]]

def test_isub():
    a = a2 = Matrix([[1,2], [3,4]])
    a -= 1
    assert a.tolist()==[[0,1],[2,3]]
    assert a.data is a2.data

    b = Matrix([[1,-2], [-3,4]])
    a -= b
    assert a.tolist()==[[-1,3],[5,-1]]
    assert a.data is a2.data

    a -= a.T
    assert a.tolist()==[[0,-2],[2,0]]
    assert a.data is a2.data

def test_sub():
    a = Matrix([[1,2],[3,4]])
    assert (1-a).tolist()==[[0,-1],[-2,-3]]
    assert (a-1).tolist()==[[0,1],[2,3]]
    b = Matrix([[3,4],[1,2]])
    assert (a-b).tolist()==[[-2,-2],[2,2]]
    
def test_posneg():
    a = Matrix([[1,2], [3,4]])
    assert (+a).tolist() == [[1,2],[3,4]]
    assert (-a).tolist() == [[-1,-2],[-3,-4]]

def test_imul():
    a = a2 = Matrix([[1,2], [3,4]])
    a *= 2
    assert a.tolist() == [[2,4],[6,8]]
    assert a.data is a2.data

    a = a2 = Matrix([[1,2], [3,4]])
    hash(a)
    a *= 2
    assert a.tolist() == [[2,4],[6,8]]
    assert a2.tolist() == [[1,2],[3,4]]
    assert a.data is not a2.data

    a = a2 = Matrix([[1,2], [3,4]])
    a *= a
    assert a.tolist()==[[7,10],[15,22]]
    assert a2.tolist() == [[1,2],[3,4]]

    a = a2 = Matrix([[1,2], [3,4]])
    a *= a.A
    assert a.tolist()==[[1,4],[9,16]]
    assert a.data is a2.data

    a = a2 = Matrix([[1,2], [3,4]])
    hash(a)
    a *= a.A
    assert a.tolist()==[[1,4],[9,16]]
    assert a2.tolist()==[[1,2],[3,4]]
    assert a.data is not a2.data

def test_mul():
    a = Matrix([[1,2], [3,4]])
    assert (a*a).tolist() == [[7,10],[15,22]]
    assert (a.A*a).tolist() == [[1,4],[9,16]]
    assert (a*a.A).tolist() == [[1,4],[9,16]]
    assert (a*a.T).tolist() == [[5,11],[11,25]]
    assert (a.T*a).tolist() == [[10,14],[14,20]]
    assert (a.T*a.T).tolist() == [[7,15],[10,22]]
    assert (a.A*a.T).tolist() == [[1,6],[6,16]]
    assert (a*a.T.A).tolist() == [[1,6],[6,16]]

    assert (a*2).tolist() == [[2,4],[6,8]]
    assert (2*a).tolist() == [[2,4],[6,8]]

def test_views():
    a = Matrix([[1,2], [3,4]])
    assert not a.head.is_array
    assert not a.M.head.is_array
    assert a.A.head.is_array
    b = a.A
    assert b.A is b

def test_trace():
    assert Matrix([[1,3],[6,9]]).trace() == 10
    assert Matrix([[1,2,3],[4,5,6],[7,8,9]]).trace() == 15
    b = Matrix(10000, 10000)
    assert b.trace() == 0
    b[100,100] = 3
    b[1000,1000] = 4
    assert b.trace() == 7

def test_solve():
    assert Matrix([[1,2],[3,4]]).solve([1,2]).tolist()==[[0],[mpq((1,2))]]
    assert Matrix([[1,2],[3,4]]).solve([2,1]).tolist()==[[-3],[mpq((5,2))]]

    while 1:
        m = Matrix(3,3,random=True)
        if m.det():
            break

    b = Matrix(3,1,random=True)
    assert m * (m//b) == b
    
    b = Matrix(3,2,random=True)
    assert m * (m//b) == b

    b = Matrix(3,15,random=True)
    assert m * (m//b) == b

    while 1:
        m = Matrix(5,5,random=True)
        if m.det():
            break

    b = Matrix(5,1,random=True)
    assert m * (m//b) == b
    
    b = Matrix(5,2,random=True)
    assert m * (m//b) == b

    b = Matrix(5,15,random=True)
    assert m * (m//b) == b

def test_resize():

    m = Matrix([[1,2],[3,4]])
    assert m.resize(3,3).tolist()==[[1,2,0],[3,4,0],[0,0,0]]

    m = Matrix([[1,2],[3,4]])
    assert m.resize(2,3).tolist()==[[1,2,0],[3,4,0]]

    m = Matrix([[1,2],[3,4]])
    assert m.resize(2,1).tolist()==[[1],[3]]

    m = Matrix([[1,2],[3,4]])
    assert m.resize(2,1).resize(2,2).tolist()==[[1,2],[3,4]]

    m = Matrix([[1,2],[3,4]])
    assert m.resize(2,1).crop().resize(2,2).tolist()==[[1,0],[3,0]]
    assert m.tolist()==[[1,0],[3,0]]
