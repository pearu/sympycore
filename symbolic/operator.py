"""
Author: Pearu Peterson <pearu.peterson@gmail.com>
Created: January 2007
"""

__all__ = ['Differential','Integral', 'SymbolicFunction']

from base import Symbolic, FunctionalMethods, ArithmeticMethods, BooleanMethods
from singleton import Singleton

class SymbolicOperator(FunctionalMethods, Symbolic):
    """ Represents an operator with label and parameters.
    """

    ###########################################################################
    #
    # Constructor methods
    #

    def init(self, label, params):
        self.label = label
        self.params = tuple(params)
        return

    def astuple(self):
        return (self.__class__.__name__, self.label) + self.params

    ############################################################################
    #
    # Informational methods
    #

    def get_precedence(self): return 71

    def calc_symbols(self):
        r = set()
        for s in self.params:
            r.update(s.symbols())
        if isinstance(self.label, Symbolic):
            r.update(self.label.symbols())
        return r

    def calc_free_symbols(self):
        r = set()
        for s in self.params:
            r.update(s.free_symbols())
        return r

    ###########################################################################
    #
    # Transformation methods
    #

    def tostr(self, level=0):
        precedence = self.get_precedence()
        s = '%s(%s)' % (self.label, ', '.join([p.tostr() for p in self.params]))
        if precedence <= level:
            return '(%s)' % (s)
        return s

    def calc_expanded(self):
        return self.__class__(self.label, [p.expand() for p in self.params])

    ###########################################################################
    #
    # Comparison methods
    #

    def compare(self, other):
        if self is other: return 0
        c = self.compare_classes(other)
        if c: return c
        c = cmp(len(self.params), len(other.params))
        if c: return c
        c = cmp(self.params, other.params)
        if c: return c
        if isinstance(self.label, Symbolic):
            if isinstance(other.label, Symbolic):
                c = self.label.compare(other.label)
            else:
                c = 1
        elif isinstance(other.label, Symbolic):
            c = -1
        return c

#
# End of SymbolicOperator class
#
################################################################################

class SymbolicFunctionGenerator(Singleton):

    def tostr(self, level=0):
        return 'D'

    def __getitem__(self, indices):
        if not isinstance(indices, tuple):
            try:
                indices = tuple(indices)
            except TypeError:
                indices = (indices,)
        return lambda f, indices = indices: SymbolicFunction(f, *indices)

#
# End of SymbolicFunctionGenerator class
#
################################################################################


class SymbolicFunction(SymbolicOperator):
    """ Represents a function and its derivatives with respect to
    i-ths arguments defined by indices. Argument indices start from 1.
    Negative indices indicate function primitives with respect to
    the corresponding positive argument index.
    """
    def __new__(cls, f, *indices):
        f = Symbolic(f)
        #assert isinstance(f, Symbolic.Symbol),`type(f)`
        assert 0 not in indices,`indices`
        indices = map(Symbolic.Integer, indices)
        indices.sort()
        #if isinstance(f, Symbolic.ElementaryFunction):
        #    pass
        obj = Symbolic.__new__(cls, f, indices)
        return obj

    def tostr(self, level=0):
        precedence = self.get_precedence()
        if self.params:
            s = 'D[%s](%s)' % (', '.join([p.tostr() for p in self.params]), self.label.tostr())
        else:
            #precedence = self.label.get_precedence()
            s = self.label.tostr(precedence)
        if precedence <= level:
            return '(%s)' % (s)        
        return s

    def calc_expanded(self):
        return self

    def __call__(self, *args):
        if self.params and len(args)<max(self.params):
            raise TypeError,'symbolic function %r should have at least %s arguments'\
                  ' according to derivative indices (%s given)'\
                  % (self.label.tostr(), int(max(self.params)), len(args))
        return Symbolic.Apply(self, *args)

    def derivative(self, index=1):
        if -index in self.params:
            i = list(self.params).index(-index)
            indices = self.params[:i] + self.params[i+1:]
            return SymbolicFunction(self.label, *indices)
        return SymbolicFunction(self.label, *(self.params + (index,)))

    def primitive(self, index=1):
        if index in self.params:
            i = list(self.params).index(index)
            indices = self.params[:i] + self.params[i+1:]
            return SymbolicFunction(self.label, *indices)
        return SymbolicFunction(self.label, *(self.params + (-index,)))

class Integral(SymbolicOperator):

    def __new__(cls, x, *bounds):
        x = Symbolic(x)
        assert isinstance(x, Symbolic.SymbolBase),`type(x),x`
        if bounds:
            assert len(bounds)==2,`bounds`
            a, b = map(Symbolic,bounds)
            obj = Symbolic.__new__(DefinedIntegral, 'Int', [x, a, b])
        else:
            obj = Symbolic.__new__(IndefinedIntegral, 'Int', [x])
        return obj

    def calc_substitute(self, subst, replacement):
        flag, params = self._apply_mth('substitute', self.params, (subst, replacement))
        if flag:
            return self.__class__(*params)
        return self

    def __call__(self, integrand):
        return Symbolic.Apply(self, Symbolic(integrand))


class DefinedIntegral(Integral):

    def calc_free_symbols(self):
        r = set()
        for s in self.params[1:]:
            r.update(s.free_symbols())
        return r

    def __call__(self, expr):
        expr = Symbolic(expr)
        v,lb,ub = self.params
        return expr.integrate(Symbolic.Range(v, lb, ub))
        if v not in expr.free_symbols():
            # I(x,lb,ub)(a) -> (ub - lb) * a
            return (ub - lb) * expr
        if isinstance(expr, Symbolic.Symbol):
            # I(x,lb,ub)(x) -> 1/2 * (ub**2 - lb**2)
            assert v.is_equal(expr)
            return Symbolic.Half() * (ub ** 2 - lb**2)
        if isinstance(expr, Symbolic.Add):
            # I(x,lb,ub)(f(x)+g(x)) -> I(x,lb,ub)(f(x)) + I(x,lb,ub)(g(x))
            return Symbolic.Add(*map(self, expr.astuple()[1:]))
        if isinstance(expr, Symbolic.Mul):
            # I(x,lb,ub)(a*f(x)) -> a*I(x,lb,ub)(f(x))
            if isinstance(expr.coeff, Symbolic.One):
                coeffs = []
            else:
                coeffs = [expr.coeff]
            expr1 = []
            for t in expr.seq:
                l = t.free_symbols()
                if v not in t.free_symbols():
                    coeffs.append(t)
                else:
                    expr1.append(t)
            if coeffs:
                return Symbolic.Mul(*coeffs) * self(Symbolic.Mul(*expr1))
        if isinstance(expr, Symbolic.Power):
            # I(x,lb,ub)(x**n) -> (ub**(n+1) - lb**(n+1))/(n+1)
            if v not in expr.exponent.free_symbols() and expr.base.is_equal(v):
                n1 = expr.exponent + Symbolic.One()
                return (ub**n1 - lb**n1)/n1
        if isinstance(expr, Symbolic.Apply):
            # I(x,lb,ub)(D(x)(f(x))) -> f(ub) - f(lb)
            if isinstance(expr.coeff, Differential):
                assert len(expr.seq[0])==1,`expr.seq`
                if expr.params[0].is_equal(v):
                    return expr.seq[0].substitute(v,ub) - expr.seq[0].substitute(v,lb)
        return Symbolic.Apply(self, expr)        


class IndefinedIntegral(Integral):

    def calc_free_symbols(self): return set()

    def calc_expanded(self):
        return self

    def __call__(self, expr):
        expr = Symbolic(expr).expand()
        v = self.params[0]
        return expr.integrate(v)
        if v not in expr.free_symbols():
            # I(x)(a) -> a * x
            return v * expr # +IC(self.params[0])
        if isinstance(expr, Symbolic.Symbol):
            # I(x)(x) -> 1/2 * x ** 2
            assert v.is_equal(expr)
            return Symbolic.Half() * v ** 2
        if isinstance(expr, Symbolic.Add):
            # I(x)(f(x)+g(x)) -> I(x)(f(x)) + I(x)(g(x))
            return Symbolic.Add(*map(self, expr.astuple()[1:]))
        if isinstance(expr, Symbolic.Mul):
            # I(x)(a*f(x)) -> a*I(x)(f(x))
            if isinstance(expr.coeff, Symbolic.One):
                coeffs = []
            else:
                coeffs = [expr.coeff]
            expr1 = []
            for t in expr.seq:
                l = t.free_symbols()
                if v not in t.free_symbols():
                    coeffs.append(t)
                else:
                    expr1.append(t)
            if coeffs:
                return Symbolic.Mul(*coeffs) * self(Symbolic.Mul(*expr1))
        if isinstance(expr, Symbolic.Power):
            # I(x)(x**n) -> x**(n+1)/(n+1)
            if v not in expr.exponent.free_symbols() and expr.base.is_equal(v):
                n1 = expr.exponent + Symbolic.One()
                return (v**n1)/n1
        if isinstance(expr, Symbolic.Apply):
            # I(x)(D(x)(f(x))) -> f(x)
            if isinstance(expr.coeff, Differential):
                assert len(expr.seq[0])==1,`expr.seq`
                if expr.params[0].is_equal(v):
                    return expr.seq[0]
            if 0 and isinstance(expr.coeff, (SymbolicFunction, Symbolic.ElementaryFunction)):
                # I(x)(f(a*x)) -> F(a*x)/a whenever f.primitive(1)->F
                ii = None
                for i in range(len(expr.seq)):
                    if expr.seq[i].free_symbols()==set([v]):
                        if ii is None:
                            a = expr.seq[i].diff(v)
                            if v not in a.free_symbols():
                                ii = i
                        else:
                            # cannot handle I(x)(f(x,x))
                            ii = None
                            break
                if ii is not None:
                    p = expr.coeff.primitive(ii+1)
                    return p(*expr.seq)/a
        return Symbolic.Apply(self, expr)


class Differential(SymbolicOperator):

    def __new__(cls, x, n = None):
        if isinstance(x, (tuple, list)):
            assert n is None,`n`
            assert len(x)==2,`len(x)`
            x,n = x
        if n is None:
            n = 1
        n = Symbolic(n)
        x = Symbolic(x)
        assert isinstance(x, Symbolic.SymbolBase),`type(x)`
        obj = Symbolic.__new__(cls, 'Diff', [x, n])
        return obj

    def calc_substitute(self, subst, replacement):
        flag, params = self._apply_mth('substitute', self.params, (subst, replacement))
        if flag:
            return self.__class__(*params)
        return self

    def tostr(self, level=0):
        precedence = self.get_precedence()
        x,n = self.params
        if isinstance(n, Symbolic.One):
            s = '%s(%s)' % (self.label, x.tostr())
        else:
            s = '%s(%s, %s)' % (self.label, x.tostr(), n.tostr())
        if precedence <= level:
            return '(%s)' % (s)
        return s

    def calc_free_symbols(self):
        return set()

    def __call__(self, expr):
        v, n = self.params
        if not isinstance(n, Symbolic.Integer):
            return Symbolic.Apply(self, expr)
        expr = Symbolic(expr).expand()
        n = int(n)
        if not n:
            return expr
        elif n>1:
            D1 = Differential(v)
            r = expr
            for i in range(n):
                r = D1(r)
            return r
        assert n==1,`n`
        return expr.diff(v)

Symbolic.singleton_classes['D'] = SymbolicFunctionGenerator
Symbolic.singleton_classes['Diff'] = lambda : Differential
Symbolic.singleton_classes['Int'] = lambda : Integral
Symbolic.SymbolicFunction = SymbolicFunction
Symbolic.SymbolicFunctionGenerator = SymbolicFunctionGenerator
Symbolic.Differential = Differential
Symbolic.Integral = Integral
Symbolic.DefinedIntegral = DefinedIntegral
Symbolic.IndefinedIntegral = IndefinedIntegral

#EOF
