
from basic import Basic, sympify

"""
To override Basic relational and arithmetic methods, use the
following templates:

    def __<mth>__(self, other)
        other = sympify(other)
        if other.is_<class convertable to self class>:
            # applicable to Number classes
            other = other.as_<self class>
        if other.is_<same class as self>:
            ...<return result>
        return NotImplemented

    def __r<mth>__(self, other)
        if isinstance(other, Basic):
            return Basic.<mth related class>(other, self)            
        return sympify(other) <mth op> self 

"""

class RelationalMeths_disable:

    def __eq__(self, other):
        if self is other: return True
        return Basic.Equality(self, other)

    def __ne__(self, other):
        if self is other: return False
        return Basic.Unequality(self, other)

    def __lt__(self, other):
        return Basic.StrictInequality(self, other)

    def __gt__(self, other):
        return Basic.StrictInequality(other, self)

    def __le__(self, other):
        return Basic.Inequality(self, other)

    def __ge__(self, other):
        return Basic.Inequality(other, self)


class ArithMeths:

    def __pos__(self):
        return self

    def __neg__(self):
        return Basic.Mul(Basic.Integer(-1), self)

    def __add__(self, other):
        return Basic.Add(self, other)

    def __sub__(self, other):
        return Basic.Add(self, (-sympify(other)))

    def __mul__(self, other):
        return Basic.Mul(self, other)

    def __div__(self, other):
        return Basic.Mul(self, (sympify(other) ** (-1)))

    def __pow__(self, other):
        return Basic.Pow(self, other)

    def __radd__(self, other):
        if isinstance(other, Basic):
            return Basic.Add(other, self)
        return sympify(other) + self

    def __rsub__(self, other):
        if isinstance(other, Basic):
            return Basic.Add(other, -self)            
        return sympify(other) - self

    def __rmul__(self, other):
        if isinstance(other, Basic):
            return Basic.Mul(other, self)            
        return sympify(other) * self

    def __rdiv__(self, other):
        if isinstance(other, Basic):
            return Basic.Mul(other, self ** (-1))
        return sympify(other) / self

    def __rpow__(self, other):
        if isinstance(other, Basic):
            return Basic.Pow(other, self)            
        return sympify(other) ** self

    def try_power(self, exponent):
        """ Try evaluating power self ** exponent.
        Return None if no evaluation is carried out.
        Caller code must ensure that exponent is
        a Basic instance.
        """
        return

    def expand(self, *args, **kwargs):
        return self

    def split(self, op, *args, **kwargs):
        if op == '**':
            return [self, Basic.Number(1)]
        return [self]

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
        r.sort(Basic.compare)
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
        r.sort(Basic.compare)
        return r

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return set.__eq__(self, other)
        if isinstance(self, (Basic,bool)):
            return False
        return self==sympify(other)


class NumberMeths(ArithMeths):

    def __eq__(self, other):
        raise NotImplementedError('%s must implement __eq__ method' % (self.__class__.__name__))

    def __ne__(self, other):
        raise NotImplementedError('%s must implement __ne__ method' % (self.__class__.__name__))

    def __lt__(self, other):
        raise NotImplementedError('%s must implement __lt__ method' % (self.__class__.__name__))

    def __le__(self, other):
        raise NotImplementedError('%s must implement __le__ method' % (self.__class__.__name__))

    def __gt__(self, other):
        raise NotImplementedError('%s must implement __gt__ method' % (self.__class__.__name__))

    def __ge__(self, other):
        raise NotImplementedError('%s must implement __ge__ method' % (self.__class__.__name__))

    def __add__(self, other):
        raise NotImplementedError('%s must implement __add__ method' % (self.__class__.__name__))

    def __mul__(self, other):
        raise NotImplementedError('%s must implement __mul__ method' % (self.__class__.__name__))

    def __div__(self, other):
        raise NotImplementedError('%s must implement __div__ method' % (self.__class__.__name__))

    def __pow__(self, other):
        raise NotImplementedError('%s must implement __pow__ method' % (self.__class__.__name__))
