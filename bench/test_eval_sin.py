

from sympycore import sin, pi

def test():
    """ sin(n*pi/6), n=0...100
    """
    for n in xrange(101):
        sin(n*pi/6)


if __name__=='__main__':
    from func_timeit import Timer
    Timer(test).smart_timeit()
