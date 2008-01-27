
from sympycore.calculus import oo, moo, zoo, undefined, I, Calculus

zero = Calculus.Number(0)
one = Calculus.Number(1)
mone = Calculus.Number(-1)
two = Calculus.Number(2)
mtwo = Calculus.Number(-2)
half = Calculus.Number(1)/2
mhalf = Calculus.Number(-1)/2
onehalf = Calculus.Number(3)/2
monehalf = Calculus.Number(-3)/2

def test_moo_optable():
    assert moo + moo == moo
    assert moo + mtwo == moo
    assert moo + monehalf == moo
    assert moo + mone == moo
    assert moo + mhalf == moo
    assert moo + zero == moo
    assert moo + half == moo
    assert moo + one == moo
    assert moo + onehalf == moo
    assert moo + two == moo
    assert moo + oo == undefined
    assert moo + undefined == undefined

    assert moo - moo == undefined
    assert moo - mtwo == moo
    assert moo - monehalf == moo
    assert moo - mone == moo
    assert moo - mhalf == moo
    assert moo - zero == moo
    assert moo - half == moo
    assert moo - one == moo
    assert moo - onehalf == moo
    assert moo - two == moo
    assert moo - oo == moo
    assert moo - undefined == undefined

    assert moo * moo == oo
    assert moo * mtwo == oo
    assert moo * monehalf == oo
    assert moo * mone == oo
    assert moo * mhalf == oo
    assert moo * zero == undefined
    assert moo * half == moo
    assert moo * one == moo
    assert moo * onehalf == moo
    assert moo * two == moo
    assert moo * oo == moo
    assert moo * undefined == undefined

    assert moo / moo == undefined
    assert moo / mtwo == oo
    assert moo / monehalf == oo
    assert moo / mone == oo
    assert moo / mhalf == oo
    assert moo / zero == moo
    assert moo / half == moo
    assert moo / one == moo
    assert moo / onehalf == moo
    assert moo / two == moo
    assert moo / oo == undefined
    assert moo / undefined == undefined

    assert moo ** moo == zero
    assert moo ** mtwo == zero
    assert moo ** monehalf == zero
    assert moo ** mone == zero
    assert moo ** mhalf == zero
    assert moo ** zero == one
    assert moo ** half == I*oo
    assert moo ** one == moo
    assert moo ** onehalf == I*oo
    assert moo ** two == oo
    assert moo ** oo == undefined
    assert moo ** undefined == undefined

def test_mtwo_optable():
    assert mtwo + moo == moo
    assert mtwo + oo == oo
    assert mtwo + undefined == undefined

    assert mtwo - moo == oo
    assert mtwo - oo == moo
    assert mtwo - undefined == undefined

    assert mtwo * moo == oo
    assert mtwo * oo == moo
    assert mtwo * undefined == undefined

    assert mtwo / moo == zero
    assert mhalf / zero == moo
    assert mtwo / oo == zero
    assert mtwo / undefined == undefined

    assert mtwo ** moo == zero
    assert mtwo ** oo == undefined
    assert mtwo ** undefined == undefined

def test_monehalf_optable():
    assert monehalf + moo == moo
    assert monehalf + oo == oo
    assert monehalf + undefined == undefined

    assert monehalf - moo == oo
    assert monehalf - oo == moo
    assert monehalf - undefined == undefined

    assert monehalf * moo == oo
    assert monehalf * oo == moo
    assert monehalf * undefined == undefined

    assert monehalf / moo == zero
    assert mhalf / zero == moo
    assert monehalf / oo == zero
    assert monehalf / undefined == undefined

    assert monehalf ** moo == zero
    assert monehalf ** oo == undefined
    assert monehalf ** undefined == undefined

def test_mone_optable():
    assert mone + moo == moo
    assert mone + oo == oo
    assert mone + undefined == undefined

    assert mone - moo == oo
    assert mone - oo == moo
    assert mone - undefined == undefined

    assert mone * moo == oo
    assert mone * oo == moo
    assert mone * undefined == undefined

    assert mone / moo == zero
    assert mhalf / zero == moo
    assert mone / oo == zero
    assert mone / undefined == undefined

    assert mone ** moo == undefined
    assert mone ** oo == undefined
    assert mone ** undefined == undefined

def test_mhalf_optable():
    assert mhalf + moo == moo
    assert mhalf + oo == oo
    assert mhalf + undefined == undefined

    assert mhalf - moo == oo
    assert mhalf - oo == moo
    assert mhalf - undefined == undefined

    assert mhalf * moo == oo
    assert mhalf * oo == moo
    assert mhalf * undefined == undefined

    assert mhalf / moo == zero
    assert mhalf / zero == moo
    assert mhalf / oo == zero
    assert mhalf / undefined == undefined

    assert mhalf ** moo == undefined
    assert mhalf ** oo == zero
    assert mhalf ** undefined == undefined

def test_zero_optable():
    assert zero + moo == moo
    assert zero + oo == oo
    assert zero + undefined == undefined

    assert zero - moo == oo
    assert zero - oo == moo
    assert zero - undefined == undefined

    assert zero * moo == undefined
    assert zero * oo == undefined
    assert zero * undefined == undefined

    assert zero / moo == zero
    assert zero / zero == undefined
    assert zero / oo == zero
    assert zero / undefined == undefined

    assert zero ** moo == undefined
    assert zero ** oo == zero
    assert zero ** undefined == undefined

def test_half_optable():
    assert half + moo == moo
    assert half + oo == oo
    assert half + undefined == undefined

    assert half - moo == oo
    assert half - oo == moo
    assert half - undefined == undefined

    assert half * moo == moo
    assert half * oo == oo
    assert half * undefined == undefined

    assert half / moo == zero
    assert half / zero == oo
    assert half / oo == zero
    assert half / undefined == undefined

    assert half ** moo == oo
    assert half ** oo == zero
    assert half ** undefined == undefined

def test_one_optable():
    assert one + moo == moo
    assert one + oo == oo
    assert one + undefined == undefined

    assert one - moo == oo
    assert one - oo == moo
    assert one - undefined == undefined

    assert one * moo == moo
    assert one * oo == oo
    assert one * undefined == undefined

    assert one / moo == zero
    assert one / zero == oo
    assert one / oo == zero
    assert one / undefined == undefined

    assert one ** moo == one
    assert one ** oo == one
    assert one ** undefined == one

def test_onehalf_optable():
    assert onehalf + moo == moo
    assert onehalf + oo == oo
    assert onehalf + undefined == undefined

    assert onehalf - moo == oo
    assert onehalf - oo == moo
    assert onehalf - undefined == undefined

    assert onehalf * moo == moo
    assert onehalf * oo == oo
    assert onehalf * undefined == undefined

    assert onehalf / moo == zero
    assert onehalf / zero == oo
    assert onehalf / oo == zero
    assert onehalf / undefined == undefined

    assert onehalf ** moo == zero
    assert onehalf ** oo == oo
    assert onehalf ** undefined == undefined

def test_two_optable():
    assert two + moo == moo
    assert two + oo == oo
    assert two + undefined == undefined

    assert two - moo == oo
    assert two - oo == moo
    assert two - undefined == undefined

    assert two * moo == moo
    assert two * oo == oo
    assert two * undefined == undefined

    assert two / moo == zero
    assert two / zero == oo
    assert two / oo == zero
    assert two / undefined == undefined

    assert two ** moo == zero
    assert two ** oo == oo
    assert two ** undefined == undefined

def test_oo_optable():
    assert oo + moo == undefined
    assert oo + mtwo == oo
    assert oo + monehalf == oo
    assert oo + mone == oo
    assert oo + mhalf == oo
    assert oo + zero == oo
    assert oo + half == oo
    assert oo + one == oo
    assert oo + onehalf == oo
    assert oo + two == oo
    assert oo + oo == oo
    assert oo + undefined == undefined

    assert oo - moo == oo
    assert oo - mtwo == oo
    assert oo - monehalf == oo
    assert oo - mone == oo
    assert oo - mhalf == oo
    assert oo - zero == oo
    assert oo - half == oo
    assert oo - one == oo
    assert oo - onehalf == oo
    assert oo - two == oo
    assert oo - oo == undefined
    assert oo - undefined == undefined

    assert oo * moo == moo
    assert oo * mtwo == moo
    assert oo * monehalf == moo
    assert oo * mone == moo
    assert oo * mhalf == moo
    assert oo * zero == undefined
    assert oo * half == oo
    assert oo * one == oo
    assert oo * onehalf == oo
    assert oo * two == oo
    assert oo * oo == oo
    assert oo * undefined == undefined

    assert oo / moo == undefined
    assert oo / mtwo == moo
    assert oo / monehalf == moo
    assert oo / mone == moo
    assert oo / mhalf == moo
    assert oo / zero == oo
    assert oo / half == oo
    assert oo / one == oo
    assert oo / onehalf == oo
    assert oo / two == oo
    assert oo / oo == undefined
    assert oo / undefined == undefined

    assert oo ** moo == zero
    assert oo ** mtwo == zero
    assert oo ** monehalf == zero
    assert oo ** mone == zero
    assert oo ** mhalf == zero
    assert oo ** zero == one
    assert oo ** half == oo
    assert oo ** one == oo
    assert oo ** onehalf == oo
    assert oo ** two == oo
    assert oo ** oo == oo
    assert oo ** undefined == undefined

def test_undefined_optable():
    assert undefined + moo == undefined
    assert undefined + mtwo == undefined
    assert undefined + monehalf == undefined
    assert undefined + mone == undefined
    assert undefined + mhalf == undefined
    assert undefined + zero == undefined
    assert undefined + half == undefined
    assert undefined + one == undefined
    assert undefined + onehalf == undefined
    assert undefined + two == undefined
    assert undefined + oo == undefined
    assert undefined + undefined == undefined

    assert undefined - moo == undefined
    assert undefined - mtwo == undefined
    assert undefined - monehalf == undefined
    assert undefined - mone == undefined
    assert undefined - mhalf == undefined
    assert undefined - zero == undefined
    assert undefined - half == undefined
    assert undefined - one == undefined
    assert undefined - onehalf == undefined
    assert undefined - two == undefined
    assert undefined - oo == undefined
    assert undefined - undefined == undefined

    assert undefined * moo == undefined
    assert undefined * mtwo == undefined
    assert undefined * monehalf == undefined
    assert undefined * mone == undefined
    assert undefined * mhalf == undefined
    assert undefined * zero == undefined
    assert undefined * half == undefined
    assert undefined * one == undefined
    assert undefined * onehalf == undefined
    assert undefined * two == undefined
    assert undefined * oo == undefined
    assert undefined * undefined == undefined

    assert undefined / moo == undefined
    assert undefined / mtwo == undefined
    assert undefined / monehalf == undefined
    assert undefined / mone == undefined
    assert undefined / mhalf == undefined
    assert undefined / zero == undefined
    assert undefined / half == undefined
    assert undefined / one == undefined
    assert undefined / onehalf == undefined
    assert undefined / two == undefined
    assert undefined / oo == undefined
    assert undefined / undefined == undefined

    assert undefined ** moo == undefined
    assert undefined ** mtwo == undefined
    assert undefined ** monehalf == undefined
    assert undefined ** mone == undefined
    assert undefined ** mhalf == undefined
    assert undefined ** zero == one
    assert undefined ** half == undefined
    assert undefined ** one == undefined
    assert undefined ** onehalf == undefined
    assert undefined ** two == undefined
    assert undefined ** oo == undefined
    assert undefined ** undefined == undefined
