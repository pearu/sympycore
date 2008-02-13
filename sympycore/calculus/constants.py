#
# Created January 2008 by Pearu Peterson
#

from ..core import Basic, classes
from ..basealgebra.primitive import SYMBOL

class Constant(str):

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, str(self))

    def evalf(self, precision=None):
        raise NotImplementedError('%s(%r).evalf'
                                  % (self.__class__.__name__, self))

    def as_algebra(self, cls):
        if cls is classes.Calculus:
            return cls(self, head=SYMBOL)
        return cls(self)

    def get_direction(self):
        if self in ['pi', 'E']:
            return 1
        return NotImplemented

const_pi = Constant('pi')
const_E = Constant('E')
