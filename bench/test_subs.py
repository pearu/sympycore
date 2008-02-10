
from sympycore import Symbol, Number
x,y,z = map(Symbol,'xyz')
e = ((x+2*y+3*z)**20).expand()

def test():
    """e.subs(x,z).subs(y,z), e = expand((x+2*y+3*z)**20)"""
    e.subs(x,z).subs(y,z)

if __name__=='__main__':
    from func_timeit import Timer
    Timer(test).smart_timeit()
