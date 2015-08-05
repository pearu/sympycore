
from numpy.testing import *

set_package_path()
from symbolic.api import Symbolic, Symbol, Mul, Power, Add
from symbolic.number import Number, Rational, Integer, Zero, NaN, Infinity, One, Half,\
     ImaginaryUnit, NegativeInfinity
from symbolic.number import factor_trial_division
restore_path()
Symbolic.interactive = False

minf = Number(-1,0)
inf = Number(1,0)
nan = Number(0,0)
zero = Number(0)
one = Number(1)
mone = Number(-1)
half = Number(1,2)
sym = Symbol()
gt1 = Number(3,2)
lt1 = Number(1,4)
I = ImaginaryUnit()

class test_Number(NumpyTestCase):

    def check_init(self):
        assert isinstance(Number(1),Rational)
        assert isinstance(Number(1),Integer)
        assert isinstance(Number(1,2),Rational)
        assert isinstance(Number((1,2)),Rational)
        assert not isinstance(Number(1,2),Integer)
        assert isinstance(Number(Number(1,1)),Number)

    def check_singleton(self):
        assert Zero() is Zero()
        assert Infinity() is Infinity()
        assert Infinity() is 2*Infinity()
        assert -1*Infinity() is -2*Infinity()
        assert Infinity() is not -Infinity()
        assert NaN() is NaN()
        
    def check_zero_init(self):
        assert isinstance(Number(0,2),Rational)
        assert isinstance(Number(0,2),Integer)
        assert isinstance(Number(0,2),Zero)
        assert isinstance(Rational(0,2),Zero)
        assert isinstance(Integer(0),Zero)

    def check_nan_init(self):
        assert isinstance(Number(0,0),Rational)
        assert isinstance(Number(0,0),NaN)
        assert isinstance(Rational(0,0),NaN)
        assert isinstance(0*Infinity(),NaN)

    def check_inf_init(self):
        assert isinstance(Number(1,0),Rational)
        assert isinstance(Number(1,0),Infinity)
        assert isinstance(Number(-1,0),NegativeInfinity)
        assert isinstance(Rational(1,0),Infinity)

    def check_compare(self):
        r = Number(2,3)
        i = Number(1)
        assert_equal(r.compare(r),0)
        assert_equal(r.compare(i),1)

    def check_tostr(self):
        n = Number(2,3)
        assert_equal(n.tostr(),'2/3')
        assert_equal((-n).tostr(),'-2/3')

    def check_diff(self):
        n = Number(2,3)
        assert_equal(n.diff('a').tostr(),'0')
        assert_equal(n.diff().tostr(),'2/3')

    def check_get_primitive(self):
        a = Symbol('a')
        n = Number(2,3)
        assert_equal((Symbolic.Integral(a)(n)).tostr(), '2/3 * a')

    def check_integrate(self):
        a = Symbol('a')
        b = Symbol('b')
        c = Symbol('c')
        n = Number(2,3)
        assert_equal((n.integrate(a)).tostr(),'2/3 * a')
        assert_equal((n.integrate(Symbolic.Range(a,1,5))).tostr(),'8/3')
        assert_equal((n.integrate(Symbolic.Range(a,c,b))).tostr(),'2/3 * b - 2/3 * c')

    def check_symbols(self):
        n = Number(2)/3
        assert_equal(n.symbols(),set([]))

class test_Decimal(NumpyTestCase):

    def check_init(self):
        r = Number('1.2')
        assert_equal(r.tostr(),'1.2')

    def check_add(self):
        r = Number('1.2')
        assert_equal((r+2).tostr(),'3.2')
        assert_equal((r+r).tostr(),'2.4')
        assert_equal((r+'3.4').tostr(),'4.6')
        assert_equal((r+'3').tostr(),'4.2')
        assert_equal((r-1).tostr(),'0.2')
        assert_equal((r-r).tostr(),'0')
        assert_equal((r-'2').tostr(),'-0.8')

    def check_todecimal(self):
        r = Number(4,5)
        assert_equal(r.tostr(),'4/5')
        assert_equal(r.todecimal().tostr(),'0.8')
        
class test_Rational(NumpyTestCase):

    def check_init(self):
        r = Number(2,3)
        assert r.numer==2 and r.denom==3

    def check_init_operations(self):
        assert Rational(2,1)==Integer(2)
        assert Rational(0,0) is NaN()
        assert Rational(2,0) is Infinity()
        assert Rational(0,1) is Zero()

    def check_repr(self):
        assert_equal(`Rational(3,2)`,'Rational(3, 2)')
        assert_equal(`Rational(2,1)`,'Integer(2)')
        assert_equal(`Rational(0,3)`,'Zero()')
        assert_equal(`Rational(1,1)`,'One()')
        assert_equal(`Rational(1,-1)`,'NegativeOne()')
        assert_equal(`Rational(1,2)`,'Half()')
        
    def check_unary(self):
        assert_equal((+Rational(1,2)).tostr(),'1/2')
        assert_equal((-Rational(1,2)).tostr(),'-1/2')

    def check_operations(self):
        assert_equal(Rational(2,3)**-1, Rational(3,2))
        assert_equal(Rational(2,3)**Number(-1), Rational(3,2))

    
class test_Integer(NumpyTestCase):

    def check_init(self):
        r = Number(2,1)
        assert r.numer==2 and r.denom==1
        r = Number(2)
        assert r.numer==2 and r.denom==1

    def check_init_operations(self):
        assert Integer(0) is Zero()
        assert Integer(1) is One()
        assert Integer(-1) is -One()
        assert Integer(Integer(3))==3

    def check_toint(self):
        assert int(Integer(2))==2

    def check_tostr(self):
        n = Integer(2)
        assert_equal(n.tostr(),'2')
        assert_equal((-n).tostr(),'-2')

    def check_cmp(self):
        assert_equal(cmp(Integer(1),Integer(2)),cmp(1,2))
        assert_equal(cmp(Integer(2),Integer(1)),cmp(2,1))

class test_Zero(NumpyTestCase):

    def check_init(self):
        z = Number(0)
        assert z is Zero()
        assert z*2 is z
        assert z/2 is z
        assert z**2 is z
        assert z.numer==0 and z.denom==1

    def check_unary(self):
        assert +Zero() is Zero()
        assert -Zero() is Zero()

    def check_operations(self):
        nan = NaN()
        inf = Infinity()
        n = Number(2,3)
        one = Number(1)
        zero = Number(0)

        assert 1/zero is inf
        assert zero ** -1 is inf
        assert zero ** -one is inf
        for z in [0, zero]:
            assert z + 2 == 2
            assert z - 2 == -2
            assert z * nan is nan
            assert z * inf is nan
            assert z * 2 is z
            assert z * Number(1,2)==0
            assert 2 + z == 2
            assert 2 - z == 2
            assert 2 * z is z
            assert nan * z is nan
            assert inf * z is nan
            assert n / z is inf, `n / z`
            assert z / n is zero, `z / n`
            if z is zero:
                assert 2 / z is inf
                assert z / z is nan
                assert z / 0 is nan
                assert z ** z is one
                assert z ** 0 is one
                assert z ** -2 is inf
            assert z / 2 is z

            assert z ** inf==z,`z,z**inf`
            assert z ** nan==z,`x**nan`
            assert z ** 2 is z
            assert z ** n is zero, `z**n`
            assert inf ** z is one,`inf**z`
            assert nan ** z is one
            assert 2 ** z==one
            assert n ** z is one
            assert z == 0

    def check_tostr(self):
        n = Zero()
        assert_equal(n.tostr(),'0')
        assert_equal((-n).tostr(),'0')

class test_One(NumpyTestCase):

    def check_init_and_unary(self):
        o = Number(1)
        m = Number(-1)
        assert o is One()
        assert o.numer==1 and o.denom==1
        assert m.numer==-1 and o.denom==1
        assert m is -o
        assert -m is o
        assert +o is o
        assert +m is m
        
    def check_operations(self):
        z = Zero()
        nan = NaN()
        inf = Infinity()
        n = Number(2,3)
        one = Number(1)
        mone = -one
        assert one ** inf is one
        assert one ** nan is one
        assert 1 ** inf is one
        assert 1 ** -inf is one
        assert n ** one == n, `n,n**one`
        assert n / one is n
        assert n * mone == -n
        assert n / mone == -n
        assert mone ** inf is nan, `mone **inf`
        assert mone ** 2 is one
        assert mone ** 3 is mone
        assert mone ** -1 is mone
        assert mone ** -4 is one
        assert 0 ** mone is inf
        assert mone * mone is one
        assert -1 * mone==one,`-1 * mone`
        assert mone * (-1)==one

    def check_tostr(self):
        n = One()
        assert_equal(n.tostr(),'1')
        assert_equal((-n).tostr(),'-1')

    def check_integrate(self):
        n = One()
        assert_equal(n.integrate('x').tostr(),'x')

class test_NaN(NumpyTestCase):
    
    def check_init_and_unary(self):
        nan = Number(0,0)
        one = One()
        assert nan is Rational(0,0)
        assert nan.numer==0 and nan.denom==0
        assert -nan is nan and +nan is nan
        assert nan * 2 is nan
        assert 1 ** nan is one
        assert One() ** nan is One()

    def check_tostr(self):
        n = NaN()
        assert_equal(n.tostr(),'NaN')
        assert_equal((-n).tostr(),'NaN')

class test_Infinity(NumpyTestCase):

    def check_init_and_unary(self):
        inf = Number(2,0)
        minf = Number(-3,0)
        assert inf is Infinity()
        assert inf.numer==1 and inf.denom==0
        assert minf.numer==-1 and minf.denom==0
        assert -inf is minf
        assert -minf is inf
        assert +inf is inf
        assert +minf is minf

    def check_operations(self):
        inf = Infinity()
        minf = -inf
        nan = NaN()
        zero = Zero()
        one = Number(1)
        assert inf * 0 is nan
        assert 0 * inf is nan
        assert inf * 3 is inf
        assert 3 * inf is inf
        assert inf * -3 is minf
        assert -3 * inf is minf
        assert minf * -3 is inf
        assert -3 * minf is inf
        assert 0/inf is zero
        assert 3/inf is zero
        assert 3/minf is zero
        assert 1 + inf is inf
        assert 1 + minf is minf
        assert 1 - inf is minf
        assert 1 - minf is inf
        assert inf + 2 is inf
        assert inf -2 is inf
        assert inf / 3 is inf
        assert inf / -4 is minf, `inf/-4`
        assert 1 / inf is zero
        assert -3 / inf is zero
        assert inf/inf is nan
        assert minf/inf is nan
        assert inf/minf is nan
        assert nan/inf is nan
        assert inf/nan is nan
        assert inf/0 is inf
        assert 1 ** inf is one
        assert (-1) ** inf is nan
        assert inf ** -1 is zero
        assert minf ** -1 is zero
        assert 1 ** minf is one
        assert (-1) ** minf is nan, `(-1) ** minf`
        assert 2 ** inf is inf, `2**inf`
        assert_equal(Number(-2) ** inf,inf+inf*I)
        assert_equal((-2) ** inf,inf+inf*I)
        assert 0 ** inf is zero,`0 ** inf`
        assert 2 ** minf is zero
        assert (-2) ** minf is zero,`(-2) ** minf`

    def check_tostr(self):
        n = Infinity()
        assert_equal(n.tostr(),'Inf')
        assert_equal((-n).tostr(),'-Inf')

class test_Half(NumpyTestCase):

    def check_init_and_unary(self):
        half = Half()
        assert half is Rational(1,2)
        assert half.numer==1 and half.denom==2
        assert +half is half
        assert -half == Rational(-1,2)

    def check_operations(self):
        half = Half()
        one = One()
        assert half * 2 is one, `half * 2`
        assert 2 * half is one
        assert_equal((4 ** half).tostr(),'4 ** (1/2)')

    def check_tostr(self):
        n = Half()
        assert_equal(n.tostr(),'1/2')
        assert_equal((-n).tostr(),'-1/2')

class test_ImaginaryUnit(NumpyTestCase):

    def check_init_and_unary(self):
        i = ImaginaryUnit()
        half = Half()
        assert (-1)**half is i

    def check_repr(self):
        assert_equal(`ImaginaryUnit()`,'ImaginaryUnit()')
        assert_equal(`-ImaginaryUnit()`,'NegativeImaginaryUnit()')

    def check_mul(self):
        i = ImaginaryUnit()
        one = Number(1)
        mone = Number(-1)
        assert i*i is mone
        assert i*(-i) is one

    def check_power(self):
        i = ImaginaryUnit()
        one = Number(1)
        mone = Number(-1)
        assert i**1 is i
        assert i**3 is -i
        assert i**5 is i
        assert i**2 is mone
        assert i**0 is one
        assert i**4 is one
        assert i**-2 is mone
        assert i**-4 is one
        assert i**-1 is -i

    def check_tostr(self):
        n = ImaginaryUnit()
        assert_equal(n.tostr(),'I')
        assert_equal((-n).tostr(),'-I')

class test_factor(NumpyTestCase):

    def check_simple(self):
        factor = factor_trial_division
        for n in [4,5,10,-2,-1,0,1,132412,-2324,586390350]:
            n1 = 1
            f = factor(n)
            for prime,e in f.items():
                n1 *= prime ** e
            assert_equal(n,n1)

class test_calcfactor(NumpyTestCase):

    def check_integer(self):
        for n in [4,5,10,-2,-1,0,1,132412,-2324,586390350]:
            i = Integer(n)
            f = i.flags.factors
            n1 = Integer(1)
            for prime,e in f.items():
                n1 *= prime ** e
            assert_equal(n,n1)

    def check_rational(self):
        for r in [Number(83,4729), Number(45,-23570)]:
            f = r.flags.factors
            n1 = Integer(1)
            for prime,e in f.items():
                if e<0:
                    n1 /= prime ** -e
                else:
                    n1 *= prime ** e
            assert_equal(r,n1)
    def check_special(self):
        inf = Number(1,0)
        assert_equal(inf.flags.factors,{0:-1})
        minf = Number(-1,0)
        assert_equal(minf.flags.factors,{0:-1,-1:1})
        nan = Number(0,0)
        assert_equal(nan.flags.factors,{})

class test_PlusTable(NumpyTestCase):

    def check_minf(self):
        lhs = minf
        for rhs, result in [(minf,minf),(inf,nan),(nan,nan),
                            (zero,minf),(one,minf),(mone,minf),
                            (half,minf),(gt1,minf),(lt1,minf),
                            (2,minf)
                            ]:
            assert_equal(lhs + rhs, result,'Op: %s + %s\n' % (lhs,rhs))
            assert_equal(rhs + lhs, result,'Op: %s + %s\n' % (rhs,lhs))

    def check_inf(self):
        lhs = inf
        for rhs, result in [(minf,nan),(inf,inf),(nan,nan),
                            (zero,inf),(one,inf),(mone,inf),
                            (half,inf),(gt1,inf),(lt1,inf),
                            (2,inf)
                            ]:
            assert_equal(lhs + rhs, result,'Op: %s + %s\n' % (lhs,rhs))
            assert_equal(rhs + lhs, result,'Op: %s + %s\n' % (rhs,lhs))

    def check_nan(self):
        lhs = nan
        for rhs, result in [(minf,nan),(inf,nan),(nan,nan),
                            (zero,nan),(one,nan),(mone,nan),
                            (half,nan),(gt1,nan),(lt1,nan),
                            (2,nan)
                            ]:
            assert_equal(lhs + rhs, result,'Op: %s + %s\n' % (lhs,rhs))
            assert_equal(rhs + lhs, result,'Op: %s + %s\n' % (rhs,lhs))

    def check_number(self):
        for lhs in [gt1, lt1, zero, one, mone, half, 2, -1, -3, 0, 1, 3, 5,
                    -gt1, -lt1]:
            for rhs, result in [(minf,minf),(inf,inf),(nan,nan)]:
                assert_equal(lhs + rhs, result,'Op: %s + %s\n' % (lhs,rhs))
                assert_equal(rhs + lhs, result,'Op: %s + %s\n' % (rhs,lhs))

        for lhs,rhs in [(gt1,gt1),(gt1,lt1),(gt1,zero),(gt1,one),(gt1,mone),(gt1,half),
                        (gt1,-gt1),(gt1,-lt1),(gt1,-half),
                        (lt1,lt1),(lt1,zero),(lt1,one),(lt1,mone),(lt1,half),
                        (lt1,-gt1),(lt1,-lt1),(lt1,-half),
                        (zero,zero),(zero,one),(zero,mone),(zero,half),
                        (zero,-gt1),(zero,-lt1),(zero,-half),
                        (one,one),(one,mone),(one,half),(one,-gt1),(one,-lt1),
                        (one,-half),
                        (mone,mone),(mone,half),(half,half),(mone,-gt1),(mone,-lt1),
                        (mone,-half),
                        (half,-gt1),(half,-lt1),(half,-half),
                      ]:
            result=Number(lhs.numer*rhs.denom+lhs.denom*rhs.numer,lhs.denom*rhs.denom)
            assert_equal(lhs + rhs, result,'Op: %s + %s\n' % (lhs,rhs))
            assert_equal(rhs + lhs, result,'Op: %s + %s\n' % (rhs,lhs))

        for r in [2,-3,1,-1,0,-15,16]:
            for lhs,rhs in [(gt1,r), (lt1,r), (zero,r), (one,r), (mone,r),
                            (half,r),
                            ]:
                result = Number(lhs.numer+lhs.denom*rhs,lhs.denom)
                assert_equal(lhs + rhs, result,'Op: %s + %s\n' % (lhs,rhs))
                assert_equal(rhs + lhs, result,'Op: %s + %s\n' % (rhs,lhs))

class test_MulTable(NumpyTestCase):

    def check_minf(self):
        lhs = minf
        for rhs, result in [(minf,inf),(inf,minf),(nan,nan),
                            (zero,nan),(one,minf),(mone,inf),
                            (half,minf),(gt1,minf),(lt1,minf),
                            (2,minf),(-gt1,inf)
                            ]:
            assert_equal(lhs * rhs, result,'Op: %s * %s\n' % (lhs,rhs))
            assert_equal(rhs * lhs, result,'Op: %s * %s\n' % (rhs,lhs))

    def check_inf(self):
        lhs = inf
        for rhs, result in [(minf,minf),(inf,inf),(nan,nan),
                            (zero,nan),(one,inf),(mone,minf),
                            (half,inf),(gt1,inf),(lt1,inf),
                            (-gt1,minf), (2,inf)
                            ]:
            assert_equal(lhs * rhs, result,'Op: %s * %s\n' % (lhs,rhs))
            assert_equal(rhs * lhs, result,'Op: %s * %s\n' % (rhs,lhs))    

    def check_nan(self):
        lhs = nan
        for rhs, result in [(minf,nan),(inf,nan),(nan,nan),
                            (zero,nan),(one,nan),(mone,nan),
                            (half,nan),(gt1,nan),(lt1,nan),
                            (2,nan),(-gt1,nan)
                            ]:
            assert_equal(lhs * rhs, result,'Op: %s * %s\n' % (lhs,rhs))
            assert_equal(rhs * lhs, result,'Op: %s * %s\n' % (rhs,lhs))    

    def check_zero(self):
        lhs = zero
        for rhs, result in [(minf,nan),(inf,nan),(nan,nan),
                            (zero,zero),(one,zero),(mone,zero),
                            (half,zero),(gt1,zero),(lt1,zero),
                            (2,zero),(sym,zero)
                            ]:
            assert_equal(lhs * rhs, result,'Op: %s * %s\n' % (lhs,rhs))
            assert_equal(rhs * lhs, result,'Op: %s * %s\n' % (rhs,lhs))    

    def check_number(self):
        for lhs in [zero,one,mone,half,gt1,lt1,-gt1,-lt1]:
            for rhs in [zero,one,mone,half,gt1,lt1]:
                result = Rational(lhs.numer*rhs.numer, lhs.denom*rhs.denom)
                assert_equal(lhs * rhs, result,'Op: %s * %s\n' % (lhs,rhs))
                assert_equal(rhs * lhs, result,'Op: %s * %s\n' % (rhs,lhs))

class test_PowerTable(NumpyTestCase):

    def check_minf(self):
        base = minf
        for exp, result in [(minf,nan),(inf,nan),(nan,nan),(zero,one),
                            (mone,zero),(one,minf),(2,inf),(3,minf),
                            (-2,zero),(-3,zero), (-lt1,zero), (-gt1,zero),
                            (gt1,-I*inf),
                            (lt1,inf*mone ** (one/4)),
                            (one/3*5,minf * mone ** (one/3*2)),
                            ]:
            assert_equal(base ** exp, result,'Op: %s ** %s\n' % (base,exp))

    def check_inf(self):
        base = inf
        for exp, result in [(minf,zero),(inf,inf),(nan,nan),(zero,one),
                            (mone,zero),(one,inf),(2,inf),(3,inf),
                            (-2,zero),(-3,zero), (-lt1,zero), (-gt1,zero),
                            (gt1,inf),(lt1,inf),(one/3*5,inf),
                            ]:
            assert_equal(base ** exp, result,'Op: %s ** %s\n' % (base,exp))

    def check_nan(self):
        base = nan
        for exp, result in [(minf,nan),(inf,nan),(nan,nan),(zero,one),
                            (mone,nan),(one,nan),(2,nan),(3,nan),
                            (-2,nan),(-3,nan), (-lt1,nan), (-gt1,nan),
                            (gt1,nan),(lt1,nan),(one/3*5,nan),
                            ]:
            assert_equal(base ** exp, result,'Op: %s ** %s\n' % (base,exp))

    def check_zero(self):
        base = zero
        for exp, result in [(minf,inf),(inf,zero),(nan,zero),(zero,one),
                            (mone,inf),(one,zero),(2,zero),(3,zero),
                            (-2,inf),(-3,inf), (-lt1,inf), (-gt1,inf),
                            (gt1,zero),(lt1,zero),(one/3*5,zero),
                            ]:
            assert_equal(base ** exp, result,'Op: %s ** %s\n' % (base,exp))
        base = 0
        for exp, result in [(minf,inf),(inf,zero),(nan,zero),(zero,one),
                            (mone,inf),(one,zero),
                            (-lt1,inf), (-gt1,inf),
                            (gt1,zero),(lt1,zero),(one/3*5,zero),
                            ]:
            assert_equal(base ** exp, result,'Op: %s ** %s\n' % (base,exp))

    def check_positive_integer(self):
        base = Integer(2)
        for exp, result in [(minf,zero),(inf,inf),(nan,nan),(zero,one),
                            (mone, half),(one,base),(2,Integer(4)),
                            (3,Integer(8)),(-2,Rational(1,4)),(-3,Rational(1,8)),
                            (-lt1,Mul(half, Power(2,Rational(3,4)))),
                            (-gt1,Rational(1,4)* 2**half),
                            (lt1,Power(2,Rational(1,4))),(gt1,Mul(2,Power(2,half)))]:
            assert_equal(base ** exp, result,'Op: %s ** %s\n' % (base,exp))

    def check_negative_integer(self):
        base = Integer(-2)
        for exp, result in [(minf,zero),(inf,inf+inf*I),(nan,nan),(zero,one),
                            (mone, -half),(one,base),(2,Integer(4)),
                            (3,Integer(-8)),(-2,Rational(1,4)),(-3,Rational(-1,8)),
                            (-lt1,Mul(-half,Power(-2,Rational(3,4)))),
                            (-gt1,Mul(Rational(1,4),Power(-2,half))),
                            (lt1,Power(-2,Rational(1,4))),(gt1,Mul(-2,Power(-2,half)))]:
            assert_equal(base ** exp, result,'Op: %s ** %s\n' % (base,exp))

    def check_rational(self):
        n = Rational(3,8)
        assert_equal(n**2,Rational(9,64))
        assert_equal(n**(one/3),Rational(1,8) * 3**(one/3) * 8 ** Rational(2,3))
        assert_equal((Integer(-4)**(one/2)).tostr(),'(-4) ** (1/2)')


if __name__=='__main__':
    NumpyTest().run()
