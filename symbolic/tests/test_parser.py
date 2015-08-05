"""
Author: Pearu Peterson <pearu.peterson@gmail.com>
Created: January 2007
"""

from numpy.testing import *

set_package_path()
from symbolic.api import Symbolic
from symbolic.parser import Base
from symbolic.parser import *
restore_path()

class test_Lambda(NumpyTestCase):

    def check_simple(self):
        f = Lambda_Test('lambda x:x')
        assert isinstance(f, Lambda_Test),`f`
        assert_equal(repr(f),"Lambda_Test('lambda x : x')")
        assert_equal(str(f), 'lambda x : x')

        f = Lambda_Test('lambda x,y:x + 1/2')
        assert isinstance(f, Lambda_Test),`f`
        assert_equal(str(f), 'lambda x, y : x + 1 / 2')

    def check_tosymbolic(self):
        f = Lambda_Test('lambda x:x').tosymbolic()
        assert isinstance(f, Symbolic.Lambda),`f`
        assert_equal(f.tostr(),'lambda x_: x_')

        f = Lambda_Test('lambda x,y:x*y').tosymbolic()
        assert isinstance(f, Symbolic.Lambda),`f`
        assert_equal(f.tostr(),'lambda x_, y_: x_ * y_')

        f = Lambda_Test('lambda x_:x_').tosymbolic()
        assert_equal(f.tostr(),'lambda x_: x_')
        
class test_Identifier(NumpyTestCase):

    def check_simple(self):
        a = Identifier('a')
        assert isinstance(a,Identifier),`a`
        assert_equal(repr(a),"Identifier('a')")
        a = Identifier('a2')
        assert isinstance(a,Identifier),`a`
        a = Expr('a')
        assert isinstance(a,Identifier),`a`

    def check_tosymbolic(self):
        a = Identifier('a').tosymbolic()
        assert isinstance(a, Symbolic.Symbol),`a`

        
class test_Parenth(NumpyTestCase):

    def check_simple(self):
        a = Parenth('(a  )')
        assert isinstance(a,Parenth),`a`
        assert_equal(repr(a),"Parenth('(a)')")
        a = Expr('(a)')
        assert isinstance(a,Parenth),`a`

    def check_tosymbolic(self):
        a = Parenth('(a  )').tosymbolic()
        assert isinstance(a,Symbolic.Symbol),`a`


class test_Slicing(NumpyTestCase):

    def check_simple(self):
        a = Slicing('a [b ]')
        assert isinstance(a,Slicing),`a`
        assert_equal(repr(a),"Slicing('a[b]')")
        a = Expr('a[b,c]')
        assert isinstance(a,Slicing),`a`


class test_Attr_Ref(NumpyTestCase):

    def check_simple(self):
        a = Attr_Ref('a .b')
        assert isinstance(a,Attr_Ref),`a`
        assert_equal(repr(a),"Attr_Ref('a.b')")
        a = Expr('a.b')
        assert isinstance(a,Attr_Ref),`a`

    def check_tosymbolic(self):
        a = Attr_Ref('a .label').tosymbolic()
        assert_equal(a,'a')

        
class test_Call(NumpyTestCase):

    def check_simple(self):
        a = Call('a ( b )')
        assert isinstance(a,Call),`a`
        assert_equal(repr(a),"Call('a(b)')")
        a = Call('a()')
        assert isinstance(a,Call),`a`
        a = Expr('a(b)')
        assert isinstance(a,Call),`a`
        a = Call('(a)()')
        assert isinstance(a,Call),`a`

    def check_tosymbolic(self):
        a = Call('a ( b )').tosymbolic()
        assert isinstance(a,Symbolic.Apply),`a`


class test_Argument(NumpyTestCase):

    def check_simple(self):
        a = Argument('a= b')
        assert isinstance(a,Argument),`a`
        assert_equal(repr(a),"Argument('a = b')")
        a = Argument('a')
        assert isinstance(a,Identifier),`a`

    def check_tosymbolic(self):
        a = Argument('a= b').tosymbolic()
        assert isinstance(a, Symbolic.Keyword)


class test_Argument_List(NumpyTestCase):

    def check_simple(self):
        a = Argument_List('a=b,c')
        assert isinstance(a,Argument_List),`a`
        assert_equal(repr(a),"Argument_List('a = b, c')")
        a = Argument_List('a,b')
        assert isinstance(a,Argument_List),`a`
        a = Argument_List('a')
        assert isinstance(a,Identifier),`a`

    def check_tosymbolic(self):
        a = Argument_List('a=b,c').tosymbolic()
        assert isinstance(a,list),`a`
        assert len(a)==2,`a`
        assert isinstance(a[0],Symbolic.Keyword),`a`


class test_Int_Literal(NumpyTestCase):

    def check_simple(self):
        a = Int_Literal('1')
        assert isinstance(a,Int_Literal),`a`
        assert_equal(repr(a),"Int_Literal('1')")
        a = Int_Literal('123')
        assert isinstance(a,Int_Literal),`a`
        a = Int_Literal('-123')
        assert isinstance(a,Int_Literal),`a`
        a = Expr('1')
        assert isinstance(a,Int_Literal),`a`

    def check_tosymbolic(self):
        a = Int_Literal('123').tosymbolic()
        assert isinstance(a, Symbolic.Integer),`a`


class test_Float_Literal(NumpyTestCase):

    def check_simple(self):
        a = Float_Literal('1.')
        assert isinstance(a,Float_Literal),`a`
        assert_equal(repr(a),"Float_Literal('1.')")
        a = Float_Literal('12.3')
        assert isinstance(a,Float_Literal),`a`
        a = Float_Literal('.123')
        assert isinstance(a,Float_Literal),`a`
        a = Float_Literal('12e1')
        assert isinstance(a,Float_Literal),`a`
        a = Float_Literal('12.0e-1')
        assert isinstance(a,Float_Literal),`a`
        a = Float_Literal('0.12e+34311')
        assert isinstance(a,Float_Literal),`a`
        a = Expr('1.0')
        assert isinstance(a,Float_Literal),`a`
        a = Expr('0.12e+34311')
        assert isinstance(a,Float_Literal),`a`


class test_Logical_Literal(NumpyTestCase):

    def check_simple(self):
        a = Logical_Literal('True')
        assert isinstance(a,Logical_Literal),`a`
        assert_equal(repr(a),"Logical_Literal('True')")
        a = Logical_Literal('False')
        assert isinstance(a,Logical_Literal),`a`
        a = Expr('True')
        assert isinstance(a,Logical_Literal),`a`

    def check_symbolic(self):
        a = Logical_Literal('True').tosymbolic()
        assert_equal(a, True)


class test_Slice(NumpyTestCase):

    def check_simple(self):
        a = Slice(':')
        assert isinstance(a,Slice),`a`
        a = Slice('a:')
        assert isinstance(a,Slice),`a`
        a = Slice(':b')
        assert isinstance(a,Slice),`a`
        a = Slice('a:b')
        assert isinstance(a,Slice),`a`
        assert_equal(repr(a),"Slice('a : b')")
        a = Slice('a : b: c')
        assert isinstance(a,Slice),`a`
        assert_equal(repr(a),"Slice('a : b : c')")
        a = Slice('a::c')
        assert isinstance(a,Slice),`a`
        a = Slice('::c')
        assert isinstance(a,Slice),`a`

    def check_tosymbolic(self):
        a = Slice('a:b').tosymbolic()
        assert isinstance(a, slice)


class test_Subscript_List(NumpyTestCase):

    def check_simple(self):
        a = Subscript_List('a:b, c:d')
        assert isinstance(a,Subscript_List),`a`
        assert_equal(repr(a),"Subscript_List('a : b, c : d')")
        a = Subscript_List('a, c')
        assert isinstance(a,Subscript_List),`a`
        a = Subscript_List('a')
        assert isinstance(a,Identifier),`a`
        a = Subscript_List('a:b')
        assert isinstance(a,Slice),`a`

    def check_tosymbolic(self):
        a = Subscript_List('a:b, c').tosymbolic()
        assert isinstance(a,list),`a`

        
class test_Power(NumpyTestCase):

    def check_simple(self):
        a = Power('a** b')
        assert isinstance(a,Power),`a`
        assert_equal(repr(a),"Power('a ** b')")
        a = Expr('a**b')
        assert isinstance(a,Power),`a`
        a = Expr('a**2')
        assert isinstance(a,Power),`a`

        a = Power('2')
        assert isinstance(a,Int_Literal),`a`
        a = Power('-2')
        assert isinstance(a,Int_Literal),`a`

    def check_tosymbolic(self):
        a = Power('a **b').tosymbolic()
        assert isinstance(a, Symbolic.Power)


class test_Term(NumpyTestCase):

    def check_simple(self):
        a = Term('a*   b')
        assert isinstance(a,Term),`a`
        assert_equal(repr(a),"Term('a * b')")
        a = Term('a/b')
        assert isinstance(a,Term),`a`
        assert_equal(repr(a),"Term('a / b')")
        a = Expr('a*b')
        assert isinstance(a,Term),`a`
        
    def check_tosymbolic(self):
        a = Term('a  *b').tosymbolic()
        assert isinstance(a, Symbolic.Mul)

    def check_power(self):
        a = Term('a*b**c')
        assert isinstance(a,Term),`a`

class test_Arith(NumpyTestCase):

    def check_simple(self):
        a = Arith('a  +b')
        assert isinstance(a,Arith),`a`
        assert_equal(repr(a),"Arith('a + b')")
        a = Arith('a-b')
        assert isinstance(a,Arith),`a`
        a = Expr('a+b')
        assert isinstance(a,Arith),`a`

    def check_tosymbolic(self):
        a = Arith('a  +b').tosymbolic()
        assert isinstance(a, Symbolic.Add)
        a = Arith('a  -b').tosymbolic()
        assert isinstance(a, Symbolic.Add)


class test_Factor(NumpyTestCase):

    def check_simple(self):
        a = Factor('+a')
        assert isinstance(a,Factor),`a`
        assert_equal(repr(a),"Factor('+ a')")
        a = Factor('-  a')
        assert isinstance(a,Factor),`a`
        a = Expr('+a')
        assert isinstance(a,Factor),`a`

    def check_tosymbolic(self):
        a = Factor('+a').tosymbolic()
        assert isinstance(a, Symbolic.Symbol),`a`
        a = Factor('-a').tosymbolic()
        assert isinstance(a, Symbolic.Mul),`a`


class test_Relational(NumpyTestCase):

    def check_simple(self):
        a = Relational('a>b')
        assert isinstance(a,Relational),`a`
        assert_equal(repr(a),"Relational('a > b')")
        a = Relational('a in b')
        assert isinstance(a,Relational),`a`
        a = Relational('a not in b')
        assert isinstance(a,Relational),`a`
        a = Expr('a>b')
        assert isinstance(a,Relational),`a`

        a = Relational('a==b')
        assert isinstance(a,Relational),`a`
        a = Relational('a>=b')
        assert isinstance(a,Relational),`a`
        a = Relational('a<=b')
        assert isinstance(a,Relational),`a`
        a = Relational('a<>b')
        assert isinstance(a,Relational),`a`
        a = Relational('a!=b')
        assert isinstance(a,Relational),`a`
        a = Relational('a<b')
        assert isinstance(a,Relational),`a`

    def check_tosymbolic(self):
        a = Relational('a  >b').tosymbolic()
        assert isinstance(a, (Symbolic.Greater,Symbolic.Less)),`a`
        a = Relational('a  <b').tosymbolic()
        assert isinstance(a, (Symbolic.Greater,Symbolic.Less)),`a`
        a = Relational('a <=b').tosymbolic()
        assert isinstance(a, (Symbolic.GreaterEqual,Symbolic.LessEqual)),`a`
        a = Relational('a >=b').tosymbolic()
        assert isinstance(a, (Symbolic.GreaterEqual,Symbolic.LessEqual)),`a`
        a = Relational('a ==b').tosymbolic()
        assert isinstance(a, Symbolic.Equal),`a`
        a = Relational('a !=b').tosymbolic()
        assert isinstance(a, Symbolic.NotEqual),`a`
        a = Relational('a <>b').tosymbolic()
        assert isinstance(a, Symbolic.NotEqual),`a`

        
class test_Not_Test(NumpyTestCase):

    def check_simple(self):
        a = Not_Test('not   a')
        assert isinstance(a,Not_Test),`a`
        assert_equal(repr(a),"Not_Test('not a')")
        a = Expr('not a')
        assert isinstance(a,Not_Test),`a`


class test_And_Test(NumpyTestCase):

    def check_simple(self):
        a = And_Test('a and   b')
        assert isinstance(a,And_Test),`a`
        assert_equal(repr(a),"And_Test('a and b')")
        a = Expr('a and b')
        assert isinstance(a,And_Test),`a`


class test_Or_Test(NumpyTestCase):

    def check_simple(self):
        a = Or_Test('a   or b')
        assert isinstance(a,Or_Test),`a`
        assert_equal(repr(a),"Or_Test('a or b')")
        a = Expr('a or b')
        assert isinstance(a,Or_Test),`a`


class test_Expr_List(NumpyTestCase):

    def check_simple(self):
        a = Expr_List('a   or b, c+  2')
        assert isinstance(a,Expr_List),`a`
        assert_equal(repr(a),"Expr_List('a or b, c + 2')")
        a = Expr_List('a')
        assert isinstance(a,Identifier),`a`

    def check_tosymbolic(self):
        a = Expr_List('a , c+  2').tosymbolic()
        assert isinstance(a,list),`a`


class test_Pattern(NumpyTestCase):

    def check_mult_op(self):
        from symbolic.parser import mult_op
        assert_equal(mult_op.named().rsplit('a*b*c'),('a*b','*','c'))
        assert_equal(mult_op.named().rsplit('a*b**c'),('a','*','b**c'))

if __name__=='__main__':
    NumpyTest().run()
