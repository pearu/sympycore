
from basic import Basic, Composite, sympify

class MutableCompositeDict(Composite, dict):
    """ Base class for MutableAdd, MutableMul, Add, Mul.

    Notes:

    - In the following comments `Cls` represents `Add` or `Mul`.

    - MutableCls instances may be uncanonical, e.g.

        MutableMul(0,x) -> 0*x
        MutableMul() -> .
    
      The purpose of this is to be able to create an empty instance
      that can be filled up with update method. When done then one can
      return a canonical and immutable instance by calling
      .canonical() method.

    - Cls instances are cached only when they are created via Cls
      classes.  MutableCls instances are not cached.  Nor are cached
      their instances that are turned to immutable objects via the
      note below.

    - <MutableCls instance>.canonical() returns always an immutable
      object, MutableCls instance is turned into immutable object by
      the following code:

        <MutableCls instance>.__class__ = Cls

    - One should NOT do the reverse:

        <Cls instance>.__class__ = MutableCls

    - One cannot use mutable objects as components of some composite
      object, e.g.

        Add(MutableMul(2),3) -> raises TypeError
        Add(MutableMul(2).canonical(),3) -> Integer(5)
    """

    is_immutable = False

    # constructor methods
    def __new__(cls, *args):
        """
        To make MutableClass immutable, execute
          obj.__class__ = Class
        """
        obj = dict.__new__(cls)
        [obj.update(a) for a in args]
        return obj

    def __init__(self, *args):
        # avoid calling default dict.__init__.
        pass

    __hash__ = dict.__hash__

    # representation methods
    def torepr(self):
        return '%s(%s)' % (self.__class__.__name__, dict(self))

    # comparison methods
    def compare(self, other):
        if self is other: return 0
        c = cmp(self.__class__, other.__class__)
        if c: return c
        return dict.__cmp__(self, other)

    def __eq__(self, other):
        other = sympify(other)
        if self.__class__ is not other.__class__: return False
        return dict.__eq__(self, other)

    def replace(self, old, new):
        old = sympify(old)
        new = sympify(new)
        if self==old:
            return new
        lst = []
        flag = False
        for (term, coeff) in self[:]:
            new_term = term.replace(old, new)
            if new_term==term:
                new_term = term
            if new_term is not term:
                flag = True
            lst.append((new_term, coeff))
        if flag:
            cls = getattr(Basic, 'Mutable'+self.__class__.__name__)
            r = cls()
            for (term, coeff) in lst:
                r.update(term, coeff)
            return r.canonical()
        return self


class BasicImmutableMeths:
    """ Auxiliary class for making mutable class immutable.
    """

    is_immutable = True

    def __hash__(self):
        h = self.__dict__.get('_cached_hash', None)
        if h is None:
            h = hash((self.__class__,)+ tuple(self.as_list()))
            self._cached_hash = h
        return h


class ImmutableDictMeths(BasicImmutableMeths):
    """ Auxiliary class for making set immutable.
    """
    def __setitem__(self, k, v):
        raise TypeError('%s instance is immutable' % (self.__class__.__name__))

    def __delitem__(self, k):
        raise TypeError('%s instance is immutable' % (self.__class__.__name__))

    def popitem(self):
        raise TypeError('%s instance is immutable' % (self.__class__.__name__))

    def as_list(self):
        r = self.keys()
        r.sort(Basic.static_compare)
        return [dict.__getitem__(self, k) for k in r]

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return dict.__eq__(self, other)
        if isinstance(self, (Basic,bool)):
            return False
        return self==sympify(other)

class ImmutableSetMeths(BasicImmutableMeths):
    """ Auxiliary class for making set immutable.
    """

    def clear(self):
        raise TypeError('%s instance is immutable' % (self.__class__.__name__))

    def add(self, other):
        raise TypeError('%s instance is immutable' % (self.__class__.__name__))

    def discard(self, other):
        raise TypeError('%s instance is immutable' % (self.__class__.__name__))

    def pop(self):
        raise TypeError('%s instance is immutable' % (self.__class__.__name__))

    def remove(self, other):
        raise TypeError('%s instance is immutable' % (self.__class__.__name__))

    def update(self, other):
        raise TypeError('%s instance is immutable' % (self.__class__.__name__))

    def as_list(self):
        r = list(self)
        r.sort(Basic.static_compare)
        return r

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return set.__eq__(self, other)
        if isinstance(self, (Basic,bool)):
            return False
        return self==sympify(other)
