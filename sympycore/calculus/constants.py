#
# Created January 2008 by Pearu Peterson
#
""" Provides Constant class.
"""
__docformat__ = "restructuredtext"
__all__ = ['Constant', 'const_pi', 'const_E']

from ..core import Basic, classes
from ..basealgebra.primitive import SYMBOL
from ..arithmetic.evalf import evalf

class Constant(str):

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, str(self))

    def evalf(self, precision=15):
        if self in ['pi', 'E']:
            return evalf(self, precision)
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

    @property
    def is_bounded(self):
        if self in ['pi', 'E']:
            return True
        return None

const_pi = Constant('pi')
const_E = Constant('E')
