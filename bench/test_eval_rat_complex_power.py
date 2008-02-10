

from sympycore import I
e = 2 + 3*I/4

def test():
    """ evaluate (2+3/4*I)**1000
    """
    e ** 1000

if __name__=='__main__':
    from func_timeit import Timer
    Timer(test).smart_timeit()
