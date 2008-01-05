
from ..core import classes, objects, sympify, Basic

__all__ = ['s_Symbol', 's_Number', 's_Terms', 's_Factors']

one = objects.one
zero = objects.zero
assert one is classes.Integer(1)
assert zero is classes.Integer(0)
two = one+one
neg_one = -one

ListIterType = type(iter([]))
DictItemsIterType = type(dict().iteritems())

class s_Expr(object):

    pass

class s_Symbol(s_Expr):
    """ Holds anything that is not a number or sum or product.
    """
    def __init__(self, obj):
        self.obj = obj

    def __str__(self):
        return str(self.obj)

    def __repr__(self):
        return 's_Symbol(%s)' % (self.obj)

    def __neg__(self):
        return s_Terms([(self, neg_one)])

    def __add__(self, other):
        if isinstance(other, s_Number):
            return s_Terms([(s_one, other.n), (self, one)])
        if isinstance(other, s_Symbol):
            if self.obj == other.obj:
                return s_Terms([(self, two)])
            return s_Terms([(self, one), (other, one)])
        if isinstance(other, s_Factors):
            return s_Terms([(self, one), (other, one)])
        if isinstance(other, s_Terms):
            return other + self
        raise NotImplementedError('%s + %s' % (self, other))

    def __mul__(self, other):
        if isinstance(other, s_Number):
            return s_Terms([(self, other.n)])
        if isinstance(other, s_Symbol):
            if self.obj == other.obj:
                return s_Factors([(self, two)])
            return s_Factors([(self, one), (other, one)])
        raise NotImplementedError('%s * %s' % (self, other))

    def __pow__(self, other):
        assert isinstance(other, Integer),`other`
        return s_Factors([(self, other)])

class s_Number(s_Expr):
    """ Holds numbers, nan, oo, -oo, zoo.
    """
    def __init__(self, n):
        self.n = n

    def __eq__(self, other):
        if isinstance(other, s_Number):
            return self.n == other.n
        return False

    def __str__(self):
        return str(self.n)

    def __repr__(self):
        return 's_Number(%s)' % (self.n)

    def __neg__(self):
        return s_Number(-self.n)

    def __add__(self, other):
        if isinstance(other, s_Number):
            return s_Number(self.n + other.n)
        if isinstance(other, (s_Symbol, s_Factors)):
            return s_Terms([(s_one, self.n), (other, one)])
        if isinstance(other, s_Terms):
            return other + self
        raise NotImplementedError('%s + %s' % (self, other))

    def __mul__(self, other):
        if isinstance(other, s_Number):
            return s_Number(self.n * other.n)
        if isinstance(other, (s_Symbol, s_Factors)):
            return s_Terms([(other, self.n)])
        if isinstance(other, s_Terms):
            return other * self
        raise NotImplementedError('%s * %s' % (self, other))

    def __pow__(self, other):
        assert isinstance(other, Integer),`other`
        return s_Number(self.n ** other)

s_one = s_Number(one)

class s_Pairs(s_Expr):

    def __init__(self, pairs):
        # pairs may be changed inplace, so, if pairs are mutable,
        # make sure that they are new object or new copies.
        assert isinstance(pairs, (tuple, list, frozenset, dict, ListIterType, DictItemsIterType)), `type(pairs)`
        self._pairs = pairs
        self._dict = None
        self._set = None
        self._hash = None
        self.mutable = True

    @property
    def dict(self):
        """ The self can be changed only through this dict instance.
        """
        if not self.mutable:
            raise ValueError('object is immutable, dict attribute will not be available')
        d = self._dict
        if d is None:
            p = self._pairs
            if isinstance(p, dict):
                self._dict = d = p
            else:
                self._dict = d = dict(p)
        return d

    @property
    def frozenset(self):
        s = self._set
        if s is None:
            p = self._pairs
            if isinstance(p, dict):
                self._set = s = frozenset(p.iteritems())
            elif isinstance(p, frozenset):
                self._set = s = p
            else:
                self._set = s = frozenset(p)
            self.mutable = False
        return s

    def __iter__(self):
        d = self._dict
        if d is None:
            p = self._pairs
            if isinstance(p, dict):
                return p.iteritems()
            elif isinstance(p, (tuple, list, frozenset)):
                return iter(p)
            else:
                ## XXX: handles iterator
                self._pairs = p = tuple(p)
                return iter(p)
        return d.iteritems()

class s_Terms(s_Pairs):
    """ Holds terms as pairs (term, coeff).
    """

    def __str__(self):
        return ' + '.join(['%s*%s' % (t,c) for t,c in self])

    def __repr__(self):
        return 's_Terms(%s)' % (', '.join(['(%s, %s)' % (t,c) for t,c in self]))

    def __eq__(self, other):
        if isinstance(other, s_Terms):
            return self.frozenset==other.frozenset
        return False
    
    def __hash__(self):
        h = self._hash
        if h is None:
            self._hash = h = hash(('s_Terms', self.frozenset))
            self.mutable = False
        return h

    def __add__(self, other):
        r = s_Terms(iter(self))
        r += other
        return r

    def __iadd__(self, other):
        d = self.dict
        if isinstance(other, (s_Symbol, s_Factors)):
            b = d.get(other)
            if b is None:
                d[other] = one
            else:
                c = b + one
                if c is zero:
                    del d[other]
                else:
                    d[other] = c
        elif isinstance(other, s_Number):
            b = d.get(s_one)
            if b is None:
                d[s_one] = other.n
            else:
                c = b + other.n
                if c is zero:
                    del d[s_one]
                else:
                    d[s_one] = c
        elif isinstance(other, s_Terms):
            for t, c in other:
                b = d.get(t)
                if b is None:
                    d[t] = c
                else:
                    c = c + one
                    if c is zero:
                        del d[t]
                    else:
                        d[t] = c
        else:
            raise NotImplementedError('%s += %s' % (self, other))            
        return self

    def __imul__(self, other):
        d = self.dict
        if isinstance(other, s_Number):
            for t in c.keys():
                c[t] = c[t] * other
        else:
            raise NotImplementedError('%s *= %s' % (self, other))

    def __mul__(self, other):
        if isinstance(other, Number):
            r = s_Terms(())
            d = r.dict
            for t,c in self:
                d[t] = c * other
            return r
        raise NotImplementedError('%s * %s' % (self, other))

class s_Factors(s_Expr):
    """ Holds factors as pairs (base, integer_exp).
    """

    def __str__(self):
        return ' * '.join(['%s**%s' % (t,c) for t,c in self])

    def __repr__(self):
        return 's_Factors(%s)' % (', '.join(['(%s, %s)' % (t,c) for t,c in self]))

    def __hash__(self):
        h = self._hash
        if h is None:
            self._hash = h = hash(('s_Factors', self.frozenset))
            self.mutable = False
        return h

    def __eq__(self, other):
        if isinstance(other, s_Factors):
            return self.frozenset==other.frozenset
        return False

    def __add__(self, other):
        if isinstance(other, s_Factors):
            if self==other:
                return s_Terms([(self, two)])
            return s_Terms([(self, one), (other, one)])
        if isinstance(other, (s_Number, s_Terms, s_Symbol)):
            return s_Terms([(self, one), (other, one)])
        raise NotImplementedError('%s + %s' % (self, other))

    def __mul__(self, other):
        r = s_Factors(iter(self))
        r *= other
        return r

    def __imul__(self, other):
        d = self.dict
        if isinstance(other, (s_Symbol, s_Terms)):
            b = d.get(other)
            if b is None:
                d[other] = one
            else:
                c = b + one
                if c is zero:
                    del d[other]
                else:
                    d[other] = c
        elif isinstance(other, s_Factors):
            for t, c in other:
                b = d.get(t)
                if b is None:
                    d[t] = c
                else:
                    c = c + one
                    if c is zero:
                        del d[t]
                    else:
                        d[t] = c
        else:
            raise NotImplementedError('%s *= %s' % (self, other))
        return self

classes.s_Symbol = s_Symbol
classes.s_Number = s_Number

def s_add_sequence(seq):
    d = s_Terms(())
    for expr in seq:
        d += expr
    return d

