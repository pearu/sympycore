
__all__ = ['APPLY']

from .base import Head, heads_precedence
from .functional import FunctionalHead

from ..core import init_module, Expr
init_module.import_heads()
init_module.import_lowlevel_operations()

class ApplyHead(FunctionalHead):
    """
    ApplyHead is a head for n-ary apply operation,
    data is a (1+n)-tuple of expression operands
    """
    op_mth = '__call__'
    parenthesis = '()'

    def is_data_ok(self, cls, data):
        if isinstance(data, tuple) and len(data)==2:
            func, args = data
            msg = func.head.is_data_ok(type(func), func.data)
            if msg:
                return '%s data=%r: %s' % (func.head, func.pair, msg)
            if type(args) is tuple:
                for i,a in enumerate(args):
                    if not isinstance(a, Expr):
                        return '%s data[1][%s] must be %s instance but got %s' % (self, i, type(a))
            else:
                return '%s data[1] must be tuple but got %s' % (self, type(args))
        else:
            return '%s data instance must be 2-tuple' % (self)

    def __repr__(self): return 'APPLY'

    def new(self, cls, (func, args), evaluate=True):
        if not isinstance(func, Expr):
            fcls = cls.get_function_algebra()
            func = fcls(CALLABLE, func)
        return cls(APPLY, (func, args))

    def term_coeff(self, cls, expr):
        return expr, 1

    def neg(self, cls, expr):
        return cls(TERM_COEFF, (expr, -1))

    def add(self, cls, lhs, rhs):
        h, d = rhs.pair
        if h is APPLY:
            if lhs.data==d:
                return cls(TERM_COEFF, (lhs, 2))
            return cls(TERM_COEFF_DICT, {lhs:1, rhs:1})
        elif h is NUMBER:
            if d==0:
                return lhs
            return cls(TERM_COEFF_DICT, {lhs:1, cls(NUMBER,1):d})
        elif h is TERM_COEFF:
            t,c = d
            if lhs==t:
                return term_coeff_new(cls, (t, c+1))
            return cls(TERM_COEFF_DICT, {t:c, lhs:1})
        elif h is TERM_COEFF_DICT:
            data = d.copy()
            dict_add_item(cls, data, lhs, 1)
            return term_coeff_dict_new(cls, data)
        elif h is SYMBOL or h is POW or h is BASE_EXP_DICT:
            return cls(TERM_COEFF_DICT, {lhs:1, rhs:1})
        raise NotImplementedError(`self, rhs.pair`)

    inplace_add = add

    def add_number(self, cls, lhs, rhs):
        return cls(TERM_COEFF_DICT, {lhs:1, cls(NUMBER,1):rhs}) if rhs else lhs

    def sub_number(self, cls, lhs, rhs):
        return cls(TERM_COEFF_DICT, {lhs:1, cls(NUMBER,1):-rhs}) if rhs else lhs

    def sub(self, cls, lhs, rhs):
        return lhs + (-rhs)
    
    def commutative_mul(self, cls, lhs, rhs):
        rhead, rdata = rhs.pair
        if rhead is NUMBER:
            return term_coeff_new(cls, (lhs, rdata))
        if rhead is SYMBOL or rhead is ADD or rhead is TERM_COEFF_DICT:
            return cls(BASE_EXP_DICT, {lhs:1, rhs:1})
        if rhead is APPLY:
            if lhs.data==rdata:
                return cls(POW, (lhs, 2))
            return cls(BASE_EXP_DICT, {lhs:1, rhs:1})
        if rhead is TERM_COEFF:
            term, coeff = rdata
            return (lhs * term) * coeff
        if rhead is POW:
            rbase, rexp = rdata
            if rbase==lhs:
                return pow_new(cls, (lhs, rexp+1))
            return cls(BASE_EXP_DICT, {lhs:1, rbase:rexp})
        if rhead is BASE_EXP_DICT:
            data = rdata.copy()
            dict_add_item(cls, data, lhs, 1)
            return base_exp_dict_new(cls, data)
        raise NotImplementedError(`self, cls, lhs.pair, rhs.pair`)

    def commutative_mul_number(self, cls, lhs, rhs):
        if rhs==0:
            return cls(NUMBER, 0)
        if rhs==1:
            return lhs
        return cls(TERM_COEFF, (lhs, rhs))

    def commutative_div(self, cls, lhs, rhs):
        rhead, rdata = rhs.pair
        if rhead is NUMBER:
            return self.commutative_div_number(cls, lhs, rdata)
        if rhead is APPLY:
            if lhs.data==rdata:
                return cls(NUMBER, 1)
            return cls(BASE_EXP_DICT, {lhs:1, rhs:-1})
        if rhead is SYMBOL or rhead is TERM_COEFF_DICT:
            return cls(BASE_EXP_DICT, {lhs:1, rhs:-1})
        if rhead is TERM_COEFF:
            term, coeff = rdata
            return (lhs / term) * number_div(1, coeff)
        if rhead is BASE_EXP_DICT:
            data = {lhs:1}
            base_exp_dict_sub_dict(cls, data, rdata)
            return base_exp_dict_new(cls, data)
        return ArithmeticHead.commutative_div(self, cls, lhs, rhs)

    def pow(self, cls, base, exp):
        return POW.new(cls, (base, exp))

    pow_number = pow

    def scan(self, proc, cls, data, target):
        f, args = data
        f.head.scan(proc, cls, f.data, target)
        for arg in args:
            arg.head.scan(proc, cls, arg.data, target)
        proc(cls, self, data, target)

    def walk(self, func, cls, data, target):
        f, args = data
        f1 = f.head.walk(func, cls, f.data, f)
        l = []
        flag = f is not f1
        for arg in args:
            h, d = arg.pair
            a = arg.head.walk(func, cls, arg.data, arg)
            if a is not arg:
                flag = True
            l.append(a)
        if flag:
            if f1.head is CALLABLE:
                r = cls(f1.data(*l))
            else:
                r = cls(APPLY, (f, tuple(l)))
            return func(cls, r.head, r.data, r)
        else:
            return func(cls, self, data, target)
        h, d = f.pair
        if h is CALLABLE:
            r = cls(d(*l))
            h, d = r.pair
            return func(cls, h, d)
        else:
            return func(cls, self, (f, tuple(l)))

    def expand(self, cls, expr):
        return expr

    def diff(self, cls, data, expr, symbol, order, cache={}):
        key = (expr, symbol, order)
        result = cache.get(key)
        if result is not None:
            return result
        key1 = (expr, symbol, 1)
        result = cache.get(key1)
        if result is None:
            func, args = data
            assert func.head is CALLABLE,`func`
            fcls = cls.get_function_algebra()
            if len(args)==1:
                arg = args[0]
                da = arg.head.diff(cls, arg.data, arg, symbol, 1, cache=cache)
                if symbol not in da.symbols_data:
                    df = func.head.fdiff(fcls, func.data, func, 0, order)
                    if df is not NotImplemented:
                        result = df(*args) * da**order
                        cache[key] = result
                        return result
                df = func.head.fdiff(fcls, func.data, func, 0, 1)
                result = df(*args) * da

            else:
                result = cls(NUMBER, 0)
                for i in range(len(args)):
                    arg = args[i]
                    da = arg.head.diff(cls, arg.data, arg, symbol, 1, cache=cache)
                    df = func.head.fdiff(fcls, func.data, func, i, 1)
                    result += df(*args) * da
            cache[key1] = result
        if order>1:
            result = result.head.diff(cls, result.data, result, symbol, order-1, cache=cache)
            cache[key] = result
        return result

    def apply(self, cls, data, func, args):
        return NotImplemented

APPLY = ApplyHead()
