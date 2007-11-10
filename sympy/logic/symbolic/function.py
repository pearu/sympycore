
from ...core import Basic
from ...core.function import BasicFunction, BasicFunctionType
from .basic import BasicBoolean

__all__ = ['PredicateType', 'Predicate']

class PredicateType(BasicBoolean, BasicFunctionType):

    pass

class Predicate(BasicBoolean, BasicFunction):
    """ Base class for predicate functions.
    """

    __metaclass__ = PredicateType
    
    # Predicate.signature is initialized in __init__.py

    def tostr(self, level=0):
        return '%s(%s)' % (self.__class__.__name__,
                           ', '.join([c.tostr(self.precedence) for c in self]))
