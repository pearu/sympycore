
from sympycore.core import Expr, Pair, heads
from sympycore.heads import NUMBER, SYMBOL, TERMS, FACTORS, MUL, ADD, TERM_COEFF

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

class AExpr(Expr):

    pass

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

    assert MyExpr(SYMBOL, 'x')==AExpr(SYMBOL, 'x')

def test_equality_add():
    x, y, z = map(Symbol,'xyz')
    assert x + y == y + x
    assert x + x == x + x
    assert x + y == (TERMS, {x:1, y:1})

    assert x + y != y + z
    assert x + y != x
    assert x + y != 'x'
    assert x + y != 1

    assert MyExpr(ADD,[])==0
    assert MyExpr(ADD,[x])==x
    assert (not not MyExpr(ADD,[])) == False

    x1 = AExpr(SYMBOL, 'x')
    y1 = AExpr(SYMBOL, 'y')

    assert AExpr(ADD,[x1])==MyExpr(ADD,[x])
    assert AExpr(ADD,[x1,y1])==MyExpr(ADD,[x,y])
    assert not (AExpr(ADD,[x1,y1])<MyExpr(ADD,[x,y]))
    assert not (AExpr(ADD,[x1,y1])>MyExpr(ADD,[x,y]))

    assert (AExpr(ADD,[x1,y1])<=MyExpr(ADD,[x,y]))
    assert (AExpr(ADD,[x1,y1])>=MyExpr(ADD,[x,y]))

def test_equality_mul():
    x, y, z = map(Symbol,'xyz')
    assert (not not MyExpr(MUL,[])) == True
    assert MyExpr(MUL,[])==1
    assert MyExpr(MUL,[x])==x

def test_equality_term_coeff():
    x, y, z = map(Symbol,'xyz')
    assert MyExpr(TERM_COEFF, (x, 0))==0
    assert MyExpr(TERM_COEFF, (x, 1))==x
    assert MyExpr(TERM_COEFF, (1, 2))==2

def test_equality_term_coeff_dict():
    x, y, z = map(Symbol,'xyz')
    assert MyExpr(heads.TERM_COEFF_DICT, {})==0
    assert MyExpr(heads.TERM_COEFF_DICT, {x:0})==0
    assert MyExpr(heads.TERM_COEFF_DICT, {x:1})==x
    assert MyExpr(heads.TERM_COEFF_DICT, {x:2})==MyExpr(TERM_COEFF, (x, 2))
    assert MyExpr(heads.TERM_COEFF_DICT, {1:2})==2

def test_equality_pow():
    x, y, z = map(Symbol,'xyz')
    assert MyExpr(heads.POW, (x, 0))==1
    assert MyExpr(heads.POW, (x, 1))==x
    assert MyExpr(heads.POW, (1, x))==1

def test_equality_base_exp_dict():
    x, y, z = map(Symbol,'xyz')
    assert MyExpr(heads.BASE_EXP_DICT, {})==1
    assert MyExpr(heads.BASE_EXP_DICT, {x:0})==1
    assert MyExpr(heads.BASE_EXP_DICT, {x:1})==x
    assert MyExpr(heads.BASE_EXP_DICT, {x:2})==MyExpr(heads.POW, (x, 2))
    assert MyExpr(heads.BASE_EXP_DICT, {1:2})==1

def test_hash_number():
    assert hash(Number(1))==hash(1)
    assert hash(Number(-1))==hash(-1)
    assert hash(Number(1212424))==hash(1212424)
    assert hash(Number(-1212424))==hash(-1212424)

def test_hash_symbol():
    assert hash(Symbol('x'))==hash('x'),`hash(Symbol('x')),hash('x')`
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

def test_is_writable():
    assert MyExpr(MUL, [1,2]).is_writable
    assert not MyExpr(MUL, (1,2)).is_writable
    assert not MyExpr(MUL, Pair(1,2)).is_writable
    assert MyExpr(MUL, Pair(1,[2])).is_writable
    assert not MyExpr(MUL, Pair(1,(1,2))).is_writable
    
