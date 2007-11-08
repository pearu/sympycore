
from sympy import *

def test_basic_symbol():
    a = BasicSymbol('a')
    assert a.name=='a'
    assert a.tostr()=='a'
    assert a.torepr()=="BasicSymbol('a')"

def test_basic_dummy():
    a = BasicDummySymbol('a')
    assert a.name=='a'
    assert a.tostr()=='_a'
    assert a.torepr()=="BasicDummySymbol('a')"
    assert a==a
    assert a!=BasicDummySymbol('a')
    
    a = BasicDummySymbol()
    assert a.name.startswith('BDS')
    assert a.tostr().startswith('_BDS')
    assert a.torepr()=="BasicDummySymbol()"
    assert a==a
    assert a!=BasicDummySymbol()

def test_basic_wild():
    a = BasicWildSymbol('a')
    assert a.name=='a'
    assert a.tostr()=='a_'
    assert a.torepr()=="BasicWildSymbol('a')"
    assert a==a
    assert a!=BasicDummySymbol('a')

    a = BasicWildSymbol()
    assert a.name.startswith('BWS')
    assert a.tostr().startswith('BWS') and a.tostr().endswith('_')
    assert a.torepr()=="BasicWildSymbol()"
    assert a==a
    assert a!=BasicDummySymbol()

def test_basic_symbol_failures():
    a = BasicSymbol('a')
    try:
        a + a
    except TypeError, msg:
        assert str(msg).startswith('unsupported operand type')
    else:
        assert 0,"Expected TypeError in <BasicSymbol instance> + <rhs> operation"

    try:
        1 + a
    except TypeError, msg:
        assert str(msg).startswith('unsupported operand type')
    else:
        assert 0,"Expected TypeError in <lhs> + <BasicSymbol instance> operation"

    try:
        a - a
    except TypeError, msg:
        assert str(msg).startswith('unsupported operand type')
    else:
        assert 0,"Expected TypeError in <BasicSymbol instance> - <rhs> operation"

    try:
        a * a
    except TypeError, msg:
        assert str(msg).startswith('unsupported operand type')
    else:
        assert 0,"Expected TypeError in <BasicSymbol instance> * <rhs> operation"

    try:
        1 * a
    except TypeError, msg:
        assert str(msg).startswith('unsupported operand type')
    else:
        assert 0,"Expected TypeError in <lhs> * <BasicSymbol instance> operation"

    try:
        a / a
    except TypeError, msg:
        assert str(msg).startswith('unsupported operand type')
    else:
        assert 0,"Expected TypeError in <BasicSymbol instance> / <rhs> operation"

    try:
        a % a
    except TypeError, msg:
        assert str(msg).startswith('unsupported operand type')
    else:
        assert 0,"Expected TypeError in <BasicSymbol instance> % <rhs> operation"

    try:
        1 % a
    except TypeError, msg:
        assert str(msg).startswith('unsupported operand type')
    else:
        assert 0,"Expected TypeError in <lhs> % <BasicSymbol instance> operation"

    try:
        +a
    except TypeError, msg:
        assert str(msg).startswith('bad operand type for unary')
    else:
        assert 0,"Expected TypeError in +<BasicSymbol instance>"

    try:
        -a
    except TypeError, msg:
        assert str(msg).startswith('bad operand type for unary')
    else:
        assert 0,"Expected TypeError in -<BasicSymbol instance>"
