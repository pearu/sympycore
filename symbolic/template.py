"""
OBJECT - template class for a symbolic object

Comments:
1) Replace OBJECT with the name of Symbolic subclass
2) Methods that are defined below are mandatory.
3) Symbolic subclasses may redefine methods that are commented out.

Author: FULLNAME <EMAIL>
Created: MONTH, YEAR
"""

from base import Symbolic

class OBJECT(Symbolic):
    """ Represents symbolic object.
    """

    ###########################################################################
    #
    # Constructor methods
    #

    def __new__(cls,*data):
        # process data, type check, carry out some simple simplifications, etc.
        return Symbolic.__new__(cls,*data)

    def init(self, *data):
        self.data = data
        return

    def astuple(self): return (self.__class__.__name__,) + self.data

##     def eval_power(self):
##         """
##         exponent is symbolic object but not equal to 0, 1
##         """
##         return

    ############################################################################
    #
    # Informational methods
    #

##     def get_precedence(self):
##         return 0

##     def calc_symbols(self):
##         """ Find all symbols contained in the object.
##         """
##         return Symbolic.calc_symbols(self)

##     def calc_free_symbols(self):
##         """ Find free symbols of the expression. Different from
##         calc_symbols(), definite integration variables and function names are skipped.
##         """
##         return Symbolic.calc_free_symbols(self)

##     def is_positive(self): return False
##     def is_negative(self): return False
##     def is_odd(self): return False
##     def is_even(self): return False
    
    ###########################################################################
    #
    # Transformation methods
    #

    def tostr(self, level=0):
        precedence = self.get_precedence()
        #
        r = str(self.data)
        #
        if precedence <= level:
            return '(%s)' % r
        return r

##     def torepr(self):
##         return Symbolic.torepr(self)

##     def calc_todecimal(self, *args):
##         return Symbolic.calc_todecimal(self, *args)

##     def calc_expanded(self):
##         """ Perform expansion of the object.
##         """
##         return Symbolic.calc_expanded(self)

    ###########################################################################
    #
    # Comparison methods
    #

##     def compare(self, other):
##         """
##         Return -1,0,1 if the object is smaller, equal, or greater than other.
##         If the object is of different type from other then their classes
##         are ordered according to sorted_classes list.
##         """
##         # all redefinitions of compare method should start with the
##         # following three lines:
##         if self is other: return 0
##         c = self.compare_classes(other)
##         if c: return c
##         #
##         return Symbolic.compare(self, other)

    ############################################################################
    #
    # Substitution methods
    #

##     def calc_substitute(self, subst, replacement):
##         return Symbolic.calc_substitute(self, subst, replacement)

    ############################################################################
    #
    # Boolean methods
    #

##     def __invert__(self): return Symbolic.__invert__(self)
##     def __and__(self, other): return Symbolic.__and__(self, other)
##     def __or__(self, other): return Symbolic.__or__(self, other)

    ############################################################################
    #
    # Relational methods
    #

##     def __eq__(self, other): return Symbolic.__eq__(self, other)
##     def __lt__(self, other): return Symbolic.__lt__(self, other)
    # __gt__, __le__, __ge__, __ne__ are computed from __eq__ and __lt__

    ############################################################################
    #
    # Arithmetic operations
    #

##     def __pos__(self): return Symbolic.__pos__(self)
##     def __neg__(self): return Symbolic.__neg__(self)
##     def __add__(self, other): return Symbolic.__add__(self, other)
##     def __mul__(self, other): return Symbolic.__mul__(self, other)
##     def __pow__(self, other): return Symbolic.__pow__(self, other)

    ############################################################################
    #
    # Functional methods
    #
    
##     def __call__(self, *args): return Symbolic.__call__(self, *args)
##     def diff(self, *args): return Symbolic.diff(self, *args)
##     def integrate(self, *args): return Symbolic.integrate(self, *args)

#
# End of OBJECT class
#
################################################################################

Symbolic.OBJECT = OBJECT

# EOF
