

from sympycore import Symbol
x,y,z = map(Symbol,'xyz')
e = (x+z+y)**20 * (z+x)**9

def test():
    """ expand((x+z+y)**20 * (z+x)**9)
    """
    e.expand()

if __name__=='__main__':
    from func_timeit import Timer
    Timer(test).smart_timeit()
