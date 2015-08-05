"""
Author: Pearu Peterson <pearu.peterson@gmail.com>
Created: 2006
"""

__all__ = ['Symbol','DummySymbol']

import sys
from base import Symbolic, BooleanMethods, RelationalMethods, FunctionalMethods,\
     ArithmeticMethods

class SymbolBase(BooleanMethods, RelationalMethods, FunctionalMethods,
                 ArithmeticMethods, Symbolic):
    """ Represents a symbol with a label.
    """

    ###########################################################################
    #
    # Constructor methods
    #

    counter = 0
    def __new__(cls, label = None):
        if label is None:
            SymbolBase.counter += 1
            label = '%s_object_%s' % (cls.__name__, SymbolBase.counter)
            return Symbolic.__new__(cls, label)
        elif isinstance(label, Symbol):
            if cls is DummySymbol and not isinstance(label, cls):
                obj = cls(label.label)
                return obj
            return label
        elif isinstance(label, str):
            if cls is DummySymbol and label.endswith('_'):
                label = label[:-1]
        else:
            raise TypeError,'%s argument must be None|Symbol|str but got %s object' \
                  % (cls.__name__, label.__class__.__name__)
        c = Symbolic.singleton_classes.get(label, None)
        if c is not None:
            return c()
        namespace = Symbolic.get_Symbolic_namespace()
        assert isinstance(label, str)
        try:
            obj = namespace[label]
            if cls is DummySymbol and not isinstance(obj, cls):
                obj = namespace[label] = Symbolic.__new__(cls, label)
        except KeyError:
            obj = namespace[label] = Symbolic.__new__(cls, label)
        return obj

    def init(self, label):
        self.label = label
        return

    def astuple(self):
        return (self.__class__.__name__, self.label)

    def eval_power(base, exponent):
        """
        exponent is symbolic object but not equal to 0, 1
        """
        return

    ############################################################################
    #
    # Informational methods
    #

    def get_precedence(self): return 0

    def calc_symbols(self):
        raise NotImplementedError,'%s needs calc_symbols() method' \
              % (self.__class__.__name__)

    def calc_free_symbols(self):
        raise NotImplementedError,'%s needs calc_free_symbols() method' \
              % (self.__class__.__name__)

    ###########################################################################
    #
    # Transformation methods
    #

    def tostr(self, level=0):
        return self.label

    def calc_expanded(self): return self

    def todecimal(self): return self

    def calc_diff(self, *args):
        if not args: return self.calc_diff
        if len(args)>1: return Symbolic.Zero()
        if self.is_equal(*args):
            return Symbolic.One()
        return Symbolic.Zero()

    def calc_integrate(self, *args):
        # All calc_diff() methods must start with the following two lines:
        if not args: return self.calc_integrate
        if len(args)>1: return self.calc_integrate(args[0]).integrate(*args[1:])
        a = args[0]
        if isinstance(a, Symbolic.Range):
            if self.is_equal(a.coeff):
                return Symbolic.Half() * (a.seq[1]**2 - a.seq[0]**2)
            else:
                return (a.seq[1] - a.seq[0]) * self
        else:
            if self.is_equal(a):
                return Symbolic.Half() * self ** 2
            else:
                return a * self

    ###########################################################################
    #
    # Comparison methods
    #

    def compare(self, other):
        if self is other: return 0
        c = self.compare_classes(other)
        if c: return c
        return cmp(self.label, other.label)

    ############################################################################
    #
    # Substitution methods
    #

    def calc_substitute(self, subst, replacement):
        if self.is_equal(subst):
            return replacement
        return self

    ############################################################################
    #
    # Functional methods
    #

    def __call__(self, *args):
        return Symbolic.UndefinedFunction(self, *((0,)*len(args)))(*args)

#
# End of SymbolBase class
#
################################################################################

class Symbol(SymbolBase):
    """ Represents free symbols.
    """

    ############################################################################
    #
    # Informational methods
    #

    def calc_symbols(self):
        return set([self])

    calc_free_symbols = calc_symbols

#
# End of Symbol class
#
################################################################################


class DummySymbol(SymbolBase):
    """ Represents dummy symbols like lambda variables, integration variables, etc.
    """

    ############################################################################
    #
    # Informational methods
    #

    def calc_symbols(self):
        return set([self])

    def calc_free_symbols(self):
        return set()

    ###########################################################################
    #
    # Transformation methods
    #

    def tostr(self, level=0):
        return self.label + '_' 

#
# End of DummySymbol class
#
################################################################################

Symbolic.SymbolBase = SymbolBase
Symbolic.Symbol = Symbol
Symbolic.DummySymbol = DummySymbol
