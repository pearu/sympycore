
from ..core import Basic, sympify, objects, classes
from ..core.function import new_function_value
from ..core.utils import UniversalMethod
from .basic import BasicArithmetic
from .function import ArithmeticFunction, Function, FunctionType
from .operations import BaseExpDict

__all__ = ['Mul', 'Div']

one = objects.one
zero = objects.zero

class Mul(ArithmeticFunction):
    """ Represents an evaluated multiplication operation.
    
    For example, Mul(x, y**2, sin(x)) represents
    the symbolic expression x * y**2 * sin(x).

    An Mul instance is a tuple/dict-like object. It means that
    when obj = Mul(*terms) is an Mul instance then
    1) obj.iterMul() returns an iterator such that
         obj == Mul(*obj.iterMul())
       holds,
    2) obj.iterBaseExp() returns an iterator such that
         obj == Mul(*[b**e for (b,e) in obj.iterBaseExp()])
       holds.
    """
    
    def __new__(cls, *args):
        return BaseExpDict(map(sympify,args)).as_Basic()
    
    @property
    def precedence(self):
        return Basic.Mul_precedence

    def compare(self, other):
        c = cmp(self._dict_content.coeff, other._dict_content.coeff)
        if c:
            return c
        c = cmp(self.count_ops(symbolic=False), self.count_ops(symbolic=False))
        if c:
            return c
        return cmp(self._dict_content, other._dict_content)

    def tostr(self, level=0):
        p = self.precedence
        r = '@*@'.join([op.tostr(p) for op in self.iterSorted()]) or '1'
        r = r.replace('-1@*@','-').replace('@*@','*')
        if p<=level:
            r = '(%s)' % r
        return r

    def iterBaseExp(self, full=False):
        coeff = self._dict_content
        if not full or (coeff is one or not isinstance(coeff, classes.Rational)):
            return self._dict_content.iterBaseExp()

    def expand(self, **hints):
        if hints.get('basic', True):
            it = iter(self)
            a = it.next()
            b = Mul(*it)
            a = a.expand(**hints)
            b = b.expand(**hints)
            if isinstance(a, classes.Add):
                return (a._dict_content * b).as_Basic()
            elif isinstance(b, classes.Add):
                return (b._dict_content * a).as_Basic()
            return Mul(a, b)
        return self

    def iterMul(self):
        return iter(self)

    def as_term_coeff(self):
        d = self._dict_content
        c = d.coeff
        if c is one:
            return self, c
        d = BaseExpDict(())
        for k,v in self.iterBaseExp():
            if k==c: continue
            d[k] = v
        return d.as_Basic(), c

    def as_base_exponent(self):
        if not self._dict_content.coeff is one:
            t, c = self.as_term_coeff()
            b, e = t.as_base_exponent()
            p = c.try_power(1/e)
            if p is not None:
                return p*b, e
            return self, one
        p = None
        for b,e in self.iterBaseExp():
            if not isinstance(e, classes.Rational):
                p = None
                break
            if p is None:
                p, q = e.p, e.q
                if p<0:
                    sign = -1
                else:
                    sign = 1
            else:
                if e.p>0 and sign==-1:
                    sign = 1
                p = classes.Integer.gcd(abs(e.p), p)
                q = classes.Integer.gcd(e.q, q)
        if p is not None:
            c = classes.Fraction(sign*q,p)
            if not c is one:
                return BaseExpDict([(b,e*c) for (b,e) in self.iterBaseExp()]).as_Basic(),1/c
        return self, one


    def try_power(self, other):
        t, c = self.as_term_coeff()
        if not c is one and isinstance(other, classes.Rational):
            return c**other * t**other

    def try_derivative(self, s):
        terms = list(self)
        factors = []
        for i in xrange(len(terms)):
            dt = terms[i].diff(s)
            if dt is zero:
                continue
            factors.append(Mul(*(terms[:i]+[dt]+terms[i+1:])))
        return classes.Add(*factors)

    def try_antiderivative(self, s):
        l1 = []
        l2 = []
        for t in self:
            if t.has(s):
                l1.append(t)
            else:
                l2.append(t)
        if not l1:
            return self * s
        if len(l1)==1:
            t = l1[0].try_antiderivative(s)
            if t is not None:
                return Mul(*(l2+[t]))
    
    _fdiff_cache = {}
    _fdiff_indices = ()

    @UniversalMethod
    def fdiff(obj, index=1):
        if isinstance(obj, type):
            # Mul = lambda x,y,z,..: Mul(x,y,z,..)
            # Mul_1 -> lambda x,y,z,..: Mul(1,y,z,..)
            # Mul_1_1 -> 0
            # Mul_1_2 -> lambda x,y,z,..: Mul(1,1,z,..)
            if index in obj._fdiff_indices:
                return objects.zero
            indices = obj._fdiff_indices + (index,)
            if indices in Mul._fdiff_cache:
                return Mul._fdiff_cache[indices]
            def canonize(cls, args):
                if index<=len(args):
                    return Mul(*[args[i] for i in range(len(args)) if i+1 not in indices])
                return objects.zero
            f = FunctionType('D%s(Mul)' % (`indices`), Mul,
                             dict(signature=obj.signature,
                                  canonize=classmethod(canonize),
                                  __new__ = Function.__new__,
                                  _fdiff_indices = indices
                                  ), is_global=False)
            Mul._fdiff_cache[indices] = f
            return f
        return obj._fdiff(index)

    def __mul__(self, other):
        other = sympify(other)
        if isinstance(other, classes.Number):
            if other is one:
                return self
            # here we shall skip d.canonical()
            d = BaseExpDict(())
            td = self._dict_content
            d.update(td)
            if td.coeff is one:
                coeff = other
                l = [other] + td.args_flattened
            else:
                coeff = other * td.coeff
                if coeff is one:
                    l = td.args_flattened[1:]
                else:
                    l = [coeff] + td.args_flattened[1:]
                del d[td.coeff]
            d[coeff] = one
            d.coeff = coeff
            d.args_flattened = l
            obj = new_function_value(Mul, l, {})
            obj._dict_content = d
            return obj
        return Mul(self, other)

    def matches(pattern, expr, repl_dict={}):
        wild_classes = (classes.Wild, classes.WildFunctionType)
        if not pattern.atoms(type=wild_classes):
            return Basic.matches(pattern, expr, repl_dict)
        wild_part = BaseExpDict(())
        exact_part = BaseExpDict(())
        for (b,e) in pattern.iterBaseExp():
            if b.atoms(type=wild_classes) or e.atoms(type=wild_classes):
                wild_part *= (b, e)
            else:
                exact_part *= (b, -e)
        if exact_part:
            exact_part *= expr
            res = wild_part.as_Basic().matches(exact_part.as_Basic(), repl_dict)
            return res
        log_pattern = classes.Add(*pattern.iterLogMul())
        log_expr = classes.Add(*expr.iterLogMul())
        return log_pattern.matches(log_expr, repl_dict)

class Div(BasicArithmetic):
    """
    Div() <=> 1
    Div(x) <=> 1/x
    Div(x, y, z, ...) <=> x / (y * z * ...)
    """
    def __new__(cls, *args):
        if len(args) == 1:
            return one/sympify(args[0])
        num, den = list(args[:1]), args[1:]
        return Mul(*(num + [one/Mul(*den)]))
