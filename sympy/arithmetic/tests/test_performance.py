
def test_mul_performance():
    from time import clock
    from random import randint
    from sympy import Symbol, Mul, Add
    x = Symbol('x')
    y = Symbol('y')
    i = 1000
    t1 = clock()
    while i:
        i -= 1
        Mul(x,randint(0,1000000),y)
    t2 = clock()
    d1 = t2-t1

    from sympy import Symbol, Mul, Add
    x = Symbol('x')
    y = Symbol('y')
    i = 1000
    t1 = clock()
    while i:
        i -= 1
        Mul(x,randint(0,1000000),y)
    t2 = clock()
    d2 = t2-t1
    print '\ntiming Mul(x, <random int>, y): sandbox.core %s secs, sympy.core %s secs' % (d1,d2)

def test_add_performance():
    from time import clock
    from random import randint
    from sympy import Symbol, Mul, Add
    x = Symbol('x')
    y = Symbol('y')
    i = 1000
    t1 = clock()
    while i:
        i -= 1
        Add(x,randint(0,1000000),y)
    t2 = clock()
    d1 = t2-t1

    from sympy import Symbol, Mul, Add
    x = Symbol('x')
    y = Symbol('y')
    i = 1000
    t1 = clock()
    while i:
        i -= 1
        Add(x,randint(0,1000000),y)
    t2 = clock()
    d2 = t2-t1
    print '\ntiming Add(x, <random int>, y): sandbox.core %s secs, sympy.core %s secs' % (d1,d2)

def xtest_sum_performance():
    from time import clock
    from sympy import Symbol, MutableAdd, Integer
    x = Symbol('x')
    n = 500

    i = n
    s = Integer(0)    
    t1 = clock()
    while i:
        i -= 1
        s += x**i
    assert len(s)==n
    t2 = clock()
    d1 = t2-t1
    
    i = n
    s = MutableAdd()
    t1 = clock()
    while i:
        i -= 1
        s += x**i
    t2 = clock()
    s = s.canonical()
    assert len(s)==n
    d2 = t2-t1

    #from sympy.core import Symbol, Add
    #i = n
    #x = Symbol('x')
    #s = Add()
    #t1 = clock()
    #while i:
    #    i -= 1
    #    s += x**i
    #t2 = clock()
    #assert len(s)==n
    #d3 = t2-t1
    #print '\ntiming summation: sandbox.core(direct/MutableAdd) %s/%s secs, sympy.core %s secs' % (d1,d2,d3)

def xtest_expand_performance():
    from time import clock
    from sympy.core import sympify
    expr = '(x+z+y)**20 * (z+x)**9'
    e = sympify(expr)
    t1 = clock()
    e = e.expand()
    t2 = clock()
    d1 = t2-t1

    d2 = None
    if 0:
        from sympy import sympify
        expr = '(x+z+y)**10 * (z+x)**9'
        e = sympify(expr)
        t1 = clock()
        e = e.expand()
        t2 = clock()
        d2 = t2-t1
    print '\ntiming %r expand: sandbox.core %s secs, sympy.core %s secs' % (expr, d1, d2)

if __name__=='__main__':
    #test_mul_performance()
    #test_add_performance()
    #test_sum_performance()
    test_expand_performance()
