
import itertools

from ..core.utils import memoizer_immutable_args, UniversalMethod
from ..core import Basic, sympify, Composite
from ..core.methods import MutableCompositeDict, ImmutableDictMeths

from .basic import BasicArithmetic

class Add2(BasicArithmetic, Composite):

    def __new__(cls, *args):
        return MutableAdd(*args, **options).canonical()        

class MutableAdd(BasicArithmetic, MutableCompositeDict):
    """ Represents a sum.

    3 + a + 2*b is Add({1:3, a:1, b:2})

    MutableAdd returns a mutable object. To make it immutable, call
    canonical() method.

    MutableAdd is useful in computing sums efficiently. For example,
    iteration like

      s = Integer(0)
      x = Symbol('x')
      i = 1000
      while i:
        i -= 1
        s += x**i

    can be made about 20 times faster by using

      s = MutableAdd()
      x = Symbol('x')
      i = 1000
      while i:
        i -= 1
        s += x**i
      s = s.canonical()

    See MutableCompositeDict.__doc__ for how to deal with mutable
    instances.
    """

    precedence = Basic.Add_precedence

    # canonize methods

    def update(self, a, p=1):
        """
        Add({}).update(a,p) -> Add({a:p})
        """
        acls = a.__class__

        if acls is dict:
            # construct Add instance from a canonical dictionary
            # it must contain Basic instances as keys as well as values.
            assert len(self)==0,`len(self)` # make sure no data is overwritten
            super(MutableAdd, self).update(a)
            return
        if acls is tuple and len(a)==2:
            self.update(*a)
            return

        a = Basic.sympify(a)
        # Flatten sum
        if a.is_MutableAdd:
            for k, v in a.iteritems():
                self.update(k, v*p)
            return
        # Add(3) -> Add({1:3})
        if a.is_Number:
            p = a * p
            a = Basic.one

        # If term is already present, add the coefficients together.
        # Otherwise insert new term.
        b = self.get(a, None)
        if b is None:
            self[a] = sympify(p)
        else:
            # Note: we don't have to check if the coefficient turns to
            # zero here. Zero terms are cleaned up later, in canonical()
            self[a] = b + p
        return

    def canonical(self):
        # self will be modified in-place,
        # always return an immutable object
        for k,v in self.items():
            if v.is_zero:
                if not (k.has(Basic.oo) or k.has(Basic.nan)):
                    # Add({a:0}) -> 0
                    del self[k]
        # turn self to an immutable instance
        if len(self)==0:
            return Basic.zero
        if len(self)==1:
            k,v = self.items()[0]
            if k.is_one:
                # Add({1:3}) -> 3
                return v
            if v.is_one:
                # Add({a:1}) -> a
                return k
        if self.has_key(Basic.oo):
            v = self[Basic.oo]
            if len(self)==1 and v==-1:
                self.__class__ = Add        
                return self
            if v.is_Number:
                if v.is_zero:
                    pass
                elif v.is_positive:
                    return Basic.oo
                elif v.is_negative:
                    return -Basic.oo
        self.__class__ = Add
        return self

    # arithmetics methods

    def __iadd__(self, other):
        self.update(other)
        return self


class Add(ImmutableDictMeths, MutableAdd):
    """
    Represents a sum. For example, Add(x, -y/2, 3*sin(x)) represents
    the symbolic expression x - y/2 + 3*sin(x).

    Automatic simplifications are performed when an Add object is
    constructed. In particular, rational multiples of identical terms
    are combined and nested sums are flattened. For example,

        Add(3*x, Add(4*x, y)) -> Add(7*x, y).

    The result from calling Add may be a simpler object. For example,

        Add(2, 3) -> 5
        Add(x, -x) -> 0
        Add() -> 0

    An Add instance is a dict-like object. Its terms are stored along
    with their rational multiplicities as key:value pairs. For example,
    x - y/2  + 3*sin(x) is equivalent to

        Add({x:Integer(1), y:Rational(-1,2), sin(x):Integer(3)}).

    You can create an Add object directly from a Python dict as above
    (however, when constructing an Add from a dict, the keys and values
    you provide must be ready canonical SymPy expressions.)

    Note that a rational multiple of a single term is represented as
    an Add object in SymPy. For example, 3*x*y is represented as
    Add({x*y:3}).

    Add is immutable. The MutableAdd class can be used for more
    efficient sequential summation (see its documentation for more
    information).
    """

    # constructor methods
    #@memoizer_immutable_args("Add.__new__")
    def __new__(cls, *args, **options):
        return MutableAdd(*args, **options).canonical()

    # canonize methods

    def canonical(self):
        return self

    def __iter2__(self): # workinprogress
        for k,v in self.iteritems():
            if k.is_one:
                yield v
            elif v.is_one:
                yield k
            else:
                yield Basic.Multiplication(v,k)

    # arithmetics methods

    def __iadd__(self, other):
        return Add(self, other)

    # object identity methods

    def __iter__(self):
        return iter([t*c for (t,c) in self.iteritems()])

    def __getitem__(self, key):
        if isinstance(key, slice):
            return [t*c for (t,c) in self.items()[key]]
        elif key.__class__ in [int, long]:
            t,c = self.items()[key]
            return t*c
        return dict.__getitem__(self, key)

    def split(self, op, *args, **kwargs):
        if op == "+" and len(self) > 1:
            return ([c*x for x, c in self.iteritems()])
        if op == "*" and len(self) == 1:
            x, c = self.items()[0]
            return [c] + x.split(op, *args, **kwargs)
        if op == "**":
            return [self, Basic.Number(1)]
        return [self]

    def tostr(self, level=0):
        seq = []
        items = self.iteritems()
        pp = Basic.Mul_precedence
        p = self.precedence
        for term, coef in items:
            if coef.is_one:
                t = term.tostr(p)
            elif term.is_one:
                t = coef.tostr(p)
            else:
                if coef==-1:
                    t = '-%s' % (term.tostr(p))
                else:
                    t = '%s*%s' % (coef.tostr(p), term.tostr(p))
            if seq:
                if t.startswith('-'):
                    seq += ['-',t[1:]]
                else:
                    seq += ['+',t]
            else:
                seq += [t]
        r = ' '.join(seq)
        if p<=level:
            r = '(%s)' % r
        return r

    def expand(self, *args, **hints):
        obj = self
        if hints.get('basic', True):
            obj = Add(*[(t.expand(*args, **hints), e) for (t,e) in self.iteritems()])
        return obj

    def try_derivative(self, s):
        return Add(*[(t.diff(s), e) for (t,e) in self.iteritems()])

    def __call__(self, *args):
        """
        (2*a + 3*sin)(x) -> 2*a(x) + 3*sin(x)
        """
        return Add(*[(t(*args), e) for (t,e) in self.iteritems()])

    @UniversalMethod
    def fdiff(obj, index=1):
        assert not isinstance(obj, BasicType),`obj`
        return Add(*[(t.fdiff(index), e) for (t,e) in obj.items()])

    def clone(self):
        return MutableAdd(*[(t.clone(), c.clone()) for t,c in self.iteritems()]).canonical()

    def iterAdd(self):
        iterator = self.iteritems()
        def itercall():
            t,c = iterator.next()
            if c.is_one:
                return t
            return t*c
        return iter(itercall, False)

    def iterMul(self):
        if len(self)==1:
            t, c = self.iteritems().next()
            if c.is_one:
                return t.iterMul()
            return iter([c,t])
        return iter([self])

    def iterLogMul(self):
        if len(self)==1:
            t, c = self.iteritems().next()
            if c.is_one:
                return t.iterLogMul()
            return itertools.chain(c.iterLogMul(),t.iterLogMul())
        return iter([Basic.Log(self)])

    def as_term_coeff(self):
        if len(self)==1:
            return self.items()[0]
        return self, Basic.Integer(1)

    def as_base_exponent(self):
        if len(self)==1:
            t, c = self.as_term_coeff()
            b, e = t.as_base_exponent()
            p = c.try_power(1/e)
            if p is not None:
                return p*b, e
        return self, Basic.Integer(1)
    
    def matches(pattern, expr, repl_dict={}):
        wild_classes = (Basic.Wild, Basic.WildFunctionType)
        if not pattern.atoms(type=wild_classes):
            return Basic.matches(pattern, expr, repl_dict)
        if len(pattern)==1:
            term, coeff = pattern.items()[0]
            return term.matches(expr/coeff, repl_dict)
        wild_part = []
        exact_part = []
        for (t,c) in pattern.iteritems():
            if t.atoms(type=wild_classes):
                wild_part.append((t,c))
            else:
                exact_part.append((t,-c))
        if exact_part:
            exact_part.append((expr, Basic.Integer(1)))
            return Add(*wild_part).matches(Add(*exact_part), repl_dict)
        piter = pattern.iteritems()
        t, c = piter.next()
        rest_pattern = Add(*piter)
        if expr.is_Add:
            items = expr.items()
            items1,items2=[],[]
            for (t1,c1) in items:
                if c1==c:
                    items1.append((t1,c1))
                else:
                    items2.append((t1,c1))
            items = items1 + items2
        else:
            items = [(expr, objects.one)]
        for i in range(len(items)):
            t1,c1 = items[i]
            d = t.matches(t1*(c1/c), repl_dict)
            if d is not None:
                new_pattern = rest_pattern.replace_dict(d)
                new_expr = Add(*(items[:i]+items[i+1:]))
                d2 = new_pattern.matches(new_expr, d)
                if d2 is not None:
                    return d2
        d = t.matches(Basic.Integer(0), repl_dict)
        if d is not None:
            return rest_pattern.replace_dict(d).matches(expr, d)
        return

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
        return Add(*(pos + [-sympify(x) for x in neg]))

