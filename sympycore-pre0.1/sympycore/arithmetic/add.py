
import types

from ..core import Basic, sympify, objects, classes, BasicType, instancemethod, sexpr
from ..core.function import new_function_value
from .basic import BasicArithmetic
from .function import ArithmeticFunction, Function, FunctionType
#from .operations import TermCoeffDict
from .sexpr import s_add_sequence, s_toBasic, TERMS, s_expand, s_mul, s_add_terms_coeffs, NUMBER

__all__ = ['Add', 'Sub']

one = objects.one
zero = objects.zero
tuple_iter_types = (tuple, type(iter([])), type(iter(())), types.GeneratorType)

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

    An Add instance is a tuple/2-tuple-like object. It means that
    when obj = Add(*terms) is an Add instance then
    1) obj.iterAdd() returns an iterator such that
         obj == Add(*obj.iterAdd())
       holds,
    2) obj.iterTermCoeff() returns an iterator such that
         obj == Add(*[t*c for (t,c) in obj.iterTermCoeff()])
       holds where c are all rational numbers.

    This Add class uses s-expressions for an internal representation.
    """

    def __new__(cls, arg0=objects.zero, *args, **options):
        if not args:
            if isinstance(arg0, tuple_iter_types):
                # Add is called in canonical form:
                #   Add(<terms or terms iterator>, sexpr = <sexpr>)
                assert options.has_key('sexpr')
                return new_function_value(cls, arg0, options)
            else:
                assert not options.has_key('sexpr'),`type(arg0)`
                return sympify(arg0)
        assert not options.has_key('sexpr')
        new_args = [sympify(arg0).as_sexpr()] + [sympify(a).as_sexpr() for a in args]
        sexpr = s_add_sequence(new_args)
        return s_toBasic(sexpr)

    @instancemethod(Function.as_sexpr)
    def as_sexpr(self, context=sexpr.ARITHMETIC):
        if context==sexpr.ARITHMETIC:
            return self.options['sexpr']
        return Basic.as_sexpr(self, context=None)

    def as_term_intcoeff(self):
        s_self = self.as_sexpr()
        if s_self[0] is TERMS:
            numpart = s_self[2]
            if numpart is one:
                return self, one
            sign = cmp(numpart,0)
            if isinstance(numpart, classes.Rational) and sign:
                coeff = abs(numpart.p)
            else:
                coeff = None
            if not sign:
                numpart = None
            l = []
            for t,c in s_self[1]:
                n1, c1 = c.as_term_intcoeff()
                if c1.p > 0 and sign==-1 and numpart is None:
                    sign = 1
                if coeff is None:
                    coeff = abs(c1.p)
                    l.append((t,n1*c1/coeff))
                    if not sign:
                        sign = cmp(c1.p,0)
                    continue
                coeff = classes.Integer.gcd(abs(c1.p), coeff)
                if coeff==1 and sign==1:
                    coeff = None
                    break
                l.append((t,n1*c1/coeff))
            if coeff is not None:
                if sign==-1:
                    l = [(t,-c) for t,c in l]
                    coeff = -coeff
                elif coeff==1:
                    return self, one
                return s_toBasic((TERMS, frozenset(l), zero)), classes.Integer(coeff)
        return self, one

    @property
    def precedence(self):
        return Basic.Add_precedence

    @instancemethod(ArithmeticFunction.tostr)
    def tostr(self, level=0):
        p = self.precedence
        r = '@+@'.join([op.tostr(p) for op in self.iterSorted()]) or '0'
        r = r.replace('@+@-',' - ').replace('@+@',' + ')
        if p<=level:
            r = '(%s)' % r
        return r

    def iterTermCoeff(self):
        expr = self.as_sexpr()
        assert expr[0] is TERMS, `expr`
        for t,c in expr[1]:
            yield s_toBasic(t), sympify(c) # XXX: sympify?

    def iterAdd(self):
        return iter(self.args)

    def as_term_coeff(self):
        p = None
        for t,c in self.iterTermCoeff():
            if not isinstance(c, classes.Rational):
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
            if not (c is one):
                return s_toBasic(s_mul(self.as_sexpr(), (NUMBER,c))), 1/c
        return self, one

    @instancemethod(ArithmeticFunction.matches)
    def matches(pattern, expr, repl_dict={}):
        wild_classes = (classes.Wild, classes.WildFunctionType)
        if not pattern.atoms(type=wild_classes):
            return Basic.matches(pattern, expr, repl_dict)
        w_d = []
        e_d = []
        for (t,c) in pattern.iterTermCoeff():
            if t.atoms(type=wild_classes):
                w_d.append((t.as_sexpr(), c))
            else:
                e_d.append((t.as_sexpr(), -c))
        if e_d:
            e_d.append((expr.as_sexpr(), 1))
            wild_part = s_toBasic(s_add_terms_coeffs(w_d))
            exact_part = s_toBasic(s_add_terms_coeffs(e_d))
            return wild_part.matches(exact_part, repl_dict)
        patitems = [(t.as_sexpr(), c)for t,c in pattern.iterTermCoeff()]
        for i in xrange(len(patitems)):
            pt,pc = patitems[i]
            pt = s_toBasic(pt)
            rpat = s_toBasic(s_add_terms_coeffs(patitems[:i]+patitems[i+1:]))
            if isinstance(expr, Add):
                items1, items2 = [], []
                for t,c in expr.iterTermCoeff():
                    item = (t.as_sexpr(), c)
                    if item[1]==pc:
                        items1.append(item)
                    else:
                        items2.append(item)
                items = items1 + items2
            else:
                t,c = expr.as_term_coeff()
                items = [(t.as_sexpr(), c)]
            for i in xrange(len(items)):
                t, c = items[i]
                d = pt.matches(s_toBasic(t)*(c/pc), repl_dict)
                if d is None:
                    continue
                npat = rpat.replace_dict(d)
                nexpr = s_toBasic(s_add_terms_coeffs(items[:i]+items[i+1:]))
                d = npat.matches(nexpr, d)
                if d is not None:
                    return d
            d = pt.matches(zero, repl_dict)
            if d is not None:
                d = rpat.replace_dict(d).matches(expr, d)
            if d is not None:
                return d

    _fdiff_cache = {}
    _fdiff_indices = ()

    @classmethod
    def fdiff(obj, index=1):
        if isinstance(obj, type):
            # Add = lambda x,y,z,..: Add(x,y,z,..)
            # Add_1 -> lambda x,y,z,..: 1
            # Add_1_1 -> 0
            # Add_1_2 -> 0
            if obj._fdiff_indices:
                return objects.zero
            indices = obj._fdiff_indices + (index,)
            if indices in Add._fdiff_cache:
                return Add._fdiff_cache[indices]
            def canonize(cls, args):
                if index <= len(args):
                    return objects.one
                return objects.zero
            f = FunctionType('D%s(Add)' % (`indices`), Add,
                             dict(signature=obj.signature,
                                  canonize=classmethod(canonize),
                                  __new__ = Function.__new__,
                                  _fdiff_indices = indices
                                  ), is_global=False)
            Add._fdiff_cache[indices] = f
            return f
        return obj._fdiff(index)

    fdiff = instancemethod(fdiff)(ArithmeticFunction)

    def try_derivative(self, s):
        return Add(*[t.diff(s) * e for (t,e) in self.iterTermCoeff()])

    def try_antiderivative(self, s):
        l1, l2 = [], []
        for t in self:
            a = t.try_antiderivative(s)
            if a is None:
                l1.append(t)
            else:
                l2.append(a)
        if not l2:
            return
        if not l1:
            return Add(*l2)
        return Add(*l2) + classes.Integral(Add(*l1),classes.Tuple(s,1),
                                           is_canonical=True)

class _old_Add(ArithmeticFunction):
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

    @instancemethod(ArithmeticFunction.tostr)
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
            return Add(*[item.s_expand(**hints) for item in self])
        return self

    _fdiff_cache = {}
    _fdiff_indices = ()

    @classmethod
    def fdiff(obj, index=1):
        if isinstance(obj, type):
            # Add = lambda x,y,z,..: Add(x,y,z,..)
            # Add_1 -> lambda x,y,z,..: 1
            # Add_1_1 -> 0
            # Add_1_2 -> 0
            if obj._fdiff_indices:
                return objects.zero
            indices = obj._fdiff_indices + (index,)
            if indices in Add._fdiff_cache:
                return Add._fdiff_cache[indices]
            def canonize(cls, args):
                if index <= len(args):
                    return objects.one
                return objects.zero
            f = FunctionType('D%s(Add)' % (`indices`), Add,
                             dict(signature=obj.signature,
                                  canonize=classmethod(canonize),
                                  __new__ = Function.__new__,
                                  _fdiff_indices = indices
                                  ), is_global=False)
            Add._fdiff_cache[indices] = f
            return f
        return obj._fdiff(index)

    fdiff = instancemethod(fdiff)(ArithmeticFunction)

    def try_derivative(self, s):
        return Add(*[t.diff(s) * e for (t,e) in self.iterTermCoeff()])

    def try_antiderivative(self, s):
        l1, l2 = [], []
        for t in self:
            a = t.try_antiderivative(s)
            if a is None:
                l1.append(t)
            else:
                l2.append(a)
        if not l2:
            return
        if not l1:
            return Add(*l2)
        return Add(*l2) + classes.Integral(Add(*l1),classes.Tuple(s,1),
                                           is_canonical=True)

    def __mul__(self, other):
        other = sympify(other)
        if isinstance(other, classes.Number):
            return (self._dict_content * other).as_Basic()
        return classes.Mul(self, other)

    @instancemethod(ArithmeticFunction.matches)
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
            if isinstance(expr, Add):
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
            if not isinstance(c, classes.Rational):
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

    def as_sexpr(self, context=sexpr.ARITHMETIC):
        if context==sexpr.ARITHMETIC:
            r = [(t.as_sexpr(context), c.as_sexpr(context)) for t,c in self.iterTermCoeff()]
            return (sexpr.TERMS,) + tuple(r)
        return Basic.as_sexpr(self, context=None)

class Sub(Function):
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

