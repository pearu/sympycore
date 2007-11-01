
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
        if arg.is_Mul:
            # handle Exp(coeff*pi*I)
            pass

    @UniversalMethod
    def fdiff(obj, index=1):
        if isinstance(obj, BasicType):
            if index!=1:
                raise ValueError('%s takes 1 argument, reguested %sth' % (cls.__name__, index))
            return obj
        return obj._fdiff(index)


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
            return
        if arg.is_Exp1:
            return Basic.one
        if arg.is_ImaginaryUnit:
            return Basic.I * Basic.pi / 2
        if arg in [-Basic.oo,-Basic.E,-Basic.pi,-Basic.I]:
            # XXX: need more generic test
            return Basic.pi * Basic.I + cls(-arg)


    @UniversalMethod
    def fdiff(obj, index=1):
        if isinstance(obj, BasicType):
            if index!=1:
                raise ValueError('%s takes 1 argument, reguested %sth' % (cls.__name__, index))
            x = Basic.Dummy('x')
            return Basic.Lambda(x,1/x)
        return obj._fdiff(index)
