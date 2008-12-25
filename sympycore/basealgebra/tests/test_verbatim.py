
from sympycore import Verbatim, utils

def test_basic():
    a = Verbatim('a')
    assert Verbatim.convert('a')==a
    assert Verbatim.convert(a) == a

    assert repr(a) == "Verbatim(SYMBOL, 'a')"


def test_operations():
    a = Verbatim('a')
    b = Verbatim('b')
    c = Verbatim('c')
    assert +a == Verbatim('+a'),`+a,Verbatim('+a')`

    assert str(+a)=='+a',`str(+a)`
    assert repr(+a) == "Verbatim(POS, Verbatim(SYMBOL, 'a'))",repr(+a)
    assert repr(-a) == "Verbatim(NEG, Verbatim(SYMBOL, 'a'))",repr(-a)
    assert repr(~a) == "Verbatim(INVERT, Verbatim(SYMBOL, 'a'))",repr(~a)

    assert repr(a+b)== "Verbatim(ADD, (Verbatim(SYMBOL, 'a'), Verbatim(SYMBOL, 'b')))", repr(a+b)
    assert repr(a-b)== "Verbatim(SUB, (Verbatim(SYMBOL, 'a'), Verbatim(SYMBOL, 'b')))", repr(a-b)
    assert repr(a*b)== "Verbatim(MUL, (Verbatim(SYMBOL, 'a'), Verbatim(SYMBOL, 'b')))", repr(a*b)
    assert repr(a/b)== "Verbatim(DIV, (Verbatim(SYMBOL, 'a'), Verbatim(SYMBOL, 'b')))", repr(a/b)
    assert repr(a//b)== "Verbatim(FLOORDIV, (Verbatim(SYMBOL, 'a'), Verbatim(SYMBOL, 'b')))", repr(a//b)
    assert repr(a**b)== "Verbatim(POW, (Verbatim(SYMBOL, 'a'), Verbatim(SYMBOL, 'b')))", repr(a**b)
    assert repr(a%b)== "Verbatim(MOD, (Verbatim(SYMBOL, 'a'), Verbatim(SYMBOL, 'b')))", repr(a%b)
    assert repr(a|b)== "Verbatim(BOR, (Verbatim(SYMBOL, 'a'), Verbatim(SYMBOL, 'b')))", repr(a|b)
    assert repr(a&b)== "Verbatim(BAND, (Verbatim(SYMBOL, 'a'), Verbatim(SYMBOL, 'b')))", repr(a&b)
    assert repr(a^b)== "Verbatim(BXOR, (Verbatim(SYMBOL, 'a'), Verbatim(SYMBOL, 'b')))", repr(a^b)
    assert repr(a<<b)== "Verbatim(LSHIFT, (Verbatim(SYMBOL, 'a'), Verbatim(SYMBOL, 'b')))", repr(a<<b)
    assert repr(a>>b)== "Verbatim(RSHIFT, (Verbatim(SYMBOL, 'a'), Verbatim(SYMBOL, 'b')))", repr(a>>b)
    assert repr(divmod(a,b))== "Verbatim(DIVMOD, (Verbatim(SYMBOL, 'a'), Verbatim(SYMBOL, 'b')))", repr(divmod(a,b))
    assert repr(a(b))== "Verbatim(APPLY, (Verbatim(SYMBOL, 'a'), Verbatim(SYMBOL, 'b')))", repr(a(b))
    assert repr(a())== "Verbatim(APPLY, (Verbatim(SYMBOL, 'a'),))", repr(a())
    assert repr(Verbatim('a and b'))=="Verbatim(AND, (Verbatim(SYMBOL, 'a'), Verbatim(SYMBOL, 'b')))", repr(Verbatim('a and b'))
    assert repr(Verbatim('a or b'))=="Verbatim(OR, (Verbatim(SYMBOL, 'a'), Verbatim(SYMBOL, 'b')))", repr(Verbatim('a or b'))
    assert repr(Verbatim('a in b'))=="Verbatim(IN, (Verbatim(SYMBOL, 'a'), Verbatim(SYMBOL, 'b')))", repr(Verbatim('a in b'))
    assert repr(Verbatim('a not in b'))=="Verbatim(NOTIN, (Verbatim(SYMBOL, 'a'), Verbatim(SYMBOL, 'b')))", repr(Verbatim('a not in b'))
    assert repr(Verbatim('a is b'))=="Verbatim(IS, (Verbatim(SYMBOL, 'a'), Verbatim(SYMBOL, 'b')))", repr(Verbatim('a is b'))
    assert repr(Verbatim('a is not b'))=="Verbatim(ISNOT, (Verbatim(SYMBOL, 'a'), Verbatim(SYMBOL, 'b')))", repr(Verbatim('a is not b'))
    assert repr(Verbatim('a and b and c'))=="Verbatim(AND, (Verbatim(SYMBOL, 'a'), Verbatim(SYMBOL, 'b'), Verbatim(SYMBOL, 'c')))", repr(Verbatim('a and b and c'))
    assert repr(Verbatim('a or b or c'))=="Verbatim(OR, (Verbatim(SYMBOL, 'a'), Verbatim(SYMBOL, 'b'), Verbatim(SYMBOL, 'c')))", repr(Verbatim('a or b or c'))
    assert repr(Verbatim('(a)'))=="Verbatim(SYMBOL, 'a')", repr(Verbatim('(a)'))
    assert repr(Verbatim('()'))=="Verbatim(TUPLE, ())", repr(Verbatim('()'))
    assert repr(Verbatim('(a,)'))=="Verbatim(TUPLE, (Verbatim(SYMBOL, 'a'),))", repr(Verbatim('(a,)'))
    assert repr(Verbatim('(a,b)'))=="Verbatim(TUPLE, (Verbatim(SYMBOL, 'a'), Verbatim(SYMBOL, 'b')))", repr(Verbatim('(a,b)'))
    assert repr(Verbatim('[]'))=="Verbatim(LIST, ())", repr(Verbatim('[]'))
    assert repr(Verbatim('[a]'))=="Verbatim(LIST, (Verbatim(SYMBOL, 'a'),))", repr(Verbatim('[a]'))
    assert repr(Verbatim('[a,b]'))=="Verbatim(LIST, (Verbatim(SYMBOL, 'a'), Verbatim(SYMBOL, 'b')))", repr(Verbatim('[a,b]'))
    assert repr(Verbatim('lambda : a'))=="Verbatim(LAMBDA, (Verbatim(TUPLE, ()), Verbatim(SYMBOL, 'a')))", repr(Verbatim('lambda : a'))
    assert repr(Verbatim('lambda x: a'))=="Verbatim(LAMBDA, (Verbatim(TUPLE, (Verbatim(SYMBOL, 'x'),)), Verbatim(SYMBOL, 'a')))", repr(Verbatim('lambda x: a'))
    
    assert str(+a) == "+a",str(+a)
    assert str(-a) == "-a",str(-a)
    assert str(~a) == "~a",str(~a)
    assert str(a+b)== "a + b", str(a+b)
    assert str(a-b)== "a - b", str(a-b)
    assert str(a*b)== "a*b", str(a*b)
    assert str(a/b)== "a/b", str(a/b)
    assert str(a//b)== "a//b", str(a//b)
    assert str(a**b)== "a**b", str(a**b)
    assert str(a%b)== "a%b", str(a%b)
    assert str(a|b)== "a|b", str(a|b)
    assert str(a&b)== "a&b", str(a&b)
    assert str(a^b)== "a^b", str(a^b)
    assert str(a<<b)== "a<<b", str(a<<b)
    assert str(a>>b)== "a>>b", str(a>>b)
    assert str(divmod(a,b))== "divmod(a, b)", str(divmod(a,b))
    assert str(a(b))== "a(b)", str(a(b))
    assert str(a())== "a()", str(a())
    assert str(Verbatim('a and b'))=="a and b", str(Verbatim('a and b'))
    assert str(Verbatim('a or b'))=="a or b", str(Verbatim('a or b'))
    assert str(Verbatim('a in b'))=="a in b", str(Verbatim('a in b'))
    assert str(Verbatim('a not in b'))=="a not in b", str(Verbatim('a not in b'))
    assert str(Verbatim('a is b'))=="a is b", str(Verbatim('a is b'))
    assert str(Verbatim('a is not b'))=="a is not b", str(Verbatim('a is not b'))
    assert str(Verbatim('a and b and c'))=="a and b and c", str(Verbatim('a and b and c'))
    assert str(Verbatim('()'))=="()", str(Verbatim('()'))
    assert str(Verbatim('(a,)'))=="(a,)", str(Verbatim('(a,)'))
    assert str(Verbatim('(a,b)'))=="(a, b)", str(Verbatim('(a,b)'))
    assert str(Verbatim('[]'))=="[]", str(Verbatim('[]'))
    assert str(Verbatim('[a]'))=="[a]", str(Verbatim('[a]'))
    assert str(Verbatim('[a,b]'))=="[a, b]", str(Verbatim('[a, b]'))
    assert str(Verbatim('lambda :a'))=="lambda : a", str(Verbatim('lambda : a'))
    assert str(Verbatim('lambda x:a'))=="lambda x: a", str(Verbatim('lambda x: a'))
    assert str(Verbatim('lambda x,y:a'))=="lambda x, y: a", str(Verbatim('lambda x,y: a'))
    
    assert Verbatim('+a') == +a
    assert Verbatim('-a') == -a
    assert Verbatim('~a') == ~a, `Verbatim('~a')`
    assert Verbatim('a+b') == a+b
    assert Verbatim('a-b') == a-b
    assert Verbatim('a*b') == a*b
    assert Verbatim('a/b') == a/b
    assert Verbatim('a//b') == a//b
    assert Verbatim('a**b') == a**b
    assert Verbatim('a % b') == a%b
    assert Verbatim('a | b') == a|b
    assert Verbatim('a & b') == a&b
    assert Verbatim('a << b') == a<<b
    assert Verbatim('a >> b') == a>>b
    assert Verbatim('a (b)') == a(b)
    assert Verbatim('a (b, a)') == a(b,a)
    assert Verbatim('a ()') == a()

    assert Verbatim('a and b') == Verbatim(utils.AND, (a, b))
    assert Verbatim('a or b') == Verbatim(utils.OR, (a, b))
    assert Verbatim('not a') == Verbatim(utils.NOT, a)
    assert Verbatim('a in b') == Verbatim(utils.IN, (a, b))
    assert Verbatim('a not in b') == Verbatim(utils.NOTIN, (a, b))
    assert Verbatim('a is b') == Verbatim(utils.IS, (a, b))
    assert Verbatim('a is not b') == Verbatim(utils.ISNOT, (a, b))
    assert Verbatim('a and b and c') == Verbatim(utils.AND, (a, b, c))
    assert Verbatim('()') == Verbatim(utils.TUPLE, ())
    assert Verbatim('(a,)') == Verbatim(utils.TUPLE, (a, ))
    assert Verbatim('(a,b)') == Verbatim(utils.TUPLE, (a, b))
    assert Verbatim('[]') == Verbatim(utils.LIST, ())
    assert Verbatim('[a]') == Verbatim(utils.LIST, (a,))
    assert Verbatim('[a,b]') == Verbatim(utils.LIST, (a,b))
    assert Verbatim('lambda :a') == Verbatim(utils.LAMBDA, (Verbatim(utils.TUPLE, ()), a))
    assert Verbatim('lambda b:a') == Verbatim(utils.LAMBDA, (Verbatim(utils.TUPLE, (b,)), a))
