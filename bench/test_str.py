
from sympycore import Symbol, Number
x,y,z = map(Symbol,'xyz')
e = ((x+2*y+3*z)**50).expand()

def test():
    """str(e), e = expand((x+2*y+3*z)**50)"""
    str(e)

if __name__=='__main__':
    from func_timeit import Timer
    Timer(test).smart_timeit()
