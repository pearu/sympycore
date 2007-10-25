
from ...core import Basic
from ...core.function import BasicFunction
from ...core.utils import memoizer_immutable_args
from .basic import BasicBoolean

__all__ = ['Predicate']

class Predicate(BasicBoolean, BasicFunction):
    """ Base class for predicate functions.
    """
    # Predicate.signature is initialized in __init__.py
    return_canonize_types = (Basic, bool)

    @memoizer_immutable_args('Predicate.__new__')
    def __new__(cls, *args):
        return BasicFunction.__new__(cls, *args)
