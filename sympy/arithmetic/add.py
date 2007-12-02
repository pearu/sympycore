
from ..core import Basic, sympify, objects, classes
from .basic import BasicArithmetic
from .function import ArithmeticFunction
from .operations import TermCoeffDict

__all__ = ['Add', 'Sub']

one = objects.one
zero = objects.zero


class Add(ArithmeticFunction):
    """ Represents an evaluated addition operation.

    For example, Add(x, -y/2, 3*sin(x)) represents
    the symbolic expression x - y/2 + 3*sin(x).

    Automatic simplifications are performed when an Add object is
    constructed. In particular, rational multiples of identical terms
    are combined and nested sums are flattened. For example,

        Add(3*x, Add(4*x, y)) -> Add(7*x, y).

    The result from calling Add may be a simpler object. For example,

        Add(2, 3) -> 5
        Add(x, -x) -> 0
        Add() -> 0

    An Add instance is a tuple/dict-like object. It means that
    when obj = Add(*terms) is an Add instance then
    1) obj.iterAdd() returns an iterator such that
         obj == Add(*obj.iterAdd())
       holds,
    2) obj.iterTermCoeff() returns an iterator such that
         obj == Add(*[t*c for (t,c) in obj.iterTermCoeff()])
       holds where c are all rational numbers.
    """

    def __new__(cls, *args):
        return TermCoeffDict(map(sympify,args)).as_Basic()
    
    @property
    def precedence(self):
        return Basic.Add_precedence

    def tostr(self, level=0):
        p = self.precedence
        r = '@+@'.join([op.tostr(p) for op in self.iterSorted()]) or '0'
        r = r.replace('@+@-',' - ').replace('@+@',' + ')
        if p<=level:
            r = '(%s)' % r
        return r

    def iterTermCoeff(self):
        return self._dict_content.iterTermCoeff()

    def iterAdd(self):
        return iter(self.args)

    def expand(self, **hints):
        if hints.get('basic', True):
            return Add(*[item.expand(**hints) for item in self])
        return self

    def try_derivative(self, s):
        return Add(*[t.diff(s) * e for (t,e) in self.iterTermCoeff()])

    def __mul__(self, other):
        other = sympify(other)
        if other.is_Number:
            return (self._dict_content * other).as_Basic()
        return classes.Mul(self, other)

    def matches(pattern, expr, repl_dict={}):
        wild_classes = (classes.Wild, classes.WildFunctionType)
        if not pattern.atoms(type=wild_classes):
            return Basic.matches(pattern, expr, repl_dict)
        wild_part = TermCoeffDict(())
        exact_part = TermCoeffDict(())
        for (t,c) in pattern.iterTermCoeff():
            if t.atoms(type=wild_classes):
                wild_part += (t, c)
            else:
                exact_part += (t, -c)
        if exact_part:
            exact_part += expr
            res = wild_part.as_Basic().matches(exact_part.as_Basic(), repl_dict)
            return res
        patitems = list(pattern.iterTermCoeff())
        for i in xrange(len(patitems)):
            pt,pc = patitems[i]
            rpat = TermCoeffDict(patitems[:i]+patitems[i+1:]).as_Basic()
            if expr.is_Add:
                items1, items2 = [], []
                for item in expr.iterTermCoeff():
                    if item[1]==pc:
                        items1.append(item)
                    else:
                        items2.append(item)
                items = items1 + items2
            else:
                items = [expr.as_term_coeff()]
            for i in xrange(len(items)):
                t, c = items[i]
                d = pt.matches(t*(c/pc), repl_dict)
                if d is None:
                    continue
                npat = rpat.replace_dict(d)
                nexpr = TermCoeffDict(items[:i]+items[i+1:]).as_Basic()
                d = npat.matches(nexpr, d)
                if d is not None:
                    return d
            d = pt.matches(zero, repl_dict)
            if d is not None:
                d = rpat.replace_dict(d).matches(expr, d)
            if d is not None:
                return d

    def as_term_coeff(self):
        p = None
        for t,c in self.iterTermCoeff():
            if not c.is_Rational:
                p = None
                break
            if p is None:
                p, q = c.p, c.q
                if p<0:
                    sign = -1
                else:
                    sign = 1
            else:
                if c.p>0 and sign==-1:
                    sign = 1
                p = classes.Integer.gcd(abs(c.p), p)
                q = classes.Integer.gcd(c.q, q)
        if p is not None:
            c = classes.Fraction(sign*q,p)
            if not c is one:
                return TermCoeffDict([(t,v*c) for (t,v) in self.iterTermCoeff()]).as_Basic(),1/c
        return self, one

class Sub(BasicArithmetic):
    """
    Sub() <=> 0
    Sub(x) <=> -x
    Sub(x, y, z, ...) <=> x - (y + z + ...)
    """
    def __new__(cls, *args):
        if len(args) == 1:
            return -sympify(args[0])
        pos, neg = list(args[:1]), args[1:]
        return Add(*(pos + [-Add(*neg)]))

