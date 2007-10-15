
"""
Defines relational classes.

"""


from utils import memoizer_immutable_args
from basic import Composite, sympify

class Relational(Composite, tuple):

    def __new__(cls, lhs, rhs):
        lhs, rhs = sympify(lhs), sympify(rhs)
        return tuple.__new__(cls, (lhs, rhs))

    @property
    def lhs(self):
        return self[0]

    @property
    def rhs(self):
        return self[1]

    def compare(self, other):
        if self is other: return 0
        c = cmp(self.__class__, other.__class__)
        if c: return c
        return cmp(id(self), id(other))

    def __hash__(self):
        return tuple.__hash__(self)

    def __eq__(self, other):
        other = sympify(other)
        if self is other: return True
        return False

    def __ne__(self, other):
        other = sympify(other)
        if self is other: return False
        return True


class Equality(Relational):

    rel_op = '=='

    # Never cache Equality instances, otherwise
    # infinite recursion will occur:
    def __new__(cls, lhs, rhs):
        sympify = cls.sympify
        lhs, rhs = sympify(lhs), sympify(rhs)
        if lhs is rhs: return True
        return tuple.__new__(cls, (lhs, rhs))

    @memoizer_immutable_args('Equality.__nonzero__')
    def __nonzero__(self):
        return self.lhs.compare(self.rhs)==0


class Unequality(Relational):

    rel_op = '!='

    @memoizer_immutable_args('Unequality.__new__')
    def __new__(cls, lhs, rhs):
        sympify = cls.sympify
        lhs, rhs = sympify(lhs), sympify(rhs)
        if lhs is rhs: return False
        return tuple.__new__(cls, (lhs, rhs))

    @memoizer_immutable_args('Unequality.__nonzero__')
    def __nonzero__(self):
        return self.lhs.compare(self.rhs)!=0


class StrictInequality(Relational):

    rel_op = '<'

    @memoizer_immutable_args('StrictInequality.__nonzero__')
    def __nonzero__(self):
        return self.lhs.compare(self.rhs)==-1


class Inequality(Relational):

    rel_op = '<='

    @memoizer_immutable_args('Inequality.__nonzero__')
    def __nonzero__(self):
        return self.lhs.compare(self.rhs)<=0
