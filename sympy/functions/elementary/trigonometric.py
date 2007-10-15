from sympy.core import Basic, Mul, Integer, Rational, sqrt, pi, I
from sympy.core.function import SingleValuedFunction, FunctionSignature

def without(L, x):
    L = L[:]
    L.remove(x)
    return L


class sin(SingleValuedFunction):

    signature = FunctionSignature((Basic,), (Basic,))

    @classmethod
    def canonize(cls, (arg,), **options):
        if arg.is_NaN: return arg
        if arg.is_Number:
            if arg.is_zero: return arg
            if arg.is_negative: return -cls(-arg)
            return
        factors = arg.split('*')
        if I in factors:
            # Simplify sin(I*x)
            return I * Basic.sinh(Mul(*without(factors, I)))
        if pi in factors:
            # Simplify sin((p/q)*pi)
            c = Mul(*without(factors, pi))
            if c.is_Rational:
                cases = {1:Integer(0), 2:Integer(1), 3:sqrt(3)/2,
                    4:sqrt(2)/2, 6:Rational(1,2)}
                if c.q in cases:
                    return (-1)**((c.p//c.q)%2) * cases[c.q]
        if any(x.is_Rational and x.p < 0 for x in factors):
            return -sin(-arg)
        return

    def fdiff(cls, index=1):
        if index!=1:
            raise ValueError('%s takes 1 argument, reguested %sth' % (cls.__name__, index))
        return cos

class cos(SingleValuedFunction):

    signature = FunctionSignature((Basic,), (Basic,))

    @classmethod
    def canonize(cls, (arg,), **options):
        if arg.is_NaN: return arg
        if arg.is_Number:
            if arg.is_zero: return Basic.one
            if arg.is_negative: return cls(-arg)
            return

    def fdiff(cls, index=1):
        if index!=1:
            raise ValueError('%s takes 1 argument, reguested %sth' % (cls.__name__, index))
        return -sin

class exp(SingleValuedFunction):

    signature = FunctionSignature((Basic,), (Basic,))

    @classmethod
    def canonize(cls, (arg,), **options):
        if arg.is_NaN: return arg
        if arg.is_Number:
            if arg.is_zero: return Basic.one
            return

    def fdiff(cls, index=1):
        if index!=1:
            raise ValueError('%s takes 1 argument, reguested %sth' % (cls.__name__, index))
        return cls

class log(SingleValuedFunction):

    signature = FunctionSignature((Basic,), (Basic,))

    @classmethod
    def canonize(cls, (arg,), **options):
        if arg.is_NaN: return arg
        if arg.is_Number:
            if arg.is_one: return Basic.zero
            return

    def fdiff(cls, index=1):
        if index!=1:
            raise ValueError('%s takes 1 argument, reguested %sth' % (cls.__name__, index))
        x = Basic.Symbol('x',dummy=True)
        return Basic.Lambda(x,1/x)

class tan(SingleValuedFunction):

    signature = FunctionSignature((Basic,), (Basic,))

    @classmethod
    def canonize(cls, (arg,), **options):
        if arg.is_NaN: return arg
        if arg.is_Number:
            if arg.is_zero: return arg
            if arg.is_negative: return -cls(-arg)


    def fdiff(cls, index=1):
        if index!=1:
            raise ValueError('%s takes 1 argument, reguested %sth' % (cls.__name__, index))
        return cls**2 + 1

class cot(SingleValuedFunction):

    signature = FunctionSignature((Basic,), (Basic,))

    @classmethod
    def canonize(cls, (arg,), **options):
        if arg.is_NaN: return arg
        if arg.is_Number:
            pass

    def fdiff(cls, index=1):
        if index!=1:
            raise ValueError('%s takes 1 argument, reguested %sth' % (cls.__name__, index))
        return -1/sin**2
