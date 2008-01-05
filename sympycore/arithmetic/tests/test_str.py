#from sympy import Symbol, Rational, Derivative, I, log, Sqrt, exp
from sympycore import Symbol, Rational, Sqrt

x = Symbol('x')
y = Symbol('y')
z = Symbol('z')
w = Symbol('w')

def test_poly_str():
    #if any of these tests fails, it can still be correct, just the terms can
    #be in a different order. That happens for example when we change the 
    #hash algorithm. If it is correct, just add another item in the list [] of
    #correct results.

    s = str((2*x-(7*x**2 - 2) + 3*y))
    assert s in ["2 - 7*x**2 + 2*x + 3*y",
        "2 + 2*x + 3*y - 7*x**2", '3*y + 2*x - 7*x**2 + 2',
                                             '2 - 7*x**2 + 3*y + 2*x',
                                             '2 + 2*x + 3*y - 7*x**2',
                 '2 + 3*y + 2*x - 7*x**2','2 + 2*x - 7*x**2 + 3*y',
                 '2 + 3*y - 7*x**2 + 2*x',
                                             ],`s`

    assert str(x-y) in ["x - y", "-y + x"]
    assert str(2+-x) in ["2 - x", "-x + 2"]
    assert str(x-2) in ["x - 2", "(-2) + x", "-2 + x"]
    s = str(x-y-z-w)
    assert s in ["x - y - z - w",'x - z - y - w',
        "x - y - z - w","-w - y - z + x","x - w - y - z",
        "-w + x - y - z","-z - w - y + x","-y + x - w - z",
        '-y + x - z - w','x - w - z - y','x - y - w - z',
                 'x - z - w - y',
        ],`s`

    s = str(x-y-z-w)
    assert s in ["x - y - z - w",'x - z - y - w','x - w - z - y','x - w - z - y',
                 'x - z - w - y','x - y - w - z',
            "-w - y - z + x","x - w - y - z","-w + x - z - y","-y - w - z + x",
            "-y + x - z - w","-y + x - w - z","-w + x - y - z","-z - w - y +x"],`s`
    assert str(x-z*y**2*z*w) in ["-z**2*y**2*w + x", "x - w*y**2*z**2",
            "-y**2*z**2*w + x","x - w*z**2*y**2","x - y**2*z**2*w",
            "x - y**2*w*z**2","x - z**2*y**2*w","-w*z**2*y**2 + x",
            "-w*y**2*z**2 + x","x - z**2*w*y**2"]

def test_bug1():
    assert str(x-1*y*x*y) in ["x - x*y**2",'-x*y**2 + x',"x - y**2*x", '-y**2*x + x']

def test_bug2():
    e = x-y
    a = str(e)
    b = str(e)
    assert a == b

def test_bug3():
    x = Symbol("x")
    e = Sqrt(x)
    assert str(e) == "x**(1/2)"

def test_bug4():
    x = Symbol("x")
    w = Symbol("w")
    e = -2*Sqrt(x)-w/Sqrt(x)/2
    assert str(e) not in ["(-2)*x**1/2(-1/2)*x**(-1/2)*w",
            "-2*x**1/2(-1/2)*x**(-1/2)*w","-2*x**1/2-1/2*x**-1/2*w"]
    assert str(e) in ["-2*x**(1/2) - 1/2*x**(-1/2)*w", "-2*x**(1/2) - 1/2*w*x**(-1/2)", 
                      "-1/2*x**(-1/2)*w - 2*x**(1/2)", "-1/2*w*x**(-1/2) - 2*x**(1/2)",
                      "-2*x**(1/2) + (-1/2)*w*x**(-1/2)",
                      "-2*x**(1/2) - (1/2)*w*x**(-1/2)",
                      '-(1/2)*x**(-1/2)*w - 2*x**(1/2)'
                      ]

# XXX: derivative not implemented
def _test_Derivative():
    x = Symbol("x")
    y = Symbol("y")

    e = Derivative(x**2, x, evaluate=False)
    assert str(e) == "D(x**2, x)"

    e = Derivative(x**2/y, x, y, evaluate=False)
    assert str(e) == "D(x**2/y, x, y)"

# XXX: "/" printing not implemented
def xtest_pow():
    assert str(1/x) == "1/x"

# XXX: "/" printing not implemented
def xtest_x_div_y():
    x = Symbol("x")
    y = Symbol("y")
    assert str(x/y) == "x/y"
    assert str(y/x) == "y/x"
