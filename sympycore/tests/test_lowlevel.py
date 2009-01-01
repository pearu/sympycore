
from sympycore.core import Expr
from sympycore.utils import NUMBER, SYMBOL, TERMS, FACTORS, MUL

class MyExpr(Expr):

    @classmethod
    def convert(cls, obj, typeerror=True):
        if isinstance(obj, cls):
            return obj
        if isinstance(obj, (int, long, float, complex)):
            return MyExpr(NUMBER, obj)
        if isinstance(obj, str):
            return MyExpr(SYMBOL, obj)
        if typeerror:
            raise TypeError('Cannot convert type %r to %r' % (type(obj), cls.__name__))
        return NotImplemented

    def __add__(self, other):
        return Add(self, self.convert(other))

    __radd__ = __add__

def Number(n):
    return MyExpr(NUMBER, n)
def Symbol(s):
    return MyExpr(SYMBOL, s)
def Add(x, y):
    d = {}
    if x==y:
        d[x] = 2
    else:
        d[x] = 1
        d[y] = 1
    return MyExpr(TERMS, d)

def test_equality_number():
    assert Number(1)==Number(1)
    assert Number(1)==Number(1L)
    assert Number(1)==1
    assert Number(1)==1.0
    assert Number(1.0)==1
    assert Number(1)==1.0+0j
    assert Number(1)==1L
    assert 1==Number(1)
    assert 1L==Number(1)
    assert 1==Number(1L)
    
    assert Number(1)!=Number(2)
    assert Number(1)!=Number(2L)
    assert Number(1)!=2
    assert Number(1)!=2L
    assert 2!=Number(1)

def test_equality_symbol():
    assert Symbol('x')==Symbol('x')
    assert Symbol('x')=='x'
    assert 'x'==Symbol('x')

    assert Symbol('x')!=Symbol('y')
    assert Symbol('x')!='y'
    assert 'x'!=Symbol('y')

def test_equality_add():
    x, y, z = map(Symbol,'xyz')
    assert x + y == y + x
    assert x + x == x + x
    assert x + y == (TERMS, {x:1, y:1})

    assert x + y != y + z
    assert x + y != x
    assert x + y != 'x'
    assert x + y != 1

def test_hash_number():
    assert hash(Number(1))==hash(1)
    assert hash(Number(-1))==hash(-1)
    assert hash(Number(1212424))==hash(1212424)
    assert hash(Number(-1212424))==hash(-1212424)

def test_hash_symbol():
    assert hash(Symbol('x'))==hash('x')
    assert hash(Symbol('y'))==hash('y')

def test_hash_dict_data():
    x, y, z = map(Symbol,'xyz')
    assert hash(x + y) == hash((TERMS, frozenset([(x,1),(y,1)])))

def test_hash_list_data():
    l = [1,2,3]
    e1 = MyExpr(MUL, l)
    assert e1.is_writable
    e2 = MyExpr(MUL, tuple(l))
    assert hash(e1)==hash(e2)
    assert not e1.is_writable
