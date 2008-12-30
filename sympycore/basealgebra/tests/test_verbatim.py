from __future__ import with_statement

from sympycore import Verbatim, utils, SymbolicEquality

def test_basic():
    a = Verbatim('a')
    assert Verbatim.convert('a')==a
    assert Verbatim.convert(a) == a

    assert repr(a) == "Verbatim(SYMBOL, 'a')"
    
    assert Verbatim.convert('1') == Verbatim(utils.NUMBER, 1)
    assert Verbatim.convert(1) == Verbatim(utils.SYMBOL, 1)
    assert Verbatim.convert(None) == Verbatim(utils.SPECIAL, None)
    assert Verbatim.convert(Ellipsis) == Verbatim(utils.SPECIAL, Ellipsis)
    assert Verbatim.convert(['a']) == Verbatim(utils.LIST, (Verbatim(utils.SYMBOL, 'a'), )),`Verbatim.convert(['a'])`
    assert Verbatim.convert(('a','1')) == Verbatim(utils.TUPLE, (Verbatim(utils.SYMBOL, 'a'), Verbatim(utils.NUMBER, 1))),`Verbatim.convert(('a',1))`
    assert str(Verbatim(utils.SPECIAL, None))=='None'
    assert str(Verbatim(utils.SPECIAL, Ellipsis))=='...'

def test_operations():
    a = Verbatim('a')
    b = Verbatim('b')
    c = Verbatim('c')
    d = Verbatim('d')
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
    assert repr(divmod(a,b))== "Verbatim(APPLY, (Verbatim(CALLABLE, <built-in function divmod>), Verbatim(SYMBOL, 'a'), Verbatim(SYMBOL, 'b')))", repr(divmod(a,b))
    assert repr(a(b))== "Verbatim(APPLY, (Verbatim(SYMBOL, 'a'), Verbatim(SYMBOL, 'b')))", repr(a(b))
    assert repr(a())== "Verbatim(APPLY, (Verbatim(SYMBOL, 'a'),))", repr(a())
    assert repr(a[b])== "Verbatim(SUBSCRIPT, (Verbatim(SYMBOL, 'a'), Verbatim(SYMBOL, 'b')))", repr(a[b])
    assert repr(a[b,c])== "Verbatim(SUBSCRIPT, (Verbatim(SYMBOL, 'a'), Verbatim(SYMBOL, 'b'), Verbatim(SYMBOL, 'c')))", repr(a[b,c])
    assert repr(a[b:c])== "Verbatim(SUBSCRIPT, (Verbatim(SYMBOL, 'a'), Verbatim(SLICE, (Verbatim(SYMBOL, 'b'), Verbatim(SYMBOL, 'c'), Verbatim(SPECIAL, None)))))", repr(a[b:c])
    assert repr(a[:])== "Verbatim(SUBSCRIPT, (Verbatim(SYMBOL, 'a'), Verbatim(SLICE, (Verbatim(SPECIAL, None), Verbatim(SPECIAL, None), Verbatim(SPECIAL, None)))))", repr(a[:])
    assert repr(a[b:])== "Verbatim(SUBSCRIPT, (Verbatim(SYMBOL, 'a'), Verbatim(SLICE, (Verbatim(SYMBOL, 'b'), Verbatim(SPECIAL, None), Verbatim(SPECIAL, None)))))", repr(a[b:])
    assert repr(a[:b])== "Verbatim(SUBSCRIPT, (Verbatim(SYMBOL, 'a'), Verbatim(SLICE, (Verbatim(SPECIAL, None), Verbatim(SYMBOL, 'b'), Verbatim(SPECIAL, None)))))", repr(a[:b])
    assert repr(a[::b])== "Verbatim(SUBSCRIPT, (Verbatim(SYMBOL, 'a'), Verbatim(SLICE, (Verbatim(SPECIAL, None), Verbatim(SPECIAL, None), Verbatim(SYMBOL, 'b')))))", repr(a[::b])

    with SymbolicEquality(Verbatim):
        assert repr(a==a)=="Logic('a==a')",repr(a==a)
    
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
    assert repr(Verbatim('a==b'))=="Verbatim(EQ, (Verbatim(SYMBOL, 'a'), Verbatim(SYMBOL, 'b')))", repr(Verbatim('a==b'))
    assert repr(Verbatim('a!=b'))=="Verbatim(NE, (Verbatim(SYMBOL, 'a'), Verbatim(SYMBOL, 'b')))", repr(Verbatim('a!=b'))
    assert repr(Verbatim('a<b'))=="Verbatim(LT, (Verbatim(SYMBOL, 'a'), Verbatim(SYMBOL, 'b')))", repr(Verbatim('a<b'))
    assert repr(Verbatim('a>b'))=="Verbatim(GT, (Verbatim(SYMBOL, 'a'), Verbatim(SYMBOL, 'b')))", repr(Verbatim('a>b'))
    assert repr(Verbatim('a<=b'))=="Verbatim(LE, (Verbatim(SYMBOL, 'a'), Verbatim(SYMBOL, 'b')))", repr(Verbatim('a<=b'))
    assert repr(Verbatim('a>=b'))=="Verbatim(GE, (Verbatim(SYMBOL, 'a'), Verbatim(SYMBOL, 'b')))", repr(Verbatim('a>=b'))
    assert repr(Verbatim('a<b<c'))=="Verbatim(AND, (Verbatim(LT, (Verbatim(SYMBOL, 'a'), Verbatim(SYMBOL, 'b'))), Verbatim(LT, (Verbatim(SYMBOL, 'b'), Verbatim(SYMBOL, 'c')))))", repr(Verbatim('a<b<c'))
    assert repr(Verbatim('a[b]'))=="Verbatim(SUBSCRIPT, (Verbatim(SYMBOL, 'a'), Verbatim(SYMBOL, 'b')))", repr(Verbatim('a[b]'))
    assert repr(Verbatim('a[b,c]'))=="Verbatim(SUBSCRIPT, (Verbatim(SYMBOL, 'a'), Verbatim(SYMBOL, 'b'), Verbatim(SYMBOL, 'c')))", repr(Verbatim('a[b,c]'))

    assert repr(Verbatim('divmod(a,b)'))=="Verbatim(APPLY, (Verbatim(SYMBOL, 'divmod'), Verbatim(SYMBOL, 'a'), Verbatim(SYMBOL, 'b')))",repr(Verbatim('divmod(a,b)'))
    assert repr(Verbatim('slice(a)'))=="Verbatim(SLICE, (Verbatim(SYMBOL, 'a'),))",repr(Verbatim('slice(a)'))
    assert repr(Verbatim('slice(a,b)'))=="Verbatim(SLICE, (Verbatim(SYMBOL, 'a'), Verbatim(SYMBOL, 'b')))",repr(Verbatim('slice(a,b)'))
    assert repr(Verbatim('slice(a,b,c)'))=="Verbatim(SLICE, (Verbatim(SYMBOL, 'a'), Verbatim(SYMBOL, 'b'), Verbatim(SYMBOL, 'c')))",repr(Verbatim('slice(a,b,c)'))
    assert repr(Verbatim('a[b:c,d]'))=="Verbatim(SUBSCRIPT, (Verbatim(SYMBOL, 'a'), Verbatim(SLICE, (Verbatim(SYMBOL, 'b'), Verbatim(SYMBOL, 'c'), Verbatim(SPECIAL, None))), Verbatim(SYMBOL, 'd')))", repr(Verbatim('a[b:c,d]'))
    assert repr(Verbatim('a[b:c]'))=="Verbatim(SUBSCRIPT, (Verbatim(SYMBOL, 'a'), Verbatim(SLICE, (Verbatim(SYMBOL, 'b'), Verbatim(SYMBOL, 'c'), Verbatim(SPECIAL, None)))))", repr(Verbatim('a[b:c]'))

    assert repr(Verbatim('{a:b, c:d}'))=="Verbatim(DICT, ((Verbatim(SYMBOL, 'a'), Verbatim(SYMBOL, 'b')), (Verbatim(SYMBOL, 'c'), Verbatim(SYMBOL, 'd'))))", repr(Verbatim('{a:b, c:d}'))
    assert repr(Verbatim('{a:b}'))=="Verbatim(DICT, ((Verbatim(SYMBOL, 'a'), Verbatim(SYMBOL, 'b')),))", repr(Verbatim('{a:b}'))
    assert repr(Verbatim('a.b'))=="Verbatim(ATTR, (Verbatim(SYMBOL, 'a'), Verbatim(SYMBOL, 'b')))", repr(Verbatim('a.b'))
    assert repr(Verbatim('a(b=c)'))=="Verbatim(APPLY, (Verbatim(SYMBOL, 'a'), Verbatim(KWARG, (Verbatim(SYMBOL, 'b'), Verbatim(SYMBOL, 'c')))))", repr(Verbatim('a(b=c)'))

    #assert repr(Verbatim('a if b else c'))=='',repr(Verbatim('a if b else c'))
    
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
    assert str(a[b])== "a[b]", str(a[b])
    assert str(a[b:])== "a[b:]", str(a[b:])
    assert str(a[b:c])== "a[b:c]", str(a[b:c])
    assert str(a[b:c:d])== "a[b:c:d]", str(a[b:c:d])
    assert str(a[:c:d])== "a[:c:d]", str(a[:c:d])
    assert str(a[::d])== "a[::d]", str(a[::d])
    assert str(a[b::d])== "a[b::d]", str(a[b::d])
    assert str((a+b)[c])== "(a + b)[c]", str((a+c)[c])
    assert str((a+b)(c))== "(a + b)(c)", str((a+c)(c))
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
    assert str(Verbatim('a< b'))=="a<b", str(Verbatim('a < b'))
    assert str(Verbatim('a==b'))=="a==b", str(Verbatim('a ==b'))
    assert str(Verbatim('a!= b'))=="a!=b", str(Verbatim('a!=b'))
    assert str(Verbatim('a<= b'))=="a<=b", str(Verbatim('a <= b'))
    assert str(Verbatim('a> b'))=="a>b", str(Verbatim('a > b'))
    assert str(Verbatim('a>= b'))=="a>=b", str(Verbatim('a >= b'))
    assert str(Verbatim('a<b<c'))=="a<b and b<c", str(Verbatim('a<b<c'))
    assert str(Verbatim('a<b==c'))=="a<b and b==c", str(Verbatim('a<b==c'))
    assert str(Verbatim('a[b:c]'))=="a[b:c]", str(Verbatim('a[b:c]'))
    assert str(Verbatim('a[b:c,d]'))=="a[b:c, d]", str(Verbatim('a[b:c, d]'))
    assert str(Verbatim('a[b:]'))=="a[b:]", str(Verbatim('a[b:]'))
    assert str(Verbatim('a[:b]'))=="a[:b]", str(Verbatim('a[:b]'))
    assert str(Verbatim('a[::b]'))=="a[::b]", str(Verbatim('a[::b]'))
    assert str(Verbatim('a[b::c]'))=="a[b::c]", str(Verbatim('a[b::c]'))
    assert str(Verbatim('a[b:c:d]'))=="a[b:c:d]", str(Verbatim('a[b:c:d]'))
    assert str(Verbatim('a[b::]'))=="a[b:]", str(Verbatim('a[b::]'))
    assert str(Verbatim('a[b::]'))=="a[b:]", str(Verbatim('a[b::]'))
    assert str(Verbatim('a[b,...,c]'))=="a[b, ..., c]", str(Verbatim('a[b,...,c]'))
    assert str(Verbatim('a[...]'))=="a[...]", str(Verbatim('a[...]'))
    assert str(Verbatim('{a:b}'))=="{a:b}", str(Verbatim('{a:b}'))
    assert str(Verbatim('{a:b, c:1}'))=="{a:b, c:1}", str(Verbatim('{a:b, c:1}'))
    assert str(Verbatim('a.b'))=="a.b", str(Verbatim('a.b'))
    assert str(Verbatim('(a+1).b'))=="(a + 1).b", str(Verbatim('(a+1).b'))
    assert str(a.b)=="a.b", str(a.b)
    assert str((a+1).b)=="(a + 1).b", str((a+1).b)
    assert str(a(b=c))=="a(b=c)", str(a(b=c))
    
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
    assert Verbatim('a[b]') == a[b]
    assert Verbatim('a[b,c]') == a[b,c], `Verbatim('a[b,c]'),a[b,c]`
    assert Verbatim('a[b:c,d]') == a[b:c,d], `Verbatim('a[b:c,d]'),a[b:c,d]`

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
    assert Verbatim('a==b')==Verbatim(utils.EQ, (a, b)), Verbatim('a == b')
    assert Verbatim('a!=b')==Verbatim(utils.NE, (a, b)), Verbatim('a != b')
    assert Verbatim('a<b')==Verbatim(utils.LT, (a, b)), Verbatim('a < b')
    assert Verbatim('a<=b')==Verbatim(utils.LE, (a, b)), Verbatim('a <= b')
    assert Verbatim('a>b')==Verbatim(utils.GT, (a, b)), Verbatim('a > b')
    assert Verbatim('a>=b')==Verbatim(utils.GE, (a, b)), Verbatim('a >= b')
    assert Verbatim('a[b]')==Verbatim(utils.SUBSCRIPT, (a, b)), Verbatim('a[b]')
    assert Verbatim('a[b,c]')==Verbatim(utils.SUBSCRIPT, (a, b, c)), Verbatim('a[b,c]')
    assert Verbatim('a[b:c]')==Verbatim(utils.SUBSCRIPT, (a, Verbatim(utils.SLICE, (b,c,Verbatim(utils.SPECIAL, None))))), `Verbatim('a[b:c]')`
    assert Verbatim('a[b:c,d]')==Verbatim(utils.SUBSCRIPT, (a, Verbatim(utils.SLICE, (b,c,Verbatim(utils.SPECIAL, None))), d)), `Verbatim('a[b:c,d]')`
    assert Verbatim('a[...]')==Verbatim(utils.SUBSCRIPT, (Verbatim(utils.SYMBOL, 'a'), Verbatim(utils.SPECIAL, Ellipsis))), `Verbatim('a[...]')`
    assert Verbatim('{a:b}')==Verbatim(utils.DICT, ((a, b),))
    assert Verbatim('a.b')==a.b
    assert Verbatim('a(b=c)')==a(b=c)
    assert Verbatim('a(b,c=d)')==a(b,c=d)

    
