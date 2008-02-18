START_REVISION=473

from sympycore import Symbol, Add, Mul, Number
x,y,z = map(Symbol,'xyz')
a = Number(1,2)
b = Number(2,3)
c = Number(4,5)

def test_directadd5():
    """ evaluate 3*(1/2*x+2/3*y+4/5*z), 33x
    """
    n = 33
    while n:
        n -= 1
        3*(a*x + b*y + c*z)

def test_Add():
    """ Add(x,i,y), i=0..100
    """
    n = 101
    while n:
        n -= 1
        Add(x,n,y)

def test_Add2():
    """ x+i+y, i=0..100
    """
    n = 101
    while n:
        n -= 1
        x + n + y

def test_Sub2():
    """ x-i-y, i=0..100
    """
    n = 101
    while n:
        n -= 1
        x - n - y

def test_Mul():
    """ Mul(x,i,y), i=0..100
    """
    n = 101
    while n:
        n -= 1
        Mul(x,n,y)

def test_Mul2():
    """ x*i*y, i=0..100
    """
    n = 101
    while n:
        n -= 1
        x * n * y

def test_Div2():
    """ x/i/y, i=0..100
    """
    n = 101
    while n:
        n -= 1
        x / n / y



if __name__=='__main__':
    from func_timeit import run_tests
    run_tests([test_Add, test_Add2, test_Sub2,
               test_Mul, test_Mul2, test_Div2,
               test_directadd5])

