

from sympycore import sin, cos, pi, I

def test_sin():
    """ evaluate sin(n*pi/6), n=0...100
    """
    n = 101
    while n:
        n -= 1
        sin(n*pi/6)

def test_cos():
    """ evaluate cos(n*pi/6), n=0...100
    """
    n = 101
    while n:
        n -= 1
        cos(n*pi/6)


e = 2 + 3*I

def test_complex_power():
    """ evaluate (2+3*I)**1000, 10x
    """
    n = 10
    while n:
        n -= 1
        e ** 1000

re = 2 + 3*I/4

def test_rat_complex_power():
    """ evaluate (2+3/4*I)**1000, 1x
    """
    re ** 1000

if __name__=='__main__':
    from func_timeit import run_tests
    run_tests([test_sin, test_cos, test_complex_power, test_rat_complex_power], start_revision=418)
