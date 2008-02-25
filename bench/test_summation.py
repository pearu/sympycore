START_REVISION=300

from sympycore import Symbol, Add
x,y,z = map(Symbol,'xyz')

def test_sum():
    """ sum(x**i/i,i=1..400)
    """
    s = 0
    i = 400
    while i:
        s += x**i/i
        i -= 1

def test_inplace_sum():
    """ Add(x**i/i,i=1..400)
    """
    Add(*[x**i/i for i in xrange(1,401)])

def test_sum40():
    """ sum(x**i/i,i=1..40), 10x
    """
    n = 10
    while n:
        s = 0
        i = 40
        while i:
            s += x**i/i
            i -= 1
        n -= 1

def test_inplace_sum40():
    """ Add(x**i/i,i=1..40), 10x
    """
    n = 10
    while n:
        Add(*[x**i/i for i in xrange(1,41)])
        n -= 1

def test_sum4():
    """ sum(x**i/i,i=1..4), 100x
    """
    n = 100
    while n:
        s = 0
        i = 4
        while i:
            s += x**i/i
            i -= 1
        n -= 1

def test_inplace_sum4():
    """ Add(x**i/i,i=1..4), 100x
    """
    n = 100
    while n:
        Add(*[x**i/i for i in xrange(1,5)])
        n -= 1

if __name__=='__main__':
    from func_timeit import run_tests
    run_tests([test_sum, test_inplace_sum,
               test_sum40, test_inplace_sum40,
               test_sum4, test_inplace_sum4,
               ])

