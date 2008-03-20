
from sympycore import *

def test_eye():
    assert eye(3).tolist()==[[1,0,0],[0,1,0],[0,0,1]]
    assert eye(3,2).tolist()==[[1,0],[0,1],[0,0]]
    assert eye(2,3).tolist()==[[1,0,0],[0,1,0]]

    assert eye(3,k=1).tolist()==[[0,1,0],[0,0,1],[0,0,0]]
    assert eye(3,k=2).tolist()==[[0,0,1],[0,0,0],[0,0,0]]
    assert eye(3,k=3).tolist()==[[0,0,0],[0,0,0],[0,0,0]]
    assert eye(3,k=-1).tolist()==[[0,0,0],[1,0,0],[0,1,0]]
