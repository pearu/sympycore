
from sympycore import Symbol, Number
x,y,z = map(Symbol,'xyz')
a = Number(1,2)
b = Number(2,3)
c = Number(4,5)

def test():
    """ evaluate 3*(1/2*x+2/3*y+4/5*z) 
    """
    3*(a*x + b*y + c*z)

if __name__=='__main__':
    from func_timeit import Timer
    Timer(test).smart_timeit()
