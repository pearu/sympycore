
from ..utils import EQ, LT
from .algebra import Algebra
from .verbatim import Verbatim

class Relational(Algebra):
    """ Represents relational expression: ``<lhs> <relation> <rhs>``.

    Parts of the relational expressions are hold in a pair::

      (<relation>, (<lhs>, <rhs>))

    Possible relations:

      EQ - mathematical equality
      LT - mathematical less-than (if defined)
      ...

    __nonzero__ returns lexicographic value of the relation

    """

    def __nonzero__(self):
        head, (lhs, rhs) = self.pair
        if head is EQ:
            lh, ld = lhs.pair
            rh, rd = rhs.pair
            return lh is rh and ld==rd
        if head is LT:
            lh, ld = lhs.pair
            rh, rd = rhs.pair
            return (lh < ld) or (lh is rh and ld < rd)
        #...
        return True

    def as_verbatim(self):
        return Verbatim(self.head, self.data)
