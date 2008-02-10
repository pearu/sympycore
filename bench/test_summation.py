

from sympycore import Symbol
x,y,z = map(Symbol,'xyz')

def test():
    """ sum(x**i/i,i=1..400)
    """
    s = 0
    i = 401
    while i:
        s += x**i/i
        i -= 1

if __name__=='__main__':
    from func_timeit import Timer
    Timer(test).smart_timeit()
