

from ...core import Basic, BasicType, classes, objects
from ...core.function import FunctionSignature
from ...core.utils import UniversalMethod
from ...arithmetic import Function, BasicArithmetic

__all__ = ['Min', 'Max', 'Sqrt']

class Max(Function):
    """ Maximum of arguments
    """
    signature = FunctionSignature([(Basic,)], (BasicArithmetic,))

    @classmethod
    def canonize(cls, args):
        new_args = set([])
        flag = False
        for a in args:
            if isinstance(a, classes.BasicSet):
                o = a.try_supremum()
                if o is not None:
                    a = o
            if isinstance(a, classes.Max):
                new_args.union(a.args)
                flag = True
            elif isinstance(a, classes.Infinity):
                return a
            elif a==-objects.oo:
                flag = True
            else:
                n = len(new_args)
                new_args.add(a)
                if n==len(new_args):
                    flag = True
        numbers = [a for a in new_args if isinstance(a, classes.Number)]
        if len(numbers)>1:
            flag = True
            new_args = set([a for a in new_args if not isinstance(a, classes.Number)]).union([max(*numbers)])
        if flag:
            return cls(*new_args)
        if len(new_args)==0:
            return -objects.oo
        if len(new_args)==1:
            arg = list(new_args)[0]
            if not isinstance(arg, classes.BasicSet):
                return arg


class Min(Function):
    """ Minimum of arguments
    """
    signature = FunctionSignature([(Basic,)], (BasicArithmetic,))

    @classmethod
    def canonize(cls, args):
        new_args = set([])
        flag = False
        for a in args:
            if isinstance(a, classes.BasicSet):
                o = a.try_infimum()
                if o is not None:
                    a = o
            if isinstance(a, classes.Max):
                new_args.union(a.args)
                flag = True
            elif isinstance(a, classes.Infinity):
                flag = True
            elif a==-objects.oo:
                return a
            else:
                n = len(new_args)
                new_args.add(a)
                if n==len(new_args):
                    flag = True
        numbers = [a for a in new_args if isinstance(a, classes.Number)]
        if len(numbers)>1:
            flag = True
            new_args = set([a for a in new_args if not isinstance(a, classes.Number)]).union([min(*numbers)])
        if flag:
            return cls(*new_args)
        if len(new_args)==0:
            return objects.oo
        if len(new_args)==1:
            arg = list(new_args)[0]
            if not isinstance(arg, classes.BasicSet):
                return arg
