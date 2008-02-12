
from sympycore import Symbol, Number
x,y,z = map(Symbol,'xyz')
e1 = ((x+2*y+3*z)**50).expand()
e2 = ((x+2*y+3*z)**2).expand()

#print len(e1.data)/len(e2.data) -> 221

def test_long():
    """str(e), e = expand((x+2*y+3*z)**50)"""
    str(e1)

def test_short():
    """str(e), e = expand((x+2*y+3*z)**2), 221x"""
    n = 221
    while n:
        n -= 1
        str(e2)

if __name__=='__main__':
    from func_timeit import run_tests
    run_tests([test_long, test_short])
