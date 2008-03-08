
from ..utils import EQ, NE, LT, LE, GT, GE
from ..basealgebra import Algebra, Verbatim

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

    def __nonzero__(self):
        head, data = self.pair
        if head is EQ: return Algebra.__eq__(*data)
        if head is NE: return Algebra.__ne__(*data)
        if head is LT: return Algebra.__lt__(*data)
        if head is LE: return Algebra.__le__(*data)
        if head is GT: return Algebra.__gt__(*data)
        if head is GE: return Algebra.__ge__(*data)
        #...
        return True

    def as_verbatim(self):
        return Verbatim(self.head, self.data)
