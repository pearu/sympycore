
from ..core import Basic
from ..logic.symbolic import Predicate

__all__ = ['Equal', 'Less']

class RelationalBasic(Predicate):

    @property
    def lhs(self): return self[0]
    @property
    def rhs(self): return self[1]
    def tostr(self, level=0):
        r = '%s %s %s' % (self.lhs, self.opsymbol, self.rhs)
        if self.precedence<=level:
            r = '(%s)' % (r)
        return r

class Equal(RelationalBasic):

    opsymbol = '=='

    @classmethod
    def canonize(cls, (lhs, rhs)):
        if lhs is rhs:
            return True

class Less(RelationalBasic):

    opsymbol = '<'

    @classmethod
    def canonize(cls, (lhs, rhs)):
        if lhs is rhs: return False
