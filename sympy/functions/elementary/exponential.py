
from ...core import Basic, BasicType
from ...core.function import FunctionSignature
from ...core.utils import UniversalMethod
from ...arithmetic import Function

class Exp(Function):

    signature = FunctionSignature((Basic,), (Basic,))

    @classmethod
    def canonize(cls, (arg,), **options):
        if arg.is_NaN or arg.is_Infinity:
            return arg
        if arg.is_Number:
            if arg.is_zero: return Basic.one
            if arg.is_one: return Basic.E
            return
        if arg==-Basic.oo:
            return Basic.zero
        if arg.is_Log:
            return arg[0]
        t, c = arg.as_term_coeff()
        if t.is_Log:
            return t.args[0] ** c

        excluded = []
        included = []
        for a in arg.iterAdd():
            it = a.iterMul()
            cs = []
            b = None
            for f in it:
                if f.is_Log:
                    excluded.append(f.args[0] ** Basic.Mul(*(cs+list(it))))
                    break
                cs.append(f)
            else:
                included.append(a)
        if excluded:
            if included:
                return Basic.Mul(*(excluded+[cls(Basic.Add(*included))]))
            else:
                return Basic.Mul(*excluded)

    @UniversalMethod
    def fdiff(obj, index=1):
        if isinstance(obj, BasicType):
            if index!=1:
                raise ValueError('%s takes 1 argument, reguested %sth' % (cls.__name__, index))
            return obj
        return obj._fdiff(index)

    def try_power(self, other):
        return Exp(self.args[0] * other)

class Log(Function):

    signature = FunctionSignature((Basic,), (Basic,))

    @classmethod
    def canonize(cls, (arg,), **options):
        if arg.is_NaN or arg.is_Infinity: return arg
        if arg.is_Number:
            if arg.is_one: return Basic.zero
            if arg.is_negative:
                return Basic.pi * Basic.I + cls(-arg)
            if arg.is_zero:
                return -Basic.oo
            if arg.is_Integer:
                factors = arg.as_factors()
                if len(factors)==1:
                    b, e = factors[0]
                    if e!=1:
                        return e * cls(b)
            if arg.is_Fraction:
                return cls(arg.p) - cls(arg.q)
            return
        if arg.is_Exp1:
            return Basic.one
        if arg.is_ImaginaryUnit:
            return Basic.I * Basic.pi / 2
        if arg in [-Basic.oo,-Basic.E,-Basic.pi,-Basic.I]:
            # XXX: need more generic test
            return Basic.pi * Basic.I + cls(-arg)
        #base, exponent = arg.as_base_exponent()
        #if exponent.is_Number:
        #    return exponent * cls(Basic.Abs(base))

    @UniversalMethod
    def fdiff(obj, index=1):
        if isinstance(obj, BasicType):
            if index!=1:
                raise ValueError('%s takes 1 argument, reguested %sth' % (cls.__name__, index))
            x = Basic.Dummy('x')
            return Basic.Lambda(x,1/x)
        return obj._fdiff(index)

    def matches(pattern, expr, repl_dict={}):
        if expr.is_Log:
            return pattern.args[0].matches(expr.args[0], repl_dict)
        if expr.is_Add and len(expr)==1:
            # Log(p).matches(4*Log(x)) -> p.matches(x**4)
            term, coeff = expr.items()[0]
            if term.is_Log and coeff.is_Integer:
                return pattern.args[0].matches(term.args[0]**coeff, repl_dict)
        if expr.is_Number:
            return pattern.args[0].matches(Exp(expr), repl_dict)
        if pattern.args[0].is_Wild:
            return pattern.args[0].matches(Exp(expr), repl_dict)
