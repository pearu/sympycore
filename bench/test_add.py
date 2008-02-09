
from random import randint
from sympycore import Symbol, Add
x = Symbol('x')
y = Symbol('y')

def test():
    Add(x,randint(0,10000000),y)

if __name__=='__main__':
    from func_timeit import Timer
    ops = Timer(test).smart_timeit()
    print 'Number of test calls per second:', int(ops)
