from random import randint
from sympycore import Symbol, Mul
x = Symbol('x')
y = Symbol('y')

def test():
    """Mul(x,randint(0,10000000),y)"""
    Mul(x,randint(0,10000000),y)

if __name__=='__main__':
    from func_timeit import Timer
    Timer(test).smart_timeit()

