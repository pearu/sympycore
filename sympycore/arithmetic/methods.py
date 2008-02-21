"""
This file is generated by the sympycore/arithmetic/mk_methods.py script.
DO NOT CHANGE THIS FILE DIRECTLY!!!
"""

from .numbers import Complex, Float, FractionTuple




def fraction_add(self, other, cls=FractionTuple):
    t = type(other)
    #IF_CHECK_INT(T=t)
    if t is int or t is long:
        #ADD_FRACTION_INT(LHS=self; RHS=other)
        p, q = self
        #RETURN_FRACTION(NUMER=p+q*(other); DENOM=q)
        return cls((p+q*(other), q))
    elif t is cls:
        #ADD_FRACTION_FRACTION(LHS=self; RHS=other)
        #ADDOP_FRACTION_FRACTION(LHS=self; RHS=other; SIGN=+; MOD=%)
        p, q = self
        r, s = other
        _tmp6 = p*s + q*r
        if not _tmp6:
            return 0
        #RETURN_FRACTION2(NUMER=_tmp6; DENOM=q*s; MOD=%)
        #FRACTION_NORMALIZE(NUMER=_tmp6; DENOM=q*s; RNUMER=_p; RDENOM=_q; MOD=%)
        _p = _x = _tmp6
        _q = _y = q*s
        while _y:
            _x, _y = _y, _x % _y
        if _x != 1:
            _p //= _x
            _q //= _x
        if _q == 1:
            return _p
        #RETURN_FRACTION(NUMER=_p; DENOM=_q)
        return cls((_p, _q))
    return NotImplemented

def fraction_sub(self, other, cls=FractionTuple):
    t = type(other)
    #IF_CHECK_INT(T=t)
    if t is int or t is long:
        #SUB_FRACTION_INT(LHS=self; RHS=other)
        p, q = self
        #RETURN_FRACTION(NUMER=p-q*(other); DENOM=q)
        return cls((p-q*(other), q))
    elif t is cls:
        #SUB_FRACTION_FRACTION(LHS=self; RHS=other)
        #ADDOP_FRACTION_FRACTION(LHS=self; RHS=other; SIGN=-; MOD=%)
        p, q = self
        r, s = other
        _tmp14 = p*s - q*r
        if not _tmp14:
            return 0
        #RETURN_FRACTION2(NUMER=_tmp14; DENOM=q*s; MOD=%)
        #FRACTION_NORMALIZE(NUMER=_tmp14; DENOM=q*s; RNUMER=_p; RDENOM=_q; MOD=%)
        _p = _x = _tmp14
        _q = _y = q*s
        while _y:
            _x, _y = _y, _x % _y
        if _x != 1:
            _p //= _x
            _q //= _x
        if _q == 1:
            return _p
        #RETURN_FRACTION(NUMER=_p; DENOM=_q)
        return cls((_p, _q))
    return NotImplemented

def fraction_rsub(self, other, cls=FractionTuple):
    t = type(other)
    #IF_CHECK_INT(T=t)
    if t is int or t is long:
        #SUB_INT_FRACTION(RHS=self; LHS=other)
        p, q = self
        #RETURN_FRACTION(NUMER=q*(other) - p; DENOM=q)
        return cls((q*(other) - p, q))
    return NotImplemented

def fraction_mul(self, other, cls=FractionTuple):
    t = type(other)
    #IF_CHECK_INT(T=t)
    if t is int or t is long:
        #MUL_FRACTION_INT(LHS=self; RHS=other; MOD=%)
        p, q = self
        #RETURN_FRACTION2(NUMER=p*other; DENOM=q; MOD=%)
        #FRACTION_NORMALIZE(NUMER=p*other; DENOM=q; RNUMER=_p; RDENOM=_q; MOD=%)
        _p = _x = p*other
        _q = _y = q
        while _y:
            _x, _y = _y, _x % _y
        if _x != 1:
            _p //= _x
            _q //= _x
        if _q == 1:
            return _p
        #RETURN_FRACTION(NUMER=_p; DENOM=_q)
        return cls((_p, _q))
    elif t is cls:
        #MUL_FRACTION_FRACTION(LHS=self; RHS=other; MOD=%)
        p, q = self
        r, s = other
        #RETURN_FRACTION2(NUMER=p*r; DENOM=q*s; MOD=%)
        #FRACTION_NORMALIZE(NUMER=p*r; DENOM=q*s; RNUMER=_p; RDENOM=_q; MOD=%)
        _p = _x = p*r
        _q = _y = q*s
        while _y:
            _x, _y = _y, _x % _y
        if _x != 1:
            _p //= _x
            _q //= _x
        if _q == 1:
            return _p
        #RETURN_FRACTION(NUMER=_p; DENOM=_q)
        return cls((_p, _q))
    return NotImplemented

def fraction_div(self, other, cls=FractionTuple):
    t = type(other)
    #IF_CHECK_INT(T=t)
    if t is int or t is long:
        #DIV_FRACTION_INT(LHS=self; RHS=other; MOD=%)
        p, q = self
        #RETURN_FRACTION2(NUMER=p; DENOM=q*other; MOD=%)
        #FRACTION_NORMALIZE(NUMER=p; DENOM=q*other; RNUMER=_p; RDENOM=_q; MOD=%)
        _p = _x = p
        _q = _y = q*other
        while _y:
            _x, _y = _y, _x % _y
        if _x != 1:
            _p //= _x
            _q //= _x
        if _q == 1:
            return _p
        #RETURN_FRACTION(NUMER=_p; DENOM=_q)
        return cls((_p, _q))
    elif t is cls:
        #DIV_FRACTION_FRACTION(LHS=self; RHS=other; MOD=%)
        p, q = self
        r, s = other
        #RETURN_FRACTION2(NUMER=p*s; DENOM=q*r; MOD=%)
        #FRACTION_NORMALIZE(NUMER=p*s; DENOM=q*r; RNUMER=_p; RDENOM=_q; MOD=%)
        _p = _x = p*s
        _q = _y = q*r
        while _y:
            _x, _y = _y, _x % _y
        if _x != 1:
            _p //= _x
            _q //= _x
        if _q == 1:
            return _p
        #RETURN_FRACTION(NUMER=_p; DENOM=_q)
        return cls((_p, _q))
    return NotImplemented

def fraction_rdiv(self, other, cls=FractionTuple):
    t = type(other)
    #IF_CHECK_INT(T=t)
    if t is int or t is long:
        #DIV_INT_FRACTION(RHS=self; LHS=other; MOD=%)
        p, q = self
        #RETURN_FRACTION2(NUMER=other*q; DENOM=p; MOD=%)
        #FRACTION_NORMALIZE(NUMER=other*q; DENOM=p; RNUMER=_p; RDENOM=_q; MOD=%)
        _p = _x = other*q
        _q = _y = p
        while _y:
            _x, _y = _y, _x % _y
        if _x != 1:
            _p //= _x
            _q //= _x
        if _q == 1:
            return _p
        #RETURN_FRACTION(NUMER=_p; DENOM=_q)
        return cls((_p, _q))
    return NotImplemented

def fraction_pow(self, other, m=None, cls=FractionTuple):
    t = type(other)
    #IF_CHECK_INT(T=t)
    if t is int or t is long:
        if not other:
            return 1
        if other==1:
            return self
        #POW_FRACTION_INT(LHS=self; RHS=other)
        _tmp45 = other
        p, q = self
        if _tmp45 > 0:
            #RETURN_FRACTION(NUMER=p**_tmp45; DENOM=q**_tmp45)
            return cls((p**_tmp45, q**_tmp45))
        _tmp45 = -_tmp45
        if p > 0:
            #RETURN_FRACTION(NUMER=q**_tmp45; DENOM=p**_tmp45)
            return cls((q**_tmp45, p**_tmp45))
        #RETURN_FRACTION(NUMER=(-q)**_tmp45; DENOM=(-p)**_tmp45)
        return cls(((-q)**_tmp45, (-p)**_tmp45))
    return NotImplemented

def complex_add(self, other, new=object.__new__, cls=Complex):
    t = type(other)
    #IF_CHECK_REAL(T=t)
    if t is int or t is long or t is FractionTuple or t is float or t is Float:
        #ADD_COMPLEX_REAL(LHS=self; RHS=other)
        #RETURN_COMPLEX(REAL=self.real + other; IMAG=self.imag)
        _tmp51 = new(cls)
        _tmp51.real = self.real + other
        _tmp51.imag = self.imag
        return _tmp51
    #IF_CHECK_COMPLEX(T=t)
    if t is cls or t is complex:
        #ADD_COMPLEX_COMPLEX(LHS=self; RHS=other)
        #RETURN_COMPLEX2(REAL=self.real + other.real; IMAG=self.imag + other.imag)
        _tmp54 = self.imag + other.imag
        if not _tmp54:
            return self.real + other.real
        #RETURN_COMPLEX(REAL=self.real + other.real; IMAG=_tmp54)
        _tmp55 = new(cls)
        _tmp55.real = self.real + other.real
        _tmp55.imag = _tmp54
        return _tmp55
    return NotImplemented

def complex_sub(self, other, new=object.__new__, cls=Complex):
    t = type(other)
    #IF_CHECK_REAL(T=t)
    if t is int or t is long or t is FractionTuple or t is float or t is Float:
        #SUB_COMPLEX_REAL(LHS=self; RHS=other)
        #RETURN_COMPLEX(REAL=self.real - other; IMAG=self.imag)
        _tmp58 = new(cls)
        _tmp58.real = self.real - other
        _tmp58.imag = self.imag
        return _tmp58
    #IF_CHECK_COMPLEX(T=t)
    if t is cls or t is complex:
        #SUB_COMPLEX_COMPLEX(LHS=self; RHS=other)
        #RETURN_COMPLEX2(REAL=self.real - other.real; IMAG=self.imag - other.imag)
        _tmp61 = self.imag - other.imag
        if not _tmp61:
            return self.real - other.real
        #RETURN_COMPLEX(REAL=self.real - other.real; IMAG=_tmp61)
        _tmp62 = new(cls)
        _tmp62.real = self.real - other.real
        _tmp62.imag = _tmp61
        return _tmp62
    return NotImplemented

def complex_rsub(self, other, new=object.__new__, cls=Complex):
    t = type(other)
    #IF_CHECK_REAL(T=t)
    if t is int or t is long or t is FractionTuple or t is float or t is Float:
        #SUB_REAL_COMPLEX(LHS=other; RHS=self)
        #RETURN_COMPLEX(REAL=other - self.real; IMAG=-self.imag)
        _tmp65 = new(cls)
        _tmp65.real = other - self.real
        _tmp65.imag = -self.imag
        return _tmp65
    if t is complex:
        #SUB_COMPLEX_COMPLEX(LHS=other; RHS=self)
        #RETURN_COMPLEX2(REAL=other.real - self.real; IMAG=other.imag - self.imag)
        _tmp67 = other.imag - self.imag
        if not _tmp67:
            return other.real - self.real
        #RETURN_COMPLEX(REAL=other.real - self.real; IMAG=_tmp67)
        _tmp68 = new(cls)
        _tmp68.real = other.real - self.real
        _tmp68.imag = _tmp67
        return _tmp68
    return NotImplemented

def complex_mul(self, other, new=object.__new__, cls=Complex):
    t = type(other)
    #IF_CHECK_REAL(T=t)
    if t is int or t is long or t is FractionTuple or t is float or t is Float:
        #MUL_COMPLEX_REAL(LHS=self; RHS=other)
        #RETURN_COMPLEX(REAL=self.real*other; IMAG=self.imag*other)
        _tmp71 = new(cls)
        _tmp71.real = self.real*other
        _tmp71.imag = self.imag*other
        return _tmp71
    #IF_CHECK_COMPLEX(T=t)
    if t is cls or t is complex:
        #MUL_COMPLEX_COMPLEX(LHS=self; RHS=other)
        a, b = self.real, self.imag
        c, d = other.real, other.imag
        #RETURN_COMPLEX2(REAL=a*c-b*d; IMAG=b*c+a*d)
        _tmp74 = b*c+a*d
        if not _tmp74:
            return a*c-b*d
        #RETURN_COMPLEX(REAL=a*c-b*d; IMAG=_tmp74)
        _tmp75 = new(cls)
        _tmp75.real = a*c-b*d
        _tmp75.imag = _tmp74
        return _tmp75
    return NotImplemented

def complex_div(self, other, new=object.__new__, cls=Complex):
    t = type(other)
    #IF_CHECK_REAL(T=t)
    if t is int or t is long or t is FractionTuple or t is float or t is Float:
        #DIV_COMPLEX_REAL(LHS=self; RHS=other; MOD=%)
        #DIV_VALUE_VALUE(LHS=self.real; RHS=other; RESULT=re; MOD=%)
        _p, _q = self.real, other
        if not _q:
            raise ZeroDivisionError(repr(self.real) + " / " + repr(other))
        _tp = type(_p)
        #IF_CHECK_INT(T=_tp)
        if _tp is int or _tp is long:
            _tq = type(_q)
            #IF_CHECK_INT(T=_tq)
            if _tq is int or _tq is long:
                #FRACTION_NORMALIZE(NUMER=_p; DENOM=_q; RNUMER=_rp; RDENOM=_rq; MOD=%)
                _rp = _x = _p
                _rq = _y = _q
                while _y:
                    _x, _y = _y, _x % _y
                if _x != 1:
                    _rp //= _x
                    _rq //= _x
                if _rq == 1:
                    re = _rp
                else:
                    re = FractionTuple((_rp, _rq))
            else:
                re = _p / _q
        else:
            re = _p / _q
        #DIV_VALUE_VALUE(LHS=self.imag; RHS=other; RESULT=im; MOD=%)
        _p, _q = self.imag, other
        if not _q:
            raise ZeroDivisionError(repr(self.imag) + " / " + repr(other))
        _tp = type(_p)
        #IF_CHECK_INT(T=_tp)
        if _tp is int or _tp is long:
            _tq = type(_q)
            #IF_CHECK_INT(T=_tq)
            if _tq is int or _tq is long:
                #FRACTION_NORMALIZE(NUMER=_p; DENOM=_q; RNUMER=_rp; RDENOM=_rq; MOD=%)
                _rp = _x = _p
                _rq = _y = _q
                while _y:
                    _x, _y = _y, _x % _y
                if _x != 1:
                    _rp //= _x
                    _rq //= _x
                if _rq == 1:
                    im = _rp
                else:
                    im = FractionTuple((_rp, _rq))
            else:
                im = _p / _q
        else:
            im = _p / _q
        #RETURN_COMPLEX(REAL=re; IMAG=im)
        _tmp86 = new(cls)
        _tmp86.real = re
        _tmp86.imag = im
        return _tmp86
    #IF_CHECK_COMPLEX(T=t)
    if t is cls or t is complex:
        #DIV_COMPLEX_COMPLEX(LHS=self; RHS=other; MOD=%)
        a, b = self.real, self.imag
        c, d = other.real, other.imag
        mag = c*c + d*d
        _tmp88 = b*c-a*d
        #DIV_VALUE_VALUE(LHS=a*c+b*d; RHS=mag; RESULT=re; MOD=%)
        _p, _q = a*c+b*d, mag
        if not _q:
            raise ZeroDivisionError(repr(a*c+b*d) + " / " + repr(mag))
        _tp = type(_p)
        #IF_CHECK_INT(T=_tp)
        if _tp is int or _tp is long:
            _tq = type(_q)
            #IF_CHECK_INT(T=_tq)
            if _tq is int or _tq is long:
                #FRACTION_NORMALIZE(NUMER=_p; DENOM=_q; RNUMER=_rp; RDENOM=_rq; MOD=%)
                _rp = _x = _p
                _rq = _y = _q
                while _y:
                    _x, _y = _y, _x % _y
                if _x != 1:
                    _rp //= _x
                    _rq //= _x
                if _rq == 1:
                    re = _rp
                else:
                    re = FractionTuple((_rp, _rq))
            else:
                re = _p / _q
        else:
            re = _p / _q
        if not _tmp88:
            return re
        #DIV_VALUE_VALUE(LHS=_tmp88; RHS=mag; RESULT=im; MOD=%)
        _p, _q = _tmp88, mag
        if not _q:
            raise ZeroDivisionError(repr(_tmp88) + " / " + repr(mag))
        _tp = type(_p)
        #IF_CHECK_INT(T=_tp)
        if _tp is int or _tp is long:
            _tq = type(_q)
            #IF_CHECK_INT(T=_tq)
            if _tq is int or _tq is long:
                #FRACTION_NORMALIZE(NUMER=_p; DENOM=_q; RNUMER=_rp; RDENOM=_rq; MOD=%)
                _rp = _x = _p
                _rq = _y = _q
                while _y:
                    _x, _y = _y, _x % _y
                if _x != 1:
                    _rp //= _x
                    _rq //= _x
                if _rq == 1:
                    im = _rp
                else:
                    im = FractionTuple((_rp, _rq))
            else:
                im = _p / _q
        else:
            im = _p / _q
        #RETURN_COMPLEX(REAL=re; IMAG=im)
        _tmp97 = new(cls)
        _tmp97.real = re
        _tmp97.imag = im
        return _tmp97
    return NotImplemented

def complex_rdiv(self, other, new=object.__new__, cls=Complex):
    t = type(other)
    #IF_CHECK_REAL(T=t)
    if t is int or t is long or t is FractionTuple or t is float or t is Float:
        #DIV_REAL_COMPLEX(LHS=other; RHS=self; MOD=%)
        _tmp99 = other
        c, d = self.real, self.imag
        mag = c*c + d*d
        #DIV_VALUE_VALUE(LHS=-_tmp99*d; RHS=mag; RESULT=im; MOD=%)
        _p, _q = -_tmp99*d, mag
        if not _q:
            raise ZeroDivisionError(repr(-_tmp99*d) + " / " + repr(mag))
        _tp = type(_p)
        #IF_CHECK_INT(T=_tp)
        if _tp is int or _tp is long:
            _tq = type(_q)
            #IF_CHECK_INT(T=_tq)
            if _tq is int or _tq is long:
                #FRACTION_NORMALIZE(NUMER=_p; DENOM=_q; RNUMER=_rp; RDENOM=_rq; MOD=%)
                _rp = _x = _p
                _rq = _y = _q
                while _y:
                    _x, _y = _y, _x % _y
                if _x != 1:
                    _rp //= _x
                    _rq //= _x
                if _rq == 1:
                    im = _rp
                else:
                    im = FractionTuple((_rp, _rq))
            else:
                im = _p / _q
        else:
            im = _p / _q
        #DIV_VALUE_VALUE(LHS= _tmp99*c; RHS=mag; RESULT=re; MOD=%)
        _p, _q = _tmp99*c, mag
        if not _q:
            raise ZeroDivisionError(repr(_tmp99*c) + " / " + repr(mag))
        _tp = type(_p)
        #IF_CHECK_INT(T=_tp)
        if _tp is int or _tp is long:
            _tq = type(_q)
            #IF_CHECK_INT(T=_tq)
            if _tq is int or _tq is long:
                #FRACTION_NORMALIZE(NUMER=_p; DENOM=_q; RNUMER=_rp; RDENOM=_rq; MOD=%)
                _rp = _x = _p
                _rq = _y = _q
                while _y:
                    _x, _y = _y, _x % _y
                if _x != 1:
                    _rp //= _x
                    _rq //= _x
                if _rq == 1:
                    re = _rp
                else:
                    re = FractionTuple((_rp, _rq))
            else:
                re = _p / _q
        else:
            re = _p / _q
        #RETURN_COMPLEX(REAL=re; IMAG=im)
        _tmp108 = new(cls)
        _tmp108.real = re
        _tmp108.imag = im
        return _tmp108
    if t is complex:
        #DIV_COMPLEX_COMPLEX(LHS=other; RHS=self; MOD=%)
        a, b = other.real, other.imag
        c, d = self.real, self.imag
        mag = c*c + d*d
        _tmp109 = b*c-a*d
        #DIV_VALUE_VALUE(LHS=a*c+b*d; RHS=mag; RESULT=re; MOD=%)
        _p, _q = a*c+b*d, mag
        if not _q:
            raise ZeroDivisionError(repr(a*c+b*d) + " / " + repr(mag))
        _tp = type(_p)
        #IF_CHECK_INT(T=_tp)
        if _tp is int or _tp is long:
            _tq = type(_q)
            #IF_CHECK_INT(T=_tq)
            if _tq is int or _tq is long:
                #FRACTION_NORMALIZE(NUMER=_p; DENOM=_q; RNUMER=_rp; RDENOM=_rq; MOD=%)
                _rp = _x = _p
                _rq = _y = _q
                while _y:
                    _x, _y = _y, _x % _y
                if _x != 1:
                    _rp //= _x
                    _rq //= _x
                if _rq == 1:
                    re = _rp
                else:
                    re = FractionTuple((_rp, _rq))
            else:
                re = _p / _q
        else:
            re = _p / _q
        if not _tmp109:
            return re
        #DIV_VALUE_VALUE(LHS=_tmp109; RHS=mag; RESULT=im; MOD=%)
        _p, _q = _tmp109, mag
        if not _q:
            raise ZeroDivisionError(repr(_tmp109) + " / " + repr(mag))
        _tp = type(_p)
        #IF_CHECK_INT(T=_tp)
        if _tp is int or _tp is long:
            _tq = type(_q)
            #IF_CHECK_INT(T=_tq)
            if _tq is int or _tq is long:
                #FRACTION_NORMALIZE(NUMER=_p; DENOM=_q; RNUMER=_rp; RDENOM=_rq; MOD=%)
                _rp = _x = _p
                _rq = _y = _q
                while _y:
                    _x, _y = _y, _x % _y
                if _x != 1:
                    _rp //= _x
                    _rq //= _x
                if _rq == 1:
                    im = _rp
                else:
                    im = FractionTuple((_rp, _rq))
            else:
                im = _p / _q
        else:
            im = _p / _q
        #RETURN_COMPLEX(REAL=re; IMAG=im)
        _tmp118 = new(cls)
        _tmp118.real = re
        _tmp118.imag = im
        return _tmp118
    return NotImplemented

def complex_pow(self, other, m=None, new=object.__new__, cls=Complex):
    t = type(other)
    #IF_CHECK_INT(T=t)
    if t is int or t is long:
        if not other:
            return 1
        if other==1:
            return self
        if other==2:
            return self*self
        if other < 0:
            base, exponent = 1/self, -other
        else:
            base, exponent = self, other
        #POW_COMPLEX_INT(LHS=base; RHS=exponent; MOD=%)
        a, b = base.real, base.imag
        n = exponent
        if not a:
            case = n % 4
            if not case:
                return b**n
            elif case == 1:
                #RETURN_COMPLEX(REAL=0; IMAG=b**n)
                _tmp121 = new(cls)
                _tmp121.real = 0
                _tmp121.imag = b**n
                return _tmp121
            elif case == 2:
                return -(b**n)
            else:
                #RETURN_COMPLEX(REAL=0; IMAG=-b**n)
                _tmp122 = new(cls)
                _tmp122.real = 0
                _tmp122.imag = -b**n
                return _tmp122
        ta, tb = type(a), type(b)
        m = 1
        if ta is FractionTuple:
            if tb is FractionTuple:
                m = (a[1] * b[1]) ** n
                a, b = a[0]*b[1], a[1]*b[0]
            #ELIF_CHECK_INT(T=tb)
            elif tb is int or tb is long:
                m = a[1] ** n
                a, b = a[0], a[1]*b
        elif tb is FractionTuple:
            #IF_CHECK_INT(T=ta)
            if ta is int or ta is long:
                m = b[1] ** n
                a, b = a*b[1], b[0]
        c, d = 1, 0
        while n:
            if n & 1:
                c, d = a*c-b*d, b*c+a*d
                n -= 1
            a, b = a*a-b*b, 2*a*b
            n //= 2
        if m==1:
            #RETURN_COMPLEX2(REAL=c; IMAG=d)
            _tmp125 = d
            if not _tmp125:
                return c
            #RETURN_COMPLEX(REAL=c; IMAG=_tmp125)
            _tmp126 = new(cls)
            _tmp126.real = c
            _tmp126.imag = _tmp125
            return _tmp126
        # c,d,m are integers
        #FRACTION_NORMALIZE(NUMER=c; DENOM=m; RNUMER=re_p; RDENOM=re_q; MOD=%)
        re_p = _x = c
        re_q = _y = m
        while _y:
            _x, _y = _y, _x % _y
        if _x != 1:
            re_p //= _x
            re_q //= _x
        if re_q==1:
            re = re_p
        else:
            re = FractionTuple((re_p, re_q))
        if not d:
            return re
        #FRACTION_NORMALIZE(NUMER=d; DENOM=m; RNUMER=im_p; RDENOM=im_q; MOD=%)
        im_p = _x = d
        im_q = _y = m
        while _y:
            _x, _y = _y, _x % _y
        if _x != 1:
            im_p //= _x
            im_q //= _x
        if im_q==1:
            im = im_p
        else:
            im = FractionTuple((im_p, im_q))
        #RETURN_COMPLEX(REAL=re; IMAG=im)
        _tmp129 = new(cls)
        _tmp129.real = re
        _tmp129.imag = im
        return _tmp129
    return NotImplemented
    
def fraction_lt(self, other, cls=FractionTuple):
    p, q = self
    t = type(other)
    #IF_CHECK_INT(T=t)
    if t is int or t is long:
        return (p < q*other)
    elif t is cls:
        r, s = other
        return p*s < q*r
    return NotImplemented
    
def fraction_le(self, other, cls=FractionTuple):
    p, q = self
    t = type(other)
    #IF_CHECK_INT(T=t)
    if t is int or t is long:
        return (p <= q*other)
    elif t is cls:
        r, s = other
        return p*s <= q*r
    return NotImplemented
    
def fraction_gt(self, other, cls=FractionTuple):
    p, q = self
    t = type(other)
    #IF_CHECK_INT(T=t)
    if t is int or t is long:
        return (p > q*other)
    elif t is cls:
        r, s = other
        return p*s > q*r
    return NotImplemented
    
def fraction_ge(self, other, cls=FractionTuple):
    p, q = self
    t = type(other)
    #IF_CHECK_INT(T=t)
    if t is int or t is long:
        return (p >= q*other)
    elif t is cls:
        r, s = other
        return p*s >= q*r
    return NotImplemented
    