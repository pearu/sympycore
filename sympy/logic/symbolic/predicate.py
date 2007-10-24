
from ...core import Basic
from ...core.function import Function
from ...core.utils import memoizer_immutable_args
from .basic import BasicBoolean

__all__ = ['Predicate']

class Predicate(BasicBoolean, Function):
    """ Base class for predicate functions.
    """
    # Predicate.signature is initialized in __init__.py
    return_canonize_types = (Basic, bool)

    @memoizer_immutable_args('Predicate.__new__')
    def __new__(cls, *args):
        return Function.__new__(cls, *args)
