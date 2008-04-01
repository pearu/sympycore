
from ..core import classes
from ..utils import EQ, NE, LT, LE, GT, GE, SYMBOL, AND, NOT, OR, NUMBER
from ..basealgebra import Algebra, Verbatim

head_mth_map = {
    EQ: Algebra.__eq__,
    NE: Algebra.__ne__,
    LT: Algebra.__lt__,
    LE: Algebra.__le__,
    GT: Algebra.__gt__,
    GE: Algebra.__ge__,
    }

class Logic(Algebra):
    """ Represents n-ary predicate expressions.

    An expression ``predicate(*args)`` is hold in a pair::

      (<predicate constant or function>, args)

    The following constants are defined to represent predicate
    functions:

      EQ - equality predicate
      LT - less-than predicate


    ``Logic.__nonzero__`` returns lexicographic value of relational
    predicates, otherwise ``True``.

    """

    def __nonzero__(self, head_mth_get=head_mth_map.get):
        head, (lhs, rhs) = self.pair
        mth = head_mth_get(head)
        if mth is None:
            return True
        return mth(lhs, rhs)

    def as_verbatim(self):
        return Verbatim(self.head, self.data)

    def convert_operand(self, obj, typeerror=True):
        head = self.head
        if head in [LT, GT, LE, GE, EQ, NE]:
            return classes.Calculus.convert(obj, typeerror)
        if isinstance(obj, bool):
            return type(self)(NUMBER, obj)
        return self.convert(obj, typeerror)

    is_Lt = property(lambda self: self.head is LT)
    is_Le = property(lambda self: self.head is LE)
    is_Gt = property(lambda self: self.head is GT)
    is_Ge = property(lambda self: self.head is GE)
    is_Eq = property(lambda self: self.head is EQ)
    is_Ne = property(lambda self: self.head is NE)

    @classmethod
    def Symbol(cls, obj):
        return cls(SYMBOL, obj)

    @classmethod
    def Number(cls, obj):
        assert isinstance(obj, bool),`obj`
        return cls(NUMBER, obj)

    @classmethod
    def Lt(cls, *seq):
        # XXX: implement canonization
        return cls(LT, seq)

    @classmethod
    def Le(cls, *seq):
        # XXX: implement canonization
        return cls(LE, seq)

    @classmethod
    def Gt(cls, *seq):
        # XXX: implement canonization
        return cls(GT, seq)

    @classmethod
    def Ge(cls, *seq):
        # XXX: implement canonization
        return cls(GE, seq)

    @classmethod
    def Eq(cls, *seq):
        # XXX: implement canonization
        return cls(EQ, seq)

    @classmethod
    def Ne(cls, *seq):
        # XXX: implement canonization
        return cls(NE, seq)

    @classmethod
    def Or(cls, *seq):
        # XXX: implement canonization
        if not seq:
            return False
        return cls(OR, seq)

    @classmethod
    def And(cls, *seq):
        # XXX: implement canonization
        if not seq:
            return True
        return cls(AND, seq)

    @classmethod
    def Not(cls, obj):
        if isinstance(obj, bool):
            return not obj
        return cls(NOT, obj)

classes.Logic = Logic
