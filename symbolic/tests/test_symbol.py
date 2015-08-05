from numpy.testing import *

set_package_path()
from symbolic.api import Symbolic, Symbol
restore_path()
Symbolic.interactive = False

Int = Symbolic.Integral

class test_Symbol(NumpyTestCase):

    def check_init(self):
        s = Symbol('s')
        assert_equal(`s`,"Symbol('s')")
        assert s is Symbol('s')

    def check_hash(self):
        a = Symbol('a')
        b = Symbol('b')
        assert hash(a)!=hash(b)
        assert_equal(a.flags.hash,hash(a))
        assert_equal(b.flags.hash,hash(b))

    def check_dict(self):
        a = Symbol('a')
        b = Symbol('b')
        d = {}
        d[a] = 1
        assert d.has_key(a)
        assert not d.has_key(b)
        assert len(d)==1
        d[a] = 2
        assert len(d)==1

    def check_equal(self):
        a = Symbol('a')
        assert bool(a==a)

    def check_tostr(self):
        a = Symbol('a')
        assert_equal(a.tostr(),'a')

    def check_diff(self):
        a = Symbol('a')
        assert_equal(a.diff(a).tostr(),'1')
        assert_equal(a.diff(a,a).tostr(),'0')
        assert_equal(a.diff('a').tostr(),'1')
        assert_equal(a.diff('b').tostr(),'0')

    def check_integrate(self):
        a = Symbol('a')
        b = Symbol('b')
        assert_equal((a.integrate(a)).tostr(),'1/2 * a ** 2')
        assert_equal((b.integrate(a)).tostr(),'a * b')
        assert_equal((b.integrate(Symbolic.Range(a,1,5))).tostr(),'4 * b')
        assert_equal((a.integrate(Symbolic.Range(a,1,5))).tostr(),'12')

    def check_substitute(self):
        a = Symbol('a')
        b = Symbol('b')
        assert_equal(a.substitute(a,b),b)
        assert_equal(a.substitute(a,b).tostr(),'b')
        assert_equal(a.substitute(b,b).tostr(),'a')
        assert_equal(a.substitute(a,34).tostr(),'34')
        assert a.substitute(b, 3) is a
        assert a.substitute(a, b) is b

    def check_symbols(self):
        a = Symbol('a')
        assert_equal(a.symbols(),set([a]))


class test_Symbol_boolean_mths(NumpyTestCase):

    def check_invert(self):
        assert_equal(Symbolic('~ a').tostr(),'~a')
        assert_equal(Symbolic('~(~ a)').tostr(),'a')
        assert_equal((~Symbolic('a')).tostr(),'~a')
        
    def check_and(self):
        assert_equal(Symbolic('a & a').tostr(),'a')
        assert_equal(Symbolic('a and a').tostr(),'a')
        assert_equal(Symbolic('b & a').tostr(),'a & b')
        assert_equal(Symbolic('a and b').tostr(),'a & b')
        assert_equal(Symbolic('a & TRUE').tostr(),'a')
        assert_equal(Symbolic('TRUE & a').tostr(),'a')
        assert_equal(Symbolic('a & False').tostr(),'FALSE')
        assert_equal((Symbolic('a') & Symbolic('b')).tostr(),'a & b')
        assert_equal(Symbolic('a&c&b').tostr(),'a & b & c')


    def check_or(self):
        assert_equal(Symbolic('a | a').tostr(),'a')
        assert_equal(Symbolic('a or a').tostr(),'a')
        assert_equal(Symbolic('a | b').tostr(),'a | b')
        assert_equal(Symbolic('b or a').tostr(),'a | b')
        assert_equal(Symbolic('a | TRUE').tostr(),'TRUE')
        assert_equal(Symbolic('FALSE | a').tostr(),'a')
        assert_equal(Symbolic('a | False').tostr(),'a')
        assert_equal((Symbolic('a') | Symbolic('b')).tostr(),'a | b')
        assert_equal(Symbolic('a|c|b').tostr(),'a | b | c')

    def check_xor(self):
        assert_equal(Symbolic('a ^ a').tostr(),'FALSE')
        assert_equal(Symbolic('a ^ ~a').tostr(),'TRUE')
        assert_equal(Symbolic('a xor b').tostr(),'a ^ b')
        assert_equal(Symbolic('a ^ TRUE').tostr(),'~a')
        assert_equal(Symbolic('TRUE ^ a').tostr(),'~a')
        assert_equal(Symbolic('a ^ FALSE').tostr(),'a')
        assert_equal(Symbolic('a^c^b').tostr(),'a ^ b ^ c')
        assert_equal(Symbolic('a^c^b^a').tostr(),'b ^ c')
        assert_equal(Symbolic('a^c^b^~a').tostr(),'b ^ ~c')

    def check_xor_not(self):
        assert_equal(Symbolic('a ^ ~a').tostr(),'TRUE')
        assert_equal(Symbolic('~ (a ^ b)').tostr(),'~(a ^ b)')
        assert_equal(Symbolic('~ a ^ b').tostr(),'b ^ ~a')

    def check_xor_or(self):
        assert_equal(Symbolic('a ^ (b | c)').tostr(),'a ^ (b | c)')
        assert_equal(Symbolic('(a ^ b) | c').tostr(),'c | a ^ b')
        assert_equal(Symbolic('a ^ b | c').tostr(),'c | a ^ b')

    def check_xor_and(self):
        assert_equal(Symbolic('a ^ b & c').tostr(),'a ^ b & c')
        assert_equal(Symbolic('a ^ (b & c)').tostr(),'a ^ b & c')
        assert_equal(Symbolic('(a ^ b) & c').tostr(),'c & (a ^ b)')
        
    def check_or_not(self):
        assert_equal(Symbolic('a | ~a').tostr(),'TRUE')
        assert_equal(Symbolic('b | a | ~a').tostr(),'TRUE')
        assert_equal(Symbolic('~ (a | b)').tostr(),'~(a | b)')

    def check_and_not(self):
        assert_equal(Symbolic('a & ~a').tostr(),'FALSE')
        assert_equal(Symbolic('b & a & ~a').tostr(),'FALSE')
        assert_equal(Symbolic('~ (b & a)').tostr(),'~(a & b)')
        
    def check_or_and(self):
        assert_equal(Symbolic('a | (b & c)').tostr(),'a | b & c')
        assert_equal(Symbolic('(a | b) & c').tostr(),'c & (a | b)')

    def check_substitute_not(self):
        a,b = map(Symbolic,'ab')
        assert_equal((~a).substitute(a,b).tostr(),'~b')
        assert_equal((~a).substitute(a,'true').tostr(),'FALSE')

    def check_substitute_and(self):
        a,b,c = map(Symbolic,'abc')
        assert_equal((a&b).substitute(a,c).tostr(),'b & c')
        assert_equal((a&b).substitute(a,'true').tostr(),'b')

    def check_substitute_or(self):
        a,b,c = map(Symbolic,'abc')
        assert_equal((a|b).substitute(a,c).tostr(),'b | c')

    def check_expand(self):
        assert_equal(Symbolic('~ (a | b)').expand().tostr(),'~a & ~b')
        assert_equal(Symbolic('~ (a & b)').expand().tostr(),'~a | ~b')

    def check_is_equal(self):
        a,b,c = map(Symbolic,'abc')
        p1 = (a&b).implies(c)
        p2 = a.implies(b.implies(c))
        assert_equal(p1.expand().tostr(),p2.expand().tostr())
        assert_equal(p1,p1)
        assert_equal(p1,p2)
        assert_equal((p1==a).is_true(), None)
        assert_equal((~a==a).is_true(), False)
        
if __name__ == '__main__':
    NumpyTest().run()
