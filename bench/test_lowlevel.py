START_REVISION=300

from sympycore import Number, Symbol, Calculus
x = Symbol('x')
y = Symbol('y')
z = Symbol('z')
w = Symbol('w')

s1 = ((x+y+z)**10).expand()
s2 = ((x+y+w)**10).expand()
two = Number(2)
assert two==2

# compute hashes of subexpressions
hash(s1)
hash(s2)

try:
    arg1, arg2 = s1.pair
except AttributeError:
    arg1, arg2 = s1.data, s1.head
    
def test_hash():
    """ hash(s), s = expand((x+y+z)**10)
    """
    hash(Calculus(arg1, arg2))

def test_compare_eq1():
    """ not not (s1 == s1), s1 = expand((x+y+z)**10), 20x
    """
    n = 20
    while n:
        not not (s1 == s1)
        n -= 1

def test_compare_eq2():
    """ not not (x == 'x'), 20x
    """
    n = 20
    while n:
        not not (x == 'x')
        n -= 1

def test_compare_eq3():
    """ not not (two == 2), 20x
    """
    n = 20
    while n:
        not not (two == 2)
        n -= 1
        
def test_compare_ne1():
    """ not not (s1 == s2), s1 = expand((x+y+z)**10), s2 = expand((x+y+w)**10), 20x
    """
    n = 20
    while n:
        not not (s1 == s2)
        n -= 1

def test_compare_ne2():
    """ not not (s1 == 1), s1 = expand((x+y+z)**10), 20x
    """
    n = 20
    while n:
        not not (s1 == 1)
        n -= 1

def test_compare_is():
    """ not not (s1 is s1), s1 = expand((x+y+z)**10), 20x
    """
    n = 20
    while n:
        not not (s1 is s1)
        n -= 1

if __name__=='__main__':
    from func_timeit import run_tests
    run_tests([test_hash, test_compare_eq1, test_compare_eq2,
               test_compare_eq3, test_compare_ne1, test_compare_ne2,
               test_compare_is])
