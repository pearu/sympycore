
from sympycore import CommutativeRing, heads, Expr

def test_add():
    x,y,z = map(CommutativeRing, 'xyz')
    assert x+y == y+x
    assert x+2 == 2+x
    assert str(x+y) in ['x + y', 'y + x'],str(x+y)
    assert str(2+x) in ['2 + x', 'x + 2'], str(2+x)

def test_mul():
    x,y,z = map(CommutativeRing, 'xyz')
    assert x*y == y*x
    assert x*2 == 2*x
    assert str(x*y) in ['x*y', 'y*x'],str(x*y)
    assert str(2*x) == '2*x', str(2*x)
    assert str(x*2) == '2*x', str(x*2)

    assert y*(2*x)==(y*2)*x
    assert str(y*(2*x)) in ['2*x*y','2*y*x'], str(y*(2*x))

    assert x*(y*z)==(x*y)*z
    assert str(x*y*z) in ['x*y*z','y*x*z'], str(x*y*z)

    assert (2*x)*(y*z)==(x*y)*(2*z)
    assert str((2*x)*(y*z)) in ['2*x*y*z', '2*y*x*z'], str((2*x)*(y*z))
    
    assert (y*x)*(y*z)==x*y*z*y
    assert (y*y)*(x*z)==x*y**2*z
    assert str(x*y*z*y) in ['y**2*x*z'], str(x*y*z*y)

    assert (y*y)*y==y*(y*y)
    assert (y*y)*(y*y)==y*(y*y)*y
    assert str(y*y*y)=='y**3',str(y*y*y)

    assert (x*x)*(y*y)==x*(x*y)*y
    assert str((x*x)*(y*y))=='y**2*x**2',str((x*x)*(y*y))

commutative_operations_results = '''\
(1)+(2):3
(1)-(2):-1
(1)*(2):2
(1)/(2):1/2
(1)**(2):1
(1)+(x):x + 1
(1)-(x):-x + 1
(1)*(x):x
(1)/(x):1/x
(1)**(x):1
(1)+(2*x):2*x + 1
(1)-(2*x):-2*x + 1
(1)*(2*x):2*x
(1)/(2*x):1/2/x
(1)**(2*x):1
(1)+(y + x):y + x + 1
(1)-(y + x):-y - x + 1
(1)*(y + x):y + x
(1)/(y + x):1/(y + x)
(1)**(y + x):1
(1)+(x**2):1 + x**2
(1)-(x**2):1 - x**2
(1)*(x**2):x**2
(1)/(x**2):1/x**2
(1)**(x**2):1
(1)+(y*x):1 + y*x
(1)-(y*x):1 - y*x
(1)*(y*x):y*x
(1)**(y*x):1
+(2):2
-(2):-2
(2)+(1):3
(2)-(1):1
(2)*(1):2
(2)/(1):2
(2)**(1):2
(2)+(2):4
(2)-(2):0
(2)*(2):4
(2)/(2):1
(2)**(2):4
(2)+(x):2 + x
(2)-(x):-x + 2
(2)*(x):2*x
(2)/(x):2/x
(2)**(x):2**x
(2)+(2*x):2*x + 2
(2)-(2*x):-2*x + 2
(2)*(2*x):4*x
(2)/(2*x):1/x
(2)**(2*x):2**(2*x)
(2)+(y + x):y + x + 2
(2)-(y + x):-y - x + 2
(2)*(y + x):2*y + 2*x
(2)/(y + x):2/(y + x)
(2)**(y + x):2**(y + x)
(2)+(x**2):2 + x**2
(2)-(x**2):2 - x**2
(2)*(x**2):2*x**2
(2)/(x**2):2/x**2
(2)**(x**2):2**x**2
(2)+(y*x):2 + y*x
(2)-(y*x):2 - y*x
(2)*(y*x):2*y*x
(2)**(y*x):2**(y*x)
+(x):x
-(x):-x
(x)+(1):x + 1
(x)-(1):x - 1
(x)*(1):x
(x)/(1):x
(x)**(1):x
(x)+(2):x + 2
(x)-(2):x - 2
(x)*(2):2*x
(x)/(2):1/2*x
(x)**(2):x**2
(x)+(x):2*x
(x)-(x):0
(x)*(x):x**2
(x)/(x):1
(x)**(x):x**x
(x)+(2*x):3*x
(x)-(2*x):-x
(x)*(2*x):2*x**2
(x)/(2*x):1/2
(x)**(2*x):x**(2*x)
(x)+(y + x):y + 2*x
(x)-(y + x):-y
(x)*(y + x):x*(y + x)
(x)/(y + x):x/(y + x)
(x)**(y + x):x**(y + x)
(x)+(x**2):x + x**2
(x)-(x**2):x - x**2
(x)*(x**2):x**3
(x)/(x**2):1/x
(x)**(x**2):x**x**2
(x)+(y*x):x + y*x
(x)-(y*x):x - y*x
(x)*(y*x):y*x**2
(x)/(y*x):1/y
(x)**(y*x):x**(y*x)
+(2*x):2*x
-(2*x):-2*x
(2*x)+(1):2*x + 1
(2*x)-(1):2*x - 1
(2*x)*(1):2*x
(2*x)/(1):2*x
(2*x)**(1):2*x
(2*x)+(2):2*x + 2
(2*x)-(2):2*x - 2
(2*x)*(2):4*x
(2*x)/(2):x
(2*x)**(2):4*x**2
(2*x)+(x):3*x
(2*x)-(x):x
(2*x)*(x):2*x**2
(2*x)/(x):2
(2*x)**(x):(2*x)**x
(2*x)+(2*x):4*x
(2*x)-(2*x):0
(2*x)*(2*x):4*x**2
(2*x)/(2*x):1
(2*x)**(2*x):(2*x)**(2*x)
(2*x)+(y + x):y + 3*x
(2*x)-(y + x):-y + x
(2*x)*(y + x):2*x*(y + x)
(2*x)/(y + x):2*x/(y + x)
(2*x)**(y + x):(2*x)**(y + x)
(2*x)+(x**2):2*x + x**2
(2*x)-(x**2):2*x - x**2
(2*x)*(x**2):2*x**3
(2*x)/(x**2):2/x
(2*x)**(x**2):(2*x)**x**2
(2*x)+(y*x):2*x + y*x
(2*x)-(y*x):2*x - y*x
(2*x)*(y*x):2*y*x**2
(2*x)/(y*x):2/y
(2*x)**(y*x):(2*x)**(y*x)
+(y + x):y + x
-(y + x):-y - x
(y + x)+(1):y + x + 1
(y + x)-(1):y + x - 1
(y + x)*(1):y + x
(y + x)/(1):y + x
(y + x)**(1):y + x
(y + x)+(2):y + x + 2
(y + x)-(2):y + x - 2
(y + x)*(2):2*y + 2*x
(y + x)/(2):1/2*y + 1/2*x
(y + x)**(2):(y + x)**2
(y + x)+(x):y + 2*x
(y + x)-(x):y
(y + x)*(x):x*(y + x)
(y + x)/(x):1/x*(y + x)
(y + x)**(x):(y + x)**x
(y + x)+(2*x):y + 3*x
(y + x)-(2*x):y - x
(y + x)*(2*x):2*x*(y + x)
(y + x)/(2*x):1/2/x*(y + x)
(y + x)**(2*x):(y + x)**(2*x)
(y + x)+(y + x):2*y + 2*x
(y + x)-(y + x):0
(y + x)*(y + x):(y + x)**2
(y + x)/(y + x):1
(y + x)**(y + x):(y + x)**(y + x)
(y + x)+(x**2):y + x + x**2
(y + x)-(x**2):y + x - x**2
(y + x)*(x**2):x**2*(y + x)
(y + x)/(x**2):1/x**2*(y + x)
(y + x)**(x**2):(y + x)**x**2
(y + x)+(y*x):y + x + y*x
(y + x)-(y*x):y + x - y*x
(y + x)*(y*x):y*x*(y + x)
(y + x)/(y*x):1/y/x*(y + x)
(y + x)**(y*x):(y + x)**(y*x)

+(x**2):x**2
-(x**2):-x**2
(x**2)+(1):1 + x**2
(x**2)-(1):-1 + x**2
(x**2)*(1):x**2
(x**2)/(1):x**2
(x**2)**(1):x**2
(x**2)+(2):2 + x**2
(x**2)-(2):-2 + x**2
(x**2)*(2):2*x**2
(x**2)/(2):1/2*x**2
(x**2)**(2):x**4
(x**2)+(x):x + x**2
(x**2)-(x):-x + x**2
(x**2)*(x):x**3
(x**2)/(x):x
(x**2)**(x):(x**2)**x
(x**2)+(2*x):2*x + x**2
(x**2)-(2*x):-2*x + x**2
(x**2)*(2*x):2*x**3
(x**2)/(2*x):1/2*x
(x**2)**(2*x):(x**2)**(2*x)
(x**2)+(y + x):y + x + x**2
(x**2)-(y + x):-y - x + x**2
(x**2)*(y + x):x**2*(y + x)
(x**2)/(y + x):x**2/(y + x)
(x**2)**(y + x):(x**2)**(y + x)
(x**2)+(x**2):2*x**2
(x**2)-(x**2):0
(x**2)*(x**2):x**4
(x**2)/(x**2):1
(x**2)**(x**2):(x**2)**x**2
(x**2)+(y*x):y*x + x**2
(x**2)-(y*x):-y*x + x**2
(x**2)*(y*x):y*x**3
(x**2)/(y*x):x/y;1/y*x
(x**2)**(y*x):(x**2)**(y*x)
+(y*x):y*x
-(y*x):-y*x
(y*x)+(1):1 + y*x
(y*x)-(1):-1 + y*x
(y*x)*(1):y*x
(y*x)/(1):y*x
(y*x)**(1):y*x
(y*x)+(2):2 + y*x
(y*x)-(2):-2 + y*x
(y*x)*(2):2*y*x
(y*x)/(2):1/2*y*x
(y*x)**(2):y**2*x**2
(y*x)+(x):x + y*x
(y*x)-(x):-x + y*x
(y*x)*(x):y*x**2
(y*x)/(x):y
(y*x)**(x):(y*x)**x
(y*x)+(2*x):2*x + y*x
(y*x)-(2*x):-2*x + y*x
(y*x)*(2*x):2*y*x**2
(y*x)**(2*x):(y*x)**(2*x)
(y*x)+(y + x):y + x + y*x
(y*x)-(y + x):-y - x + y*x
(y*x)*(y + x):y*x*(y + x)
(y*x)**(y + x):(y*x)**(y + x)
(y*x)+(x**2):y*x + x**2
(y*x)-(x**2):y*x - x**2
(y*x)*(x**2):y*x**3
(y*x)/(x**2):y/x
(y*x)**(x**2):(y*x)**x**2
(y*x)+(y*x):2*y*x
(y*x)-(y*x):0
(y*x)*(y*x):y**2*x**2
(y*x)/(y*x):1
(y*x)**(y*x):(y*x)**(y*x)
(1)/(y*x):1/y/x
(2)/(y*x):2/y/x
(y*x)/(2*x):1/2*y
(y*x)/(y + x):y*x/(y + x)
'''

def test_commutative_operations():
    Ring = CommutativeRing
    x,y,z = map(Ring, 'xyz')
    operands = [1,
                Ring(heads.NUMBER, 2),
                x,
                Ring(heads.TERM_COEFF, (x, 2)), # 2*x
                Ring(heads.TERM_COEFF_DICT, {x:1, y:1}), # x+y
                Ring(heads.POW, (x, 2)), # x**2
                Ring(heads.BASE_EXP_DICT, {x:1, y:1}), # x*y
                ]
    unary_operations = ['+', '-']
    binary_operations = ['+', '-', '*', '/', '**']
    results = {}
    for line in commutative_operations_results.split('\n'):
        line = line.strip()
        if ':' not in line: continue
        expr, result = line.split(':')
        for e in expr.split(';'):
            e = e.strip()
            results[e] = [r.strip() for r in result.split(';')]

    for op1 in operands:
        if isinstance(op1, Expr):
            for op in unary_operations:
                expr = '%s(%s)' % (op, op1) 

                try:
                    result = str(eval('%s(op1)' % (op)))
                except Exception, msg:
                    print  expr,'failed with %s' % (msg)
                    raise
                
                if expr not in results:
                    print '%s:%s' % (expr, result)
                    continue
                assert result in results[expr], `results[expr], result`
        for op2 in operands:
            if not (isinstance(op1, Expr) or isinstance(op2, Expr)):
                continue
            for op in binary_operations:
                expr = '(%s)%s(%s)' % (op1, op, op2)

                try:
                    result = str(eval('(op1)%s(op2)' % op))
                except Exception, msg:
                    print  expr,'failed with %s' % (msg)
                    raise
                
                if expr not in results:
                    print '%s:%s' % (expr, result)
                    continue
                assert result in results[expr], `results[expr], result`
