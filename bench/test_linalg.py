START_REVISION=568

N = 5
try:
    from sympycore import MatrixRing
    a = MatrixRing[N,N].random()
    b = MatrixRing[N,N].random()
    c = MatrixRing[N,N].random((0,1))
    d = MatrixRing[N,N].random((0,1))
    m = MatrixRing[N,N].random()
except ImportError:
    from sympycore import MatrixBase
    a = MatrixBase.random(N, N)
    b = MatrixBase.random(N, N)
    c = MatrixBase.random(N, N, (0,1))
    d = MatrixBase.random(N, N, (0,1))
    m = MatrixBase.random(N, N)

for i in range(N):
    m[i,i] = 100 + i

def test_lu():
    """LU decomposition of a dense random matrix."""
    a.lu()

def test_inv():
    """Inverse of a dense random matrix."""
    m.inv()

def test_mul():
    """Multiply 5x5 random dense matrices."""
    a * b

def test_mul_sparse():
    """Multiply 5x5 random sparse matrices."""
    c * d


if __name__=='__main__':
    from func_timeit import run_tests
    run_tests([test_mul, test_mul_sparse, test_lu, test_inv])

