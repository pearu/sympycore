START_REVISION=564

try:
    from sympycore import MatrixRing
    a = MatrixRing[15,20].random()
    b = MatrixRing[15,20].random()
    
    c = MatrixRing[15,20].random((0,1))
    d = MatrixRing[15,20].random((0,1))
except ImportError:
    from sympycore import MatrixBase
    a = MatrixBase.random(15,20)
    b = MatrixBase.random(15,20)

    c = MatrixBase.random(15,20,(0,1))
    d = MatrixBase.random(15,20,(0,1))


def test_neg():
    """Negate a 15x20 random dense matrix."""
    -a

def test_add():
    """Add two 15x20 random dense matricies."""
    a + b

def test_sub():
    """Substract two 15x20 random dense matricies."""
    a - b

def test_mul_coeff():
    """Multiply 15x20 random dense matrix with a number."""
    a * 3

def test_div_coeff():
    """Divide 15x20 random dense matrix with a number."""
    a / 3

def test_add_sparse():
    """Add two 15x20 random sparse int matricies."""
    c + d


if __name__=='__main__':
    from func_timeit import run_tests
    run_tests([test_neg, test_add, test_sub, test_mul_coeff, test_div_coeff,
               test_add_sparse])
