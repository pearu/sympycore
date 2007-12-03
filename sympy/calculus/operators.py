"""
Calculus operators
"""

from sympy.core import sympify, classes, objects
from sympy.arithmetic import BasicArithmetic


class CalculusOperator(BasicArithmetic):
    """
    CalculusOperator(expr, x, y, ...):
    Apply operator in turn with respect to x, y, ...

    CalculusOperator(expr, (x, a, ...), (y, b, ...), ...):
    Apply operator with specified options (e.g. evaluation points)
    for each parameter.

    CalculusOperator(..., evaluate=False)
    Do not attempt to evaluate in closed form.
    """

    def __new__(cls, expr, *params, **options):
        expr = sympify(expr)
        assert params
        params = list(params)
        for i, p in enumerate(params):
            if isinstance(p, tuple):
                sym = p[0]
                opts = tuple(map(sympify, p[1:]))
            else:
                sym = sympify(p)
                opts = ()
            assert sym.is_Symbol, 'parameter must be a symbol'
            params[i] = (sym,) + opts
        if options.get('evaluate', True):
            res = expr
            for p in params:
                res = cls.try_eval(res, p[0], *p[1:])
                if res is None:
                    break
            if res is not None:
                return res
        self = BasicArithmetic.__new__(cls)
        self.expr = expr
        self.params = params
        return self

    @classmethod
    def try_eval(cls, expr, sym, *points):
        return None

    def tostr(self, *args):
        params = []
        for p in self.params:
            if len(p) > 1:
                params.append(str(p))
            else:
                params.append(str(p[0]))
        params = ", ".join(params)
        return "%s(%s, %s)" % (self.__class__.__name__, self.expr, params)


    def replace(self, old, new):
        # Should handle index variables properly, etc
        raise NotImplementedError


class Limit(CalculusOperator):
    pass


class Derivative(CalculusOperator):
    """
    Derivative(expr, x, y, ...) represents the derivative of expr with
    respect to x, y, ... in order.

    Repeated derivatives can be specified as
    Derivative(expr, (x, 2), (y, 3), ...)
    """

    @classmethod
    def try_eval(cls, expr, sym, *opts):
        if opts:
            order = opts[0]
        else:
            order = 1
        return expr.diff(sym, order)


class Integral(CalculusOperator):
    """
    Integral(expr, x, y, ...) represents the indefinite integral of
    expr with respect to x, y, ... in order.

    Definite integration on intervals [a, b], [c, d], etc is specified
    as Integral(expr, (x, a, b), (y, c, d), ...)
    """

    @classmethod
    def try_eval(cls, expr, sym, *opts):
        try:
            expr = integrate_basic(expr, sym)
        except ValueError:
            return None
        if opts:
            a, b = opts
            return expr.replace(sym, b) - expr.replace(sym, a)
        return expr


class Sum(CalculusOperator):
    pass


class Product(CalculusOperator):
    pass



# Very basic implementation just to handle simple polynomials
def integrate_basic(a, x):
    if not a.has(x):
        return a*x
    if a is x:
        return (x**2)/2
    a = a.expand()
    if a.is_Add:
        return classes.Add(*[integrate_basic(t, x) for t in a])
    if a.is_Mul:
        c = classes.Integer(1)
        ppart = None
        for b in a:
            if not b.has(x):
                c *= b
            elif ppart is not None:
                raise ValueError
            else:
                ppart = integrate_basic(b, x)
        return c * ppart
    if a.is_Pow:
        b, e = a
        if e.has(x):
            raise ValueError
        if b is x:
            if e == -1:
                return classes.Log(b)
            else:
                return b**(e+1) / (e+1)
        elif b.has(x):
            raise ValueError
    raise ValueError
