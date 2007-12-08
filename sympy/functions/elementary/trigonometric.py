
from ...core import Basic, BasicType, classes, objects
from ...core.function import FunctionSignature
from ...core.utils import UniversalMethod
from ...arithmetic import Function, BasicArithmetic


__all__ = ['Cos', 'Sin', 'Tan', 'Cot']

def without(L, x):
    L = L[:]
    L.remove(x)
    return L

class Cos(Function):

    signature = FunctionSignature((BasicArithmetic,), (BasicArithmetic,))

    @classmethod
    def canonize(cls, (arg,), options):
        if arg.is_NaN: return arg
        if arg.is_Number:
            if arg.is_zero: return objects.one
            if arg.is_negative: return cls(-arg)
            return

    @classmethod
    def fdiff1(cls):
        return -Sin

class Sin(Function):
    """ sin(x)
    """
    signature = FunctionSignature((BasicArithmetic,), (BasicArithmetic,))

    @classmethod
    def canonize(cls, (arg,), options):
        if arg.is_NaN: return arg
        if arg.is_Number:
            if arg.is_zero: return arg
            if arg.is_negative: return -cls(-arg)
            return
        factors = list(arg.split(classes.Mul)[1])
        I = objects.I
        pi = objects.pi
        if I in factors:
            # Simplify sin(I*x)
            return I * classes.Sinh(classes.Mul(*without(factors, I)))
        if pi in factors:
            # Simplify Sin((p/q)*pi)
            c = classes.Mul(*without(factors, pi))
            if c.is_Rational:
                cases = {1:classes.Integer(0), 2:classes.Integer(1), 3:classes.Sqrt(3)/2,
                    4:classes.Sqrt(2)/2, 6:classes.Rational(1,2)}
                if c.q in cases:
                    return (-1)**((c.p//c.q)%2) * cases[c.q]
        if any(x.is_Rational and x.p < 0 for x in factors):
            return -Sin(-arg)
        return

    @classmethod
    def fdiff1(cls):
        return Cos

class Tan(Function):

    signature = FunctionSignature((BasicArithmetic,), (BasicArithmetic,))

    @classmethod
    def canonize(cls, (arg,), options):
        if arg.is_NaN: return arg
        if arg.is_Number:
            if arg.is_zero: return arg
            if arg.is_negative: return -cls(-arg)

    @classmethod
    def fdiff1(cls):
        return cls**2 + 1

class Cot(Function):

    signature = FunctionSignature((BasicArithmetic,), (BasicArithmetic,))

    @classmethod
    def canonize(cls, (arg,), options):
        if arg.is_NaN: return arg
        if arg.is_Number:
            pass

    @classmethod
    def fdiff1(cls):
        return -Sin**(-2)
