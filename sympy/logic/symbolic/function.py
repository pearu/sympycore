
from ...core import Basic
from ...core.function import BasicFunction, BasicFunctionType
from ...core.utils import memoizer_immutable_args
from .basic import BasicBoolean

__all__ = ['PredicateType', 'Predicate']

class PredicateType(BasicBoolean, BasicFunctionType):

    pass

class Predicate(BasicBoolean, BasicFunction):
    """ Base class for predicate functions.
    """

    __metaclass__ = PredicateType
    
    # Predicate.signature is initialized in __init__.py
    return_canonize_types = (Basic, bool)

