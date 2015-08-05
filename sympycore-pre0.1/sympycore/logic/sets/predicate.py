
from ...core import classes
from ..symbolic import Predicate

class Element(Predicate):
    """ Predicate function 'object is an element of a set'.
    """

    # Element.signature is initialized in sets module
    
    @classmethod
    def canonize(cls, (obj, set)):
        return set.try_element(obj)

class Subset(Predicate):
    """ Predicate function 'object is a subset of a set'.
    """

    # Subset.signature is initialized in sets module
    
    @classmethod
    def canonize(cls, (obj, set)):
        if obj.domain==set:
            return True
        if isinstance(obj, classes.EmptySet):
            return True
        return set.try_subset(obj)
