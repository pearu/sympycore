
from sympycore import *

def test_Add():
    x = Symbol('x')
    y = Symbol('y')
    z = Symbol('z')
    assert Add()==0
    assert Add(x)==x
    assert isinstance(Add(x,y), classes.Add)==True

    assert Add(Add(x,y),z)==Add(x,y,z)

    e = Add(x,y,z)

def _test_TermCoeffDict():
    from sympy.arithmetic.operations import TermCoeffDict
    x = Symbol('x')
    y = Symbol('y')
    z = Symbol('z')
    
    d = TermCoeffDict(())
    assert repr(d)=='TermCoeffDict(())'
    assert d=={}
    assert d.canonical()==0

    assert TermCoeffDict((x,))=={x:1}
    assert TermCoeffDict((x,)).canonical()==x
    assert TermCoeffDict((x,Integer(2)))=={x:1,1:2}
    assert TermCoeffDict((x,Integer(2),y))=={x:1,1:2,y:1}
    assert TermCoeffDict((x,Integer(2),x))=={x:2,1:2}
    assert TermCoeffDict((x,Integer(2),x)).canonical()=={x:2,1:2}
    assert TermCoeffDict((Integer(2),Integer(3))).canonical()==5
    assert TermCoeffDict((x,x))=={x:2}
    assert TermCoeffDict((x,x)).canonical()==Mul(2,x)
    assert TermCoeffDict(({x:Integer(2)},))=={x:2}
    assert TermCoeffDict(((x,Integer(2)),))=={x:2}

    m = Mul(Integer(2),x)
    d = TermCoeffDict((x,Integer(2),x,y,z))
    d += (z,Integer(-1))
    assert d=={x:2,1:2,y:1,z:0}
    #assert d.args_flattened==None
    assert d.canonical()=={x:2,1:2,y:1}
    #assert d.args_flattened==None
    assert set(list(d))==set([m,2,y])
    assert d.args_flattened!=None
    assert set(list(d.args_flattened))==set([m,2,y])

    a = Add(x,y)
    assert TermCoeffDict((a,))=={x:1,y:1}
    assert TermCoeffDict(((a,Integer(2)),))=={x:2,y:2}
    assert TermCoeffDict((m,))=={x:2}

def test_oo_nan():
    assert Add(oo,0)==oo
    assert Add(oo,1)==oo
    assert Add(oo,-1)==oo
    assert Add(-oo,1)==-oo
    assert Add(-oo,-1)==-oo
    assert Add(oo,-oo)==nan
    assert Add(oo,nan)==nan
    assert Add(2,nan)==nan
    assert Mul(oo,2)==oo
    assert Mul(oo,1)==oo
    assert Mul(oo,-2)==-oo
    assert Mul(oo,-1)==-oo
    assert Mul(-oo,2)==-oo
    assert Mul(-oo,1)==-oo
    assert Mul(-oo,-2)==oo
    assert Mul(-oo,-1)==oo
    assert Mul(oo,0)==nan
    assert Mul(2,nan)==nan
    assert Mul(oo,oo)==oo
    assert Mul(oo,-oo)==-oo

def main():
    test_TermCoeffDict()

def profile():
    import hotshot, hotshot.stats
    fn = "/tmp/%s.prof" % (__name__)
    prof = hotshot.Profile(fn)
    prof.runcall(main)
    prof.close()
    stats = hotshot.stats.load(fn)
    for func, (cc, nc, tt, ct, callers) in stats.stats.items():
        break
        if func[0].startswith('compiler'):
            stats.stats.pop(func)
    stats.strip_dirs()
    stats.sort_stats('calls', 'time')
    stats.print_stats(40)

if __name__=='__main__':
    profile()
