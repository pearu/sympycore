
from ..core import Basic, objects, classes
from ..core.assume_utils import is_equal

__all__ = ['is_less', 'is_less_equal', 'is_greater', 'is_greater_equal']

def is_less(lhs, rhs, assumptions=None):
    """ Return True or False if the relation 'lhs < rhs' is satisfied or not.
    For non-numeric operants assumptions model will be used.
    If the result is undefined, return None.
    """
    if isinstance(lhs, classes.Number) and isinstance(rhs, classes.Number):
        return lhs < rhs
    d = rhs - lhs
    if isinstance(d, classes.Number):
        return d.is_positive
    if isinstance(d, classes.Infinity): return True
    if d==objects.moo: return False
    #print lhs, rhs
    #XXX: implement assumptions model

def is_less_equal(lhs, rhs, assumptions=None):
    if is_equal(lhs, rhs, assumptions):
        return True
    return is_less(lhs, rhs, assumptions)

def is_greater(lhs, rhs, assumptions=None):
    return is_less(rhs, lhs, assumptions)

def is_greater_equal(lhs, rhs, assumptions=None):
    return is_less_equal(rhs, lhs, assumptions)
