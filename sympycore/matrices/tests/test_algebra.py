
from sympycore import *

def test_Matrix1():
    a = Matrix(2)
    assert a.rows==2
    assert a.cols==2
    assert a.tolist()==[[0,0], [0,0]]

    a = Matrix([1,2])
    assert a.rows==2
    assert a.cols==2
    assert a.tolist()==[[1,0], [0,2]]

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
    
def test_iadd():
    a = a2 = Matrix([[1,2], [3,4]])
    a += 1
    assert a.tolist()==[[2,3],[4,5]]
    assert a is a2

    a = a2 = Matrix([[1,2], [3,4]])
    hash(a)
    a += 1
    assert a.tolist()==[[2,3],[4,5]]
    assert a2.tolist()==[[1,2],[3,4]]
    assert a is not a2

    a = a2 = Matrix([[1,2], [3,4]])
    b = Matrix([[1,-2], [-3,4]])
    a += b
    assert a.tolist()==[[2,0],[0,8]]
    assert a is a2

    a = a2 = Matrix([[1,2], [3,4]])
    b = Matrix([[1,-2], [-3,4]])
    hash(a)
    a += b
    assert a.tolist()==[[2,0],[0,8]]
    assert a2.tolist()==[[1,2],[3,4]]
    assert a is not a2

    a = 1
    a2 = Matrix([[1,2], [3,4]])
    a += a2
    assert a.tolist()==[[2,3],[4,5]]

def test_add():
    a = Matrix([[1,2], [3,4]])
    assert (a+1).tolist()==[[2,3],[4,5]]
    assert (1+a).tolist()==[[2,3],[4,5]]

    b = Matrix([[1,-2], [-3,4]])
    assert (a+b).tolist()==[[2,0],[0,8]]

def test_neg():
    a = Matrix([[1,2], [3,4]])
    assert (-a).tolist() == [[-1,-2],[-3,-4]]

def test_imul():
    a = a2 = Matrix([[1,2], [3,4]])
    a *= 2
    assert a.tolist() == [[2,4],[6,8]]
    assert a is a2

    a = a2 = Matrix([[1,2], [3,4]])
    hash(a)
    a *= 2
    assert a.tolist() == [[2,4],[6,8]]
    assert a2.tolist() == [[1,2],[3,4]]
    assert a is not a2

    a = a2 = Matrix([[1,2], [3,4]])
    a *= a
    assert a.tolist()==[[7,10],[15,22]]
    assert a2.tolist() == [[1,2],[3,4]]

    a = a2 = Matrix([[1,2], [3,4]])
    a *= a.A
    assert a.tolist()==[[1,4],[9,16]]
    assert a is a2

    a = a2 = Matrix([[1,2], [3,4]])
    hash(a)
    a *= a.A
    assert a.tolist()==[[1,4],[9,16]]
    assert a2.tolist()==[[1,2],[3,4]]
    assert a is not a2

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

