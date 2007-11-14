
from ..core import Basic, sympify

"""
To override arithmetic methods, use the following templates:

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

class ArithmeticMethods:

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

class ArithmeticMethods2:

    def __pos__(self):
        return self

    def __neg__(self):
        return Basic.Mul(Basic.Integer(-1), self)

    def __add__(self, other):
        return Basic.Addition(self, other)

    def __sub__(self, other):
        return Basic.Addition(self, (-sympify(other)))

    def __mul__(self, other):
        return Basic.Mul(self, other)

    def __div__(self, other):
        return Basic.Mul(self, (sympify(other) ** (-1)))

    def __pow__(self, other):
        return Basic.Exponentiation(self, other)

    def __radd__(self, other):
        if isinstance(other, Basic):
            return Basic.Addition(other, self)
        return sympify(other) + self

    def __rsub__(self, other):
        if isinstance(other, Basic):
            return Basic.Addition(other, -self)            
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
            return Basic.Exponentiation(other, self)            
        return sympify(other) ** self

class NumberMethods(ArithmeticMethods):

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

