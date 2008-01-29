
from .algebra import BasicAlgebra

class CommutativeRing(BasicAlgebra):
    """ Base class to commutative rings.

    Derived classes may redefine the following methods:
    
      Symbol(cls, obj), Number(cls, obj), Add(cls, *seq), Mul(cls, *seq),
      Pow(cls, base, exponent), Terms(cls, *seq), Factors(cls, *seq)
      as_Add_args(self), as_Mul_args(self), as_Pow_args(self),
      as_Terms_args(self), as_Factors_args(self)
    """
    __slots__ = ['_symbols']
    _symbols = None

    @classmethod
    def npower(cls, base, exp):
        """ Compute the power base ** exp where base, exp are numbers.
        """
        raise NotImplementedError('%s must define classmethod npower' #pragma NO COVER
                                  % (cls.__name__))                   #pragma NO COVER

    @property
    def symbols(self):
        """ Return a set of atomic subexpressions in a symbolic object.
        """
        symbols = self._symbols
        if symbols is None:
            args = self.args
            if args:
                symbols = set()
                for arg in args:
                    symbols |= arg.symbols
            else:
                symbols = set([self])
            self._symbols = symbols
        return symbols

    def has(self, obj):
        obj = self.convert(obj)
        return obj in self.symbols
    
    @classmethod
    def Add(cls, *seq):
        """ Compute sum over seq containing algebra elements.
        """
        raise NotImplementedError('%s must define classmethod Add'    #pragma NO COVER
                                  % (cls.__name__))                   #pragma NO COVER

    @classmethod
    def Mul(cls, *seq):
        """ Compute product over seq containing algebra elements.
        """
        raise NotImplementedError('%s must define classmethod Mul'    #pragma NO COVER
                                  % (cls.__name__))                   #pragma NO COVER

    @classmethod
    def Pow(cls, base, exponent):
        """ Compute power from base and exponent.
        Argument base must be an algebra element and exponent must be
        an element of exponent algebra.
        """
        raise NotImplementedError('%s must define classmethod Pow'     #pragma NO COVER
                                  % (cls.__name__))                    #pragma NO COVER

    @classmethod
    def Log(cls, arg, base=None):
        """ Compute logarithm of arg in base.
        Argument arg must be an element of exponent algebra and base
        is an element of an algebra.
        """
        raise NotImplementedError('%s must define classmethod Pow'     #pragma NO COVER
                                  % (cls.__name__))                    #pragma NO COVER

    @classmethod
    def Terms(cls, *seq):
        """ Compute sum over seq containing pairs (element, coefficient).
        elements must belong to algebra.
        coefficients must belong to the coefficient algebra.
        """
        raise NotImplementedError('%s must define classmethod Terms'   #pragma NO COVER
                                  % (cls.__name__))                    #pragma NO COVER

    @classmethod
    def Factors(cls, *seq):
        """ Compute product over seq containing pairs (element, exponent).
        elements must belong to algebra.
        exponents must belong to the exponent algebra.
        """
        raise NotImplementedError('%s must define classmethod Factors' #pragma NO COVER
                                  % (self.__class__.__name__))         #pragma NO COVER

    def as_Add_args(self):
        """ Return a sequence such that Add(*self.as_Add_args()) == self
        """
        raise NotImplementedError('%s must define method as_Add_args'  #pragma NO COVER
                                  % (self.__class__.__name__))         #pragma NO COVER
    
    def as_Mul_args(self):
        """ Return a sequence such that Mul(*self.as_Mul_args()) == self
        """
        raise NotImplementedError('%s must define method as_Mul_args'  #pragma NO COVER
                                  % (self.__class__.__name__))         #pragma NO COVER
    
    def as_Pow_args(self):
        """ Return a 2-tuple such that Pow(*self.as_Pow_args()) == self
        """
        raise NotImplementedError('%s must define method as_Pow_args'  #pragma NO COVER
                                  % (self.__class__.__name__))         #pragma NO COVER

    def as_Terms_args(self):
        """ Return a sequence such that Terms(*self.as_Terms_args()) == self
        """
        raise NotImplementedError('%s must define method as_Terms_args' #pragma NO COVER
                                  % (self.__class__.__name__))          #pragma NO COVER

    def as_Factors_args(self):
        """ Return a sequence such that Factors(*self.as_Factors_args()) == self
        """
        raise NotImplementedError('%s must define method as_Factors_args' #pragma NO COVER
                                  % (self.__class__.__name__))            #pragma NO COVER

    def __pos__(self):
        return self

    def __neg__(self):
        return self.Mul(self, self.convert(-1))

    def __add__(self, other):
        other = self.convert(other, False)
        if other is NotImplemented:
            return NotImplemented
        return self.Add(self, other)

    def __radd__(self, other):
        other = self.convert(other, False)
        if other is NotImplemented:
            return NotImplemented
        return self.Add(other, self)

    def __sub__(self, other):
        other = self.convert(other, False)
        if other is NotImplemented:
            return NotImplemented
        return self + (-other)

    def __rsub__(self, other):
        other = self.convert(other, False)
        if other is NotImplemented:
            return NotImplemented
        return other + (-self)

    def __mul__(self, other):
        other = self.convert(other, False)
        if other is NotImplemented:
            return NotImplemented
        return self.Mul(self, other)

    def __rmul__(self, other):
        other = self.convert(other, False)
        if other is NotImplemented:
            return NotImplemented
        return self.Mul(other, self)

    def __div__(self, other):
        other = self.convert(other, False)
        if other is NotImplemented:
            return NotImplemented
        if isinstance(other, (int, long)):
            other = self.Number(other)
        return self * other ** (-1)

    def __rdiv__(self, other):
        other = self.convert(other, False)
        if other is NotImplemented:
            return NotImplemented
        return other * self ** (-1)

    def __truediv__(self, other):
        other = self.convert(other, False)
        if other is NotImplemented:
            return NotImplemented
        return self * other ** (-1)

    def __rtruediv__(self, other):
        other = self.convert(other, False)
        if other is NotImplemented:
            return NotImplemented
        return other * self ** (-1)

    def __pow__(self, other):
        other = self.convert_exponent(other, False)
        if other is NotImplemented:
            return NotImplemented
        return self.Pow(self, other)

    def __rpow__(self, other):
        other = self.convert(other, False)
        if other is NotImplemented:
            return NotImplemented
        return self.Pow(other,  self.convert_exponent(self))

    @classmethod
    def Add_derivative(cls, args, x):
        return cls.Add(*[a.diff(x) for a in args])

    @classmethod
    def Mul_derivative(cls, args, x):
        terms = []
        Mul = cls.Mul
        for i in range(len(args)):
            da = args[i].diff(x)
            if da==0:
                continue
            terms.append(Mul(*(args[:i]+[da]+args[i+1:])))
        return cls.Add(*terms)

    @classmethod
    def Pow_derivative(cls, (b, e), x):
        if isinstance(e, (int, long)):
            de = 0
        else:
            de = e.diff(x)
        db = b.diff(x)
        if de==0:
            return b**(e-1) * db * e
        if db==0:
            return (b**e) * cls.Log(b) * de
        return (b**e) * (cls.Log(b) * de + db * e/b)

    def diff(self, x):
        """ Return derivative of the expression with respect to x.
        """
        x = self.convert(x)
        assert x.head is SYMBOL,`x`
        return self._diff(x.data, self.zero, self.__class__)

    def _diff(self, x):
        raise NotImplementedError('%s must define _diff method'     #pragma NO COVER
                                  % (self.__class__.__name__))      #pragma NO COVER


from .primitive import NUMBER, SYMBOL
