
import types

from ..core import Basic, sympify, objects, classes, instancemethod, sexpr
from ..core.function import new_function_value
from .basic import BasicArithmetic
from .function import ArithmeticFunction, Function, FunctionType
from .sexpr import s_mul_sequence, s_toBasic, FACTORS, s_mul_bases_exps, TERMS, s_mul, NUMBER, s_power

__all__ = ['Mul', 'Div']

one = objects.one
zero = objects.zero
tuple_iter_types = (tuple, type(iter([])), type(iter(())), types.GeneratorType)

class Mul(ArithmeticFunction):
    
    def __new__(cls, arg0=objects.one, *args, **options):
        if not args:
            if isinstance(arg0, tuple_iter_types):
                # Mul is called in canonical form:
                #   Mul(<terms or terms iterator>, sexpr = <sexpr>)
                assert options.has_key('sexpr')
                return new_function_value(cls, arg0, options)
            else:
                assert not options.has_key('sexpr'),`type(arg0)`
                return sympify(arg0)
        assert not options.has_key('sexpr')
        new_args = [sympify(arg0).as_sexpr()] + [sympify(a).as_sexpr() for a in args]
        sexpr = s_mul_sequence(new_args)
        return s_toBasic(sexpr)

    @instancemethod(Function.as_sexpr)
    def as_sexpr(self, context=sexpr.ARITHMETIC):
        if context==sexpr.ARITHMETIC:
            if 'sexpr' in self.options:
                return self.options['sexpr']
        return Basic.as_sexpr(self, context=None)

    def as_term_intcoeff(self):
        s_self = self.as_sexpr()
        if s_self[0] is TERMS:
            assert len(s_self[1])==1,`self`
            t, c = list(s_self[1])[0]
            n1, c1 = c.as_term_intcoeff()
            if c1 is not one:
                if n1 is not one:
                    return s_toBasic((TERMS,frozenset([(t, n1)]),zero)), c1
                return s_toBasic(t), c1
        return self, one

    @property
    def precedence(self):
        return Basic.Mul_precedence

    @instancemethod(ArithmeticFunction.tostr)
    def tostr(self, level=0):
        p = self.precedence
        r = '@*@'.join([op.tostr(p) for op in self.iterSorted()]) or '1'
        r = r.replace('-1@*@','-').replace('@*@','*')
        if p<=level:
            r = '(%s)' % r
        return r

    def as_term_coeff(self):
        expr = self.as_sexpr()
        if expr[0] is FACTORS:
            return self, one
        if expr[0] is TERMS:
            if len(expr[1])==1:
                t, c = list(expr[1])[0]
                return s_toBasic(t), c
        # One should never end up here. But just for any case,
        # an exception will be raised in order to notify
        # that either something is wrong or needs more thought.
        raise NotImplementedError(`self, expr`)

    def as_base_exponent(self):
        sexpr = self.as_sexpr()
        if sexpr[0] is TERMS:
            t, c = self.as_term_coeff()
            b, e = t.as_base_exponent()
            p = c.try_power(1/e)
            if p is not None:
                return p*b, e
        elif sexpr[0] is FACTORS:
            e = None
            sign = 1
            for t,c in sexpr[1]:
                if e is None:
                    e = abs(c.p)
                    if c.p<0:
                        sign = -1
                    else:
                        sign = 1
                    continue
                e = classes.Integer.gcd(abs(e), c.p)
                if c.p > 0 and sign==-1:
                    sign = 1
                if e==1 and sign:
                    c = None
                    break
            if e is not None:
                e = classes.Integer(sign * e)
                return s_toBasic(s_mul_sequence([s_power(t,c/e) for t,c in sexpr[1]])), e
        return self, one
        
    def iterBaseExp(self, full=False):
        expr = self.as_sexpr()
        if expr[0] is FACTORS:
            for t,c in expr[1]:
                yield s_toBasic(t), c
        elif expr[0] is TERMS:
            assert len(expr[1])==1,`expr`
            t, c = list(expr[1])[0]
            yield sympify(c), one
            yield s_toBasic(t).as_base_exponent()
        else:
            raise ValueError(`str(self), expr`)

    def iterMul(self):
        return iter(self.args)

    def compare2(self, other):
        s1 = self.as_sexpr()
        s2 = other.as_sexpr()
        c = cmp(s1,s2)
        if c:
            return c
        c = cmp(self.count_ops(symbolic=False), self.count_ops(symbolic=False))
        if c:
            return c
        return cmp(self._dict_content, other._dict_content)

    @instancemethod(ArithmeticFunction.matches)
    def matches(pattern, expr, repl_dict={}):
        wild_classes = (classes.Wild, classes.WildFunctionType)
        if not pattern.atoms(type=wild_classes):
            return Basic.matches(pattern, expr, repl_dict)
        w_d = []
        e_d = []
        for (b,e) in pattern.iterBaseExp():
            if b.atoms(type=wild_classes) or e.atoms(type=wild_classes):
                w_d.append((b.as_sexpr(), e))
            else:
                e_d.append((b.as_sexpr(), -e))
        if e_d:
            e_d.append((expr.as_sexpr(), one))
            wild_part = s_toBasic(s_mul_bases_exps(w_d))
            exact_part = s_toBasic(s_mul_bases_exps(e_d))
            return wild_part.matches(exact_part, repl_dict)
        log_pattern = classes.Add(*pattern.iterLogMul())
        log_expr = classes.Add(*expr.iterLogMul())
        return log_pattern.matches(log_expr, repl_dict)

    @instancemethod(ArithmeticFunction.try_power)
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

    @classmethod
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

    fdiff = instancemethod(fdiff)(ArithmeticFunction)


class _oldMul(ArithmeticFunction):
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
    
    def as_term_coeff(self):
        d = self._dict_content
        c = d.coeff
        if c is one:
            return self, c
        d = BaseExpDict(())
        for k,v in self.iterBaseExp():
            if k==c:
                continue
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

    @instancemethod(ArithmeticFunction.try_power)
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

    @classmethod
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

    fdiff = instancemethod(fdiff)(ArithmeticFunction)

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

    @instancemethod(ArithmeticFunction.matches)
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

    def as_sexpr(self, context=sexpr.ARITHMETIC):
        if context==sexpr.ARITHMETIC:
            r = [t.as_sexpr(context) for t in self.args]
            return (sexpr.FACTORS,) + tuple(r)
        return Basic.as_sexpr(self, context=None)

class Div(Function):
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
