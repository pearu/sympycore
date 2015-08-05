"""
Author: Pearu Peterson <pearu.peterson@gmail.com>
Created: 2006
"""

__all__ = ['Equal','NotEqual','Less','Greater','LessEqual','GreaterEqual','Keyword']

from base import Symbolic, RelationalMethods, BooleanMethods

def get_rop_class(rop):
    if rop is None or rop in ['==','eq']: return Equal
    if rop in ['!=','<>','ne']: return NotEqual
    if rop in ['<','lt']: return Less
    if rop in ['>','gt']: return Greater
    if rop in ['<=','le']: return LessEqual
    if rop in ['>=','ge']: return GreaterEqual
    raise ValueError,`rop`

class Relational(BooleanMethods, Symbolic):

    ###########################################################################
    #
    # Constructor methods
    #

    def __new__(cls, lhs, rhs, rop=None):
        lhs = Symbolic(lhs)
        rhs = Symbolic(rhs)
        
        if cls is not Relational:
            rop_cls = cls
            if rop is not None:
                assert rop_cls is get_top_class(rop), `rop, rop_cls`
        else:
            rop_cls = get_rop_class(rop)
        if rop_cls is Greater:
            rop_cls = Less
            lsh, rhs = rhs, lhs
        elif rop_cls is GreaterEqual:
            rop_cls = LessEqual
            lsh, rhs = rhs, lhs

        if rop_cls.rel_op != '==':
            # all symbolic objects can be compared for equality
            if not isinstance(lhs, RelationalMethods):
                raise ValueError, 'binary operation %s not defined with %s' \
                      % (rop_cls.rel_op, lhs.__class__.__name__)
            if not isinstance(rhs, RelationalMethods):
                raise ValueError, 'binary operation %s not defined with %s' \
                      % (rop_cls.rel_op, rhs.__class__.__name__)
        
        return Symbolic.__new__(rop_cls, lhs, rhs)

    def init(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs
        return

    def astuple(self):
        return (self.__class__.__name__, self.lhs, self.rhs)

    ############################################################################
    #
    # Informational methods
    #

    def get_precedence(self): return 20

    def is_true(self):
        raise NotImplementedError,'%s needs is_true() method' % (self.__class__.__name__)

    def is_false(self):
        r = self.is_true()
        if r is None: return r
        return not r

    ###########################################################################
    #
    # Transformation methods
    #

    def tostr(self, level=0):
        precedence = self.get_precedence()
        r = '%s %s %s' % (self.lhs.tostr(precedence), self.rel_op, self.rhs.tostr(precedence))
        if precedence <= level:
            return '(%s)' % r
        return r

    def calc_expanded(self):
        return self.__class__(self.lhs.expand(),self.rhs.expand())

#
# End of Relational class
#
################################################################################


class Keyword(Relational):

    rel_op = '='

    def compare(self, other):
        if self is other: return 0
        c = self.compare_classes(other)
        if c: return c
        return self.lhs.compare(other.lhs) or self.rhs.compare(other.rhs)


class Equal(Relational):

    ###########################################################################
    #
    # Constructor methods
    #

    rel_op = '=='

    ############################################################################
    #
    # Informational methods
    #

    def is_true(self):
        return self.lhs.is_equal(self.rhs)

    ###########################################################################
    #
    # Comparison methods
    #

    def __nonzero__(self):
        return bool(self.is_true())

    def compare(self, other):
        if self is other: return 0
        c = self.compare_classes(other)
        if c: return c
        c = self.lhs.compare(other.lhs)
        if c:
            return self.lhs.compare(other.rhs) or self.rhs.compare(other.lhs)
        return self.rhs.compare(other.rhs)

    ############################################################################
    #
    # Boolean methods
    #

    def __invert__(self):
        return NotEqual(self.lhs, self.rhs)

#
# End of Equal class
#
################################################################################

class NotEqual(Relational):

    ###########################################################################
    #
    # Constructor methods
    #
    
    rel_op = '!='

    ############################################################################
    #
    # Informational methods
    #

    def is_true(self):
        return (~ self).is_true()

    ###########################################################################
    #
    # Comparison methods
    #

    def compare(self, other):
        if self is other: return 0
        c = self.compare_classes(other)
        if c: return c
        c = self.lhs.compare(other.lhs)
        if c:
            return self.lhs.compare(other.rhs) or self.rhs.compare(other.lhs)
        return self.rhs.compare(other.rhs)

    ############################################################################
    #
    # Boolean methods
    #

    def __invert__(self):
        return Equal(self.lhs, self.rhs)

#
# End of NotEqual class
#
################################################################################

class Less(Relational):

    ###########################################################################
    #
    # Constructor methods
    #

    rel_op = '<'

    ############################################################################
    #
    # Informational methods
    #
    
    def is_true(self):
        return self.lhs.is_less(self.rhs)

    ###########################################################################
    #
    # Comparison methods
    #

    def compare(self, other):
        if self is other: return 0
        c = self.compare_classes(other)
        if c:
            if not isinstance(other, Greater): return c
            c1 = self.lhs.compare(other.rhs) or self.rhs.compare(other.lhs)
            if c1: return c
            return c1
        return self.lhs.compare(other.lhs) or self.rhs.compare(other.rhs)

    ############################################################################
    #
    # Boolean methods
    #

    def __invert__(self):
        return LessEqual(self.rhs, self.lhs)

#
# End of Less class
#
################################################################################

class Greater(Relational):

    ###########################################################################
    #
    # Constructor methods
    #

    rel_op = '>'

    ############################################################################
    #
    # Informational methods
    #

    def is_true(self):
        return self.rhs.is_less(self.lhs)

    ###########################################################################
    #
    # Comparison methods
    #

    def compare(self, other):
        if self is other: return 0
        c = self.compare_classes(other)
        if c:
            if not isinstance(other, Less): return c
            c1 = self.lhs.compare(other.rhs) or self.rhs.compare(other.lhs)
            if c1: return c
            return c1
        return self.lhs.compare(other.lhs) or self.rhs.compare(other.rhs)

    ############################################################################
    #
    # Boolean methods
    #

    def __invert__(self):
        return LessEqual(self.lhs, self.rhs)

#
# End of Greater class
#
################################################################################

class LessEqual(Relational):

    ###########################################################################
    #
    # Constructor methods
    #

    rel_op = '<='

    ############################################################################
    #
    # Informational methods
    #

    def is_true(self):
        r = self.rhs.is_less(self.lhs)
        if r is None: return r
        return not r

    ###########################################################################
    #
    # Comparison methods
    #

    def compare(self, other):
        if self is other: return 0
        c = self.compare_classes(other)
        if c:
            if not isinstance(other, GreaterEqual): return c
            c1 = self.lhs.compare(other.rhs) or self.rhs.compare(other.lhs)
            if c1: return c
            return c1
        return self.lhs.compare(other.lhs) or self.rhs.compare(other.rhs)

    ############################################################################
    #
    # Boolean methods
    #

    def __invert__(self):
        return Less(self.rhs, self.lhs)

#
# End of LessEqual class
#
################################################################################

class GreaterEqual(Relational):

    ###########################################################################
    #
    # Constructor methods
    #

    rel_op = '>='

    ############################################################################
    #
    # Informational methods
    #
    
    def is_true(self):
        r = self.lhs.is_less(self.rhs)
        if r is None: return r
        return not r

    ###########################################################################
    #
    # Comparison methods
    #
    
    def compare(self, other):
        if self is other: return 0
        c = self.compare_classes(other)
        if c:
            if not isinstance(other, LessEqual): return c
            c1 = self.lhs.compare(other.rhs) or self.rhs.compare(other.lhs)
            if c1: return c
            return c1
        return self.lhs.compare(other.lhs) or self.rhs.compare(other.rhs)

    ############################################################################
    #
    # Boolean methods
    #

    def __invert__(self):
        return Less(self.lhs, self.rhs)

#
# End of GreaterEqual class
#
################################################################################

Symbolic.Keyword = Keyword
Symbolic.Equal = Equal
Symbolic.NotEqual = NotEqual
Symbolic.Less = Less
Symbolic.Greater = Greater
Symbolic.LessEqual = LessEqual
Symbolic.GreaterEqual = GreaterEqual

#EOF
