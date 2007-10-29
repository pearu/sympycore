
from ...core import Basic, BasicType
from ...core.function import FunctionSignature
from ...core.utils import UniversalMethod
from ..function import Function


__all__ = ['Sin', 'Cos', 'Exp', 'Log', 'Tan', 'Cot',
           'Sqrt',
           'Min', 'Max',
           ]

def without(L, x):
    L = L[:]
    L.remove(x)
    return L

class Max(Function):
    """ Maximum of arguments
    """
    signature = FunctionSignature([(Basic,)], (Basic,))

    @classmethod
    def canonize(cls, args):
        new_args = set([])
        flag = False
        for a in args:
            if a.is_BasicSet:
                o = a.try_supremum()
                if o is not None:
                    a = o
            if a.is_Max:
                new_args.union(a.args)
                flag = True
            elif a.is_Infinity:
                return a
            elif a==-Basic.oo:
                flag = True
            else:
                n = len(new_args)
                new_args.add(a)
                if n==len(new_args):
                    flag = True
        numbers = [a for a in new_args if a.is_Number]
        if len(numbers)>1:
            flag = True
            new_args = set([a for a in new_args if not a.is_Number]).union([max(*numbers)])
        if flag:
            return cls(*new_args)
        if len(new_args)==0:
            return -Basic.oo
        if len(new_args)==1:
            arg = list(new_args)[0]
            if not arg.is_BasicSet:
                return arg


class Min(Function):
    """ Minimum of arguments
    """
    signature = FunctionSignature([(Basic,)], (Basic,))

    @classmethod
    def canonize(cls, args):
        new_args = set([])
        flag = False
        for a in args:
            if a.is_BasicSet:
                o = a.try_infimum()
                if o is not None:
                    a = o
            if a.is_Max:
                new_args.union(a.args)
                flag = True
            elif a.is_Infinity:
                flag = True
            elif a==-Basic.oo:
                return a
            else:
                n = len(new_args)
                new_args.add(a)
                if n==len(new_args):
                    flag = True
        numbers = [a for a in new_args if a.is_Number]
        if len(numbers)>1:
            flag = True
            new_args = set([a for a in new_args if not a.is_Number]).union([min(*numbers)])
        if flag:
            return cls(*new_args)
        if len(new_args)==0:
            return Basic.oo
        if len(new_args)==1:
            arg = list(new_args)[0]
            if not arg.is_BasicSet:
                return arg
            
class Sqrt(Function):
    signature = FunctionSignature((Basic,), (Basic,))
    @classmethod
    def canonize(cls, (arg,), **options):
        return arg ** Basic.Rational(1,2)

class Cos(Function):

    signature = FunctionSignature((Basic,), (Basic,))

    @classmethod
    def canonize(cls, (arg,), **options):
        if arg.is_NaN: return arg
        if arg.is_Number:
            if arg.is_zero: return Basic.one
            if arg.is_negative: return cls(-arg)
            return

    @UniversalMethod
    def fdiff(obj, index=1):
        if isinstance(obj, BasicType):
            if index!=1:
                raise ValueError('%s takes 1 argument, reguested %sth' % (cls.__name__, index))
            return -Sin
        return obj._fdiff(index)


class Sin(Function):
    """ sin(x)
    """
    signature = FunctionSignature((Basic,), (Basic,))

    @classmethod
    def canonize(cls, (arg,), **options):
        if arg.is_NaN: return arg
        if arg.is_Number:
            if arg.is_zero: return arg
            if arg.is_negative: return -cls(-arg)
            return
        factors = arg.split('*')
        I = Basic.I
        pi = Basic.pi
        if I in factors:
            # Simplify sin(I*x)
            return I * Basic.Sinh(Basic.Mul(*without(factors, I)))
        if pi in factors:
            # Simplify Sin((p/q)*pi)
            c = Basic.Mul(*without(factors, pi))
            if c.is_Rational:
                cases = {1:Basic.Integer(0), 2:Basic.Integer(1), 3:Sqrt(3)/2,
                    4:Sqrt(2)/2, 6:Basic.Rational(1,2)}
                if c.q in cases:
                    return (-1)**((c.p//c.q)%2) * cases[c.q]
        if any(x.is_Rational and x.p < 0 for x in factors):
            return -Sin(-arg)
        return

    @UniversalMethod
    def fdiff(obj, index=1):
        if isinstance(obj, BasicType):
            if index!=1:
                raise ValueError('%s takes 1 argument, reguested %sth' % (obj.__name__, index))
            return Cos
        return obj._fdiff(index)


class Exp(Function):

    signature = FunctionSignature((Basic,), (Basic,))

    @classmethod
    def canonize(cls, (arg,), **options):
        if arg.is_NaN: return arg
        if arg.is_Number:
            if arg.is_zero: return Basic.one
            return

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
        if arg.is_NaN: return arg
        if arg.is_Number:
            if arg.is_one: return Basic.zero
            return

    @UniversalMethod
    def fdiff(obj, index=1):
        if isinstance(obj, BasicType):
            if index!=1:
                raise ValueError('%s takes 1 argument, reguested %sth' % (cls.__name__, index))
            x = Basic.Dummy('x')
            return Basic.Lambda(x,1/x)
        return obj._fdiff(index)

class Tan(Function):

    signature = FunctionSignature((Basic,), (Basic,))

    @classmethod
    def canonize(cls, (arg,), **options):
        if arg.is_NaN: return arg
        if arg.is_Number:
            if arg.is_zero: return arg
            if arg.is_negative: return -cls(-arg)

    @UniversalMethod
    def fdiff(obj, index=1):
        if isinstance(obj, BasicType):
            if index!=1:
                raise ValueError('%s takes 1 argument, reguested %sth' % (cls.__name__, index))
            return obj**2 + 1
        return obj._fdiff(index)

class Cot(Function):

    signature = FunctionSignature((Basic,), (Basic,))

    @classmethod
    def canonize(cls, (arg,), **options):
        if arg.is_NaN: return arg
        if arg.is_Number:
            pass

    @UniversalMethod
    def fdiff(obj, index=1):
        if isinstance(obj, BasicType):
            if index!=1:
                raise ValueError('%s takes 1 argument, reguested %sth' % (cls.__name__, index))
            return -1/Sin**2
        return obj._fdiff(index)
