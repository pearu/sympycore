
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
