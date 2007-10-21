
from utils import memoizer_immutable_args
from basic import Basic, MutableCompositeDict, sympify
from methods import ArithMeths, ImmutableDictMeths#, RelationalMeths

class MutableAdd(ArithMeths, MutableCompositeDict):
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
            for k, v in a.items():
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
    @memoizer_immutable_args("Add.__new__")
    def __new__(cls, *args, **options):
        return MutableAdd(*args, **options).canonical()

    # canonize methods
    def canonical(self):
        return self

    # arithmetics methods
    def __iadd__(self, other):
        return Add(self, other)

    # object identity methods
    def DISABLE__hash__(self):
        h = self.__dict__.get('_cached_hash', None)
        if h is None:
            h = hash((Add,)+ self.as_tuple())
            self._cached_hash = h
        return h

    def DISABLEas_tuple(self):
        r = self.__dict__.get('_cached_as_tuple', None)
        if r is None:
            l = self.items()
            l.sort()
            r = tuple(l)
            self._cached_as_tuple = r
        return r


    def DISABLE__eq__(self, other):
        if isinstance(self, Add):
            return dict.__eq__(self, other)
        if isinstance(self, Basic):
            return False
        return self==sympify(other)

    def __getitem__(self, key):
        if isinstance(key, slice) or key.__class__ in [int, long]:
            return self.items()[key]
        return dict.__getitem__(self, key)

    def split(self, op, *args, **kwargs):
        if op == "+" and len(self) > 1:
            return ([c*x for x, c in self[:]])
        if op == "*" and len(self) == 1:
            x, c = self.items()[0]
            return [c] + x.split(op, *args, **kwargs)
        if op == "**":
            return [self, Basic.Number(1)]
        return [self]

    def tostr(self, level=0):
        seq = []
        items = self[:]
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
            obj = Add(*[(t.expand(*args, **hints), e) for (t,e) in self.items()])
        return obj

    def try_derivative(self, s):
        return Add(*[(t.diff(s), e) for (t,e) in self.items()])

    def __call__(self, *args):
        """
        (2*a + 3*sin)(x) -> 2*a(x) + 3*sin(x)
        """
        return Add(*[(t(*args), e) for (t,e) in self.items()])

    def fdiff(self, index=1):
        return Add(*[(t.fdiff(index), e) for (t,e) in self.items()])

    def clone(self):
        return MutableAdd(*[(t.clone(), c.clone()) for t,c in self.items()]).canonical()
