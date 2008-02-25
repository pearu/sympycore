START_REVISION=300

from sympycore import Symbol, Add
x,y,z = map(Symbol,'xyz')

def test_sum():
    """ sum(x**i/i,i=1..400)
    """
    s = 0
    i = 401
    while i:
        s += x**i/i
        i -= 1

def test_inplace_sum():
    """ Add(x**i/i,i=1..400)
    """
    Add(*[x**i/i for i in xrange(1,401)])

if __name__=='__main__':
    from func_timeit import run_tests
    run_tests([test_sum, test_inplace_sum])

