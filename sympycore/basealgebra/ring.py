
from .algebra import BasicAlgebra

class CommutativeRing(BasicAlgebra):

    @classmethod
    def npower(cls, base, exp):
        """ Compute the power base ** exp where base, exp are numbers.
        """
        raise NotImplementedError('%s must define classmethod npower' #pragma NO COVER
                                  % (cls.__name__))                   #pragma NO COVER
    
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
