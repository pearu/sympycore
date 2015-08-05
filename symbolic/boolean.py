"""
Boolean - provides TRUE, FALSE singletons and And, Or, Not operations.

Author: Pearu Peterson <pearu.peterson#gmail.com>
Created: February, 2007
"""

__all__ = ['Boolean','And', 'Or', 'Not', 'XOr']

from base import Symbolic, CommutativeSequence, BooleanMethods
from singleton import ConstantSingleton

class Boolean(BooleanMethods,
              ConstantSingleton):
    """ Base class for TRUE and FALSE.
    """

    ############################################################################
    #
    # Informational methods
    #

    def __nonzero__(self):
        return self._tobool()

    ############################################################################
    #
    # Relational methods
    #

    def __eq__(self, other):
        return Symbolic.Equal(self, other)

    def compare(self, other):
        if self is other: return 0
        c = self.compare_classes(other)
        if c: return c
        return cmp(self._tobool(), other._tobool())

    ############################################################################
    #
    # Substitution methods
    #

    def substitute(self, subst, replacement=None):
        return self

    def neg_invert(self):
        return ~self

#
# End of TRUE class
#
################################################################################


class TRUE(Boolean):
    """ Represents True value.
    """

    ############################################################################
    #
    # Informational methods
    #

    def get_precedence(self): return 0
    def is_true(self): return True
    def is_false(self): return False

    ###########################################################################
    #
    # Transformation methods
    #

    def tostr(self, level=0): return 'TRUE'
    def _tobool(self): return True

    ############################################################################
    #
    # Boolean operations
    #

    def __invert__(self): return FALSE()
    def __and__(self, other): return other
    def __or__(self, other): return self

#
# End of TRUE class
#
################################################################################


class FALSE(Boolean):
    """ Represents False value.
    """

    ############################################################################
    #
    # Informational methods
    #

    def get_precedence(self): return 0
    def is_true(self): return False
    def is_false(self): return True

    ###########################################################################
    #
    # Transformation methods
    #

    def tostr(self, level=0): return 'FALSE'
    def _tobool(self): return False

    ############################################################################
    #
    # Boolean operations
    #

    def __invert__(self): return TRUE()
    def __and__(self, other): return self
    def __or__(self, other): return other

#
# End of FALSE class
#
################################################################################


class Not(BooleanMethods,
          Symbolic):
    """ Represents negation.

    ~ TRUE -> FALSE
    ~ FALSE -> TRUE
    """
    def __new__(cls, expr):
        expr = Symbolic(expr)
        lambda_args = None
        if isinstance(expr, Symbolic.Lambda):
            lambda_args = expr.args
            expr = expr.expr
        if isinstance(expr, Boolean):
            result = ~ expr
        elif isinstance(expr, Not):
            result = expr.expr
        else:
            result = Symbolic.__new__(cls, expr)
        if lambda_args is None:
            return result
        return Symbolic.Lambda(*(lambda_args + (result,)))

    def init(self, expr):
        self.expr = expr
        return

    def astuple(self):
        return (self.__class__.__name__, self.expr)

    ############################################################################
    #
    # Informational methods
    #
       
    def get_precedence(self): return 27

    ###########################################################################
    #
    # Transformation methods
    #

    def tostr(self, level=0):
        precedence = self.get_precedence()
        r = '~%s' % (self.expr.tostr(precedence))
        if precedence<=level:
            return '(%s)' % (r)
        return r

    def calc_expanded(self):
        """ Perform expansion of the object.
        ~ (a | b) -> ~a & ~b
        ~ (a & b) -> ~a | ~b
        """
        expr = self.expr.expand()
        if isinstance(expr, Boolean): return ~expr
        if isinstance(expr, Not): return expr.expr
        if isinstance(expr, Or): return And(*[~t for t in expr.seq])
        if isinstance(expr, And): return Or(*[~t for t in expr.seq])
        return ~expr

    ############################################################################
    #
    # Boolean methods
    #

    def __invert__(self): return self.expr

    ############################################################################
    #
    # Relational methods
    #

    def __eq__(self, other):
        return Symbolic.Equal(self, other)

#
# End of Not class
#
################################################################################


def flatten_and_sequence(seq):
    """
    a & TRUE -> a
    a & FALSE -> FALSE
    a & (b & c) -> a & b & c
    a & a -> a
    a & ~a -> FALSE
    """
    seq = list(seq)
    andseq = []
    lambda_args = None
    coeff = TRUE()
    while seq:
        t = seq.pop(0)
        lambda_args, t = Symbolic.process_lambda_args(lambda_args, t)
        if isinstance(t, TRUE):
            continue
        if isinstance(t, FALSE):
            coeff, andseq = FALSE(), []
            break
        if isinstance(t, And):
            seq.extend(t.seq)
            continue
        if (~t).is_in(andseq):
            coeff, andseq = FALSE(), []
            break
        if not t.is_in(andseq):
            andseq.append(t)
    if lambda_args is not None:
        return Symbolic.Lambda(*(lambda_args+(And(coeff, *andseq),))), []
    return coeff, andseq


class And(BooleanMethods,
          CommutativeSequence):
    """ Represents conjunction.
    """

    ###########################################################################
    #
    # Constructor methods
    #

    identity = True
    flatten_sequence = staticmethod(flatten_and_sequence)

    ############################################################################
    #
    # Informational methods
    #

    def get_precedence(self): return 25
    
    ###########################################################################
    #
    # Transformation methods
    #

    def tostr(self, level=0):
        delim = ' & '
        this_precedence = self.get_precedence()
        upper_precedence = level
        assert isinstance(self.coeff, TRUE),`self.coeff`
        r = delim.join([s.tostr(this_precedence) for s in self.seq])
        if this_precedence<=upper_precedence:
            return '(%s)' % r
        return r

    def calc_expanded(self):
        """ Perform expansion of the object.
        (a | b) & c -> (a & c) | (a & c)
        """
        seq = []
        for t in self.astuple()[1:]:
            t = t.expand()
            if not seq:
                if isinstance(t, Symbolic.Or):
                    seq = t.astuple()[1:]
                else:
                    seq.append(t)
            elif isinstance(t, Symbolic.Or):
                new_seq = []
                for f1 in seq:
                    for f2 in t.astuple()[1:]:
                        new_seq.append(f1 & f2)
                seq = new_seq
            else:
                seq = [f & t for f in seq]
        return Symbolic.Or(*seq)

    ############################################################################
    #
    # Relational methods
    #

    def __eq__(self, other):
        return Symbolic.Equal(self, other)

#
# End of And class
#
################################################################################


def flatten_or_sequence(seq):
    """
    a | TRUE -> TRUE
    a | FALSE -> a
    a | (b | c) -> a | b | c
    a | a -> a
    a | ~a -> TRUE
TODO:    a | (a & b) -> a
    """
    seq = list(seq)
    orseq = []
    coeff = FALSE()
    lambda_args = None
    while seq:
        t = seq.pop(0)
        lambda_args, t = Symbolic.process_lambda_args(lambda_args, t)
        if isinstance(t, TRUE):
            coeff, orseq = TRUE(), []
            break
        if isinstance(t, FALSE):
            continue
        if isinstance(t, Or):
            seq.extend(t.seq)
            continue
        if (~t).is_in(orseq):
            coeff, orseq = TRUE(), []
            break
        if not t.is_in(orseq):
            orseq.append(t)
    if lambda_args is not None:
        return Symbolic.Lambda(*(lambda_args+(Or(coeff, *orseq),))), []
    return coeff, orseq


class Or(BooleanMethods,
         CommutativeSequence):
    """ Represents disjunction.
    """

    ###########################################################################
    #
    # Constructor methods
    #

    identity = False
    flatten_sequence = staticmethod(flatten_or_sequence)

    ############################################################################
    #
    # Informational methods
    #

    def get_precedence(self): return 22
    
    ###########################################################################
    #
    # Transformation methods
    #

    def tostr(self, level=0):
        delim = ' | '
        this_precedence = self.get_precedence()
        upper_precedence = level
        r = delim.join([s.tostr(this_precedence) for s in self.seq])
        if this_precedence<=upper_precedence:
            return '(%s)' % r
        return r

    def calc_expanded(self):
        """ Perform expansion of the object.
        a | (b & ~a) -> a | b
        a | (b & a)  -> a
        """
        orig_r = r = self.__class__(*[t.expand() for t in self.seq])
        if isinstance(r, Or):
            flag = True
            while flag:
                flag = False
                seq = r.seq
                l = len(seq)
                for i in range(l):
                    ti = seq[i]
                    ti1 = ~ti
                    for j in range(l):
                        if i==j: continue
                        tj = seq[j]
                        if isinstance(tj, And):
                            if ti1.is_in(tj.seq):
                                new_tj = And(*[tt for tt in tj.seq if tt.compare(ti1)])
                                flag = True
                                break
                            if ti.is_in(tj.seq):
                                new_tj = ti
                                flag = True
                                break
                    if flag:
                        new_seq = seq[:j] + (new_tj,) + seq[j+1:]
                        r = Or(*new_seq)
                        if not isinstance(r, Or):
                            return r
                        break
        return r
    
    ############################################################################
    #
    # Relational methods
    #

    def __eq__(self, other):
        return Symbolic.Equal(self, other)

#
# End of Or class
#
################################################################################

def flatten_xor_sequence(seq):
    """
    a ^ TRUE -> ~a
    a ^ FALSE -> a
    a ^ (b ^ c) -> a ^ b ^ c
    a ^ a -> FALSE
    a ^ ~a -> TRUE
    """
    seq = list(seq)
    new_seq = []
    truth_index = 0
    lambda_args = None
    coeff = FALSE()
    while seq:
        t = seq.pop(0)
        lambda_args, t = Symbolic.process_lambda_args(lambda_args, t)
        if isinstance(t, TRUE):
            truth_index += 1
            continue
        if isinstance(t, FALSE):
            continue
        if isinstance(t, XOr):
            seq.extend(t.seq)
            continue
        t1 = ~t
        if t1.is_in(new_seq):
            t1.remove_in(new_seq)
            truth_index +=1
            continue
        if t.is_in(new_seq):
            t.remove_in(new_seq)
        else:
            new_seq.append(t)
    if not truth_index:
        coeff = FALSE()
    elif new_seq:
        if truth_index % 2:
            new_seq = new_seq[:-1] + [ ~ new_seq[-1] ]
    else:
        if truth_index % 2:
            coeff = TRUE()
    if lambda_args is not None:
        return Symbolic.Lambda(*(lambda_args+(XOr(coeff, *new_seq),))), []
    return coeff, new_seq


class XOr(BooleanMethods,
          CommutativeSequence):
    """ Represents exclusive disjunction.
    """

    ###########################################################################
    #
    # Constructor methods
    #

    identity = False
    flatten_sequence = staticmethod(flatten_xor_sequence)

    ############################################################################
    #
    # Informational methods
    #

    def get_precedence(self): return 23
    
    ###########################################################################
    #
    # Transformation methods
    #

    def tostr(self, level=0):
        delim = ' ^ '
        this_precedence = self.get_precedence()
        upper_precedence = level
        r = delim.join([s.tostr(this_precedence) for s in self.seq])
        if this_precedence<=upper_precedence:
            return '(%s)' % r
        return r

    def calc_expanded(self):
        """ Perform expansion of the object.
        a | (b & ~a) -> a | b
        """
        r = self.__class__(*[t.expand() for t in self.seq])
        if isinstance(r, XOr):
            pass
        return r
    
    ############################################################################
    #
    # Relational methods
    #

    def __eq__(self, other):
        return Symbolic.Equal(self, other)

#
# End of XOr class
#
################################################################################


Symbolic.And = And
Symbolic.Or = Or
Symbolic.XOr = XOr
Symbolic.Not = Not
Symbolic.TRUE = TRUE
Symbolic.FALSE = FALSE

Symbolic.singleton_classes['TRUE'] = TRUE
Symbolic.singleton_classes['FALSE'] = FALSE

# EOF
