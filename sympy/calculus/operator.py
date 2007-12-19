
from ..core import classes, objects
from ..arithmetic import Operator, Function

__all__ = ['FD', 'D', 'FDerivative', 'Derivative',
           'AD', 'Integral','At']

class At(Function):
    """ At operator.

    At(f(x_), (x_, x)) -> f(x) when possible.
    At(f(x_, y_), (x_, x), (y_, y)) -> f(x, y) when possible.
    """
    @classmethod
    def canonize(cls, args):
        expr = args[0]
        unreplaced = []
        flag = True
        for x,y in args[1:]:
            obj = expr.try_replace(x, y)
            if obj is None:
                unreplaced.append(classes.Tuple(x,y))
                continue
            expr = obj
            flag = False
        if not unreplaced:
            return expr
        return At(expr, *unreplaced, **dict(is_canonical=True))


def derivative_compose_arg_tuples(r1, r2=None):
    if r2 is None:
        if not r1:
            return (objects.one,)
        return r1
    if not r2:
        r2 = (objects.one,)
    return (r1[0] + r2[0],)    

class FD(Operator):
    """ Derivative function operator.
    
    FD(index) - 1st order derivative with respect to index-th argument
    FD((index, n)) - n-th order derivative with respect to index-th argument
    FD((index1,n1), (index2,n2), ..) - (n1+n2+...)-th order partial
      derivative with respect to index-th argument n1 times, ....
    """
    
    compose_arg_tuples = staticmethod(derivative_compose_arg_tuples)

    def __call__(self, expr):
        if isinstance(expr, classes.FD):
            return FD(*(self[:] + expr[:]))
        f = expr
        unevaluated = []
        for index, n in self:
            if isinstance(index, classes.Integer) and isinstance(n, classes.Integer):
                assert n>=0,`index,n`
                for i in range(n):
                    f = f.fdiff(index)
            else:
                unevaluated.append(classes.Tuple(index, n))
        if not unevaluated:
            return f
        return FDerivative(f, *unevaluated, **dict(is_canonical=True))

class D(Operator):
    """ Derivative operator.
    
    D(x) - 1st derivative with respect to x
    D((x, n)) - n-th derivative with respect to x
    D((x,n1), (y,n2), ..)
    """
    compose_arg_tuples = staticmethod(derivative_compose_arg_tuples)

    def __call__(self, expr):
        if isinstance(expr, classes.D):
            return D(*(self[:] + expr[:]))
        f = expr
        unevaluated = []
        for t in self:
            v, n = t
            if isinstance(n, classes.Integer):
                assert n>=0,`v,n`
                i = n
                while i:
                    obj = f.try_derivative(v)
                    if obj is None:
                        unevaluated.append(classes.Tuple(v, i))
                        break
                    i -= 1
                    f = obj
            else:
                unevaluated.append(t)
        if not unevaluated:
            return f
        return Derivative(f, *unevaluated, **dict(is_canonical=True))

class AD(Operator):
    """ Antiderivative operator.
    
    AD(x) - 1st antiderivative with respect to x.
    AD((x,a,b))
    """
    @staticmethod
    def compose_arg_tuples(r1, r2=None):
        if r2 is None:
            if not r1:
                return (objects.one,)
            return r1
        if len(r1)==1:
            if not r2:
                return (r1[0]+1,)
            assert len(r2)==1,`r1,r2` # XXX: need meaningful error message
            return (r1[0]+r2[0],)
        raise ValueError(`r1,r2`) # XXX: need meaningful error message
    
    def __call__(self, expr):
        if isinstance(expr, classes.AD):
            return AD(*(self[:] + expr[:]))
        f = expr
        unevaluated = []
        for t in self:
            v = t[0]
            r = t[1:]
            if len(r)==1:
                n = r[0]
                if isinstance(n, classes.Integer):
                    assert n>=0,`n`
                    i = n
                    while i:
                        obj = f.try_antiderivative(v)
                        if obj is None:
                            unevaluated.append(classes.Tuple(v,i))
                            break
                        i -= 1
                        f = obj
            elif len(r)==2:
                obj = f.try_antiderivative(v)
                if obj is None:
                    unevaluated.append(t)
                    continue
                f = obj.replace(v, r[1]) - obj.replace(v, r[0])
            else:
                unevaluated.append(t)
        if not unevaluated:
            return f
        return Integral(f, *unevaluated, **dict(is_canonical=True))


class Derivative(Function):
    """ Derivative of an expression.
    """

    @classmethod
    def canonize(cls, args, options):
        expr = args[0]
        op = D(*args[1:])
        return op(expr)

    def try_replace(self, old, new):
        opts = None
        if isinstance(old, classes.Symbol):
            i = 0
            flag = False
            for r in self[1:]:
                i += 1
                if old==r[0]:
                    if not isinstance(new, classes.Symbol):
                        return
                    l = self[1:i]+(classes.Tuple(new, r[1]),)+self[i+1:]
                    e = self[0].replace(old, new)
                    return Derivative(e, *l, **dict(is_canonical=True))
                if new==r[0]:
                    flag = True
            if flag:
                return
            if isinstance(new, classes.Symbol):
                opts = dict(is_canonical=True)
        e = self[0].replace(old, new)
        l = [r.replace(old, new) for r in self[1:]]
        if e==self[0] and l==self[1:]:
            return
        return Derivative(e, *l, **(opts or {}))

    def try_derivative(self, s):
        return Derivative(*(self[:] + (s,)))

    def try_antiderivative(self, s):
        i = 0
        for t in self[1:]:
            i += 1
            if len(t)==2 and t[0]==s:
                return Derivative(*(self[:] + ((s,-1),)))
        return

class FDerivative(Function):
    """ Derivative function.
    """
    @classmethod
    def canonize(cls, args, options):
        expr = args[0]
        op = FD(*args[1:])
        return op(expr)

    def __call__(self, *args):
        dargs = [classes.Dummy('x%s' % i) for i in range(len(args))]
        expr = self[0](*dargs)
        rest = [classes.Tuple(dargs[r[0]-1], r[1]) for r in self[1:]]
        return At(Derivative(expr, *rest, **dict(is_canonical=True)),
                  *[classes.Tuple(d, a) for (d, a) in zip(dargs, args)])

class Integral(Function):

    @classmethod
    def canonize(cls, args, options):
        expr = args[0]
        op = AD(*args[1:])
        return op(expr)

    def try_replace(self, old, new):
        #XXX
        return

    def try_derivative(self, s):
        i = 0
        for t in self[1:]:
            i += 1
            if len(t)==2 and t[0]==s:
                return Integral(*(self[:] + ((s,-1),)))
        return
    
    def try_antiderivative(self, s):
        return Integral(*(self[:] + (s,)))
