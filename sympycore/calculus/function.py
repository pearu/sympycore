
from ..core import Basic, BasicType, classes
from .algebra import Calculus

class FunctionType(BasicType):

    def __new__(typ, name, bases, attrdict):
        cls = type.__new__(typ, name, bases, attrdict)
        if 'Function' in name:
            setattr(classes, name, cls)
        else:
            Calculus.defined_functions[name] = cls
        return cls

class Function(Basic):
    """ Base class to calculus functions.
    """
    __metaclass__ = FunctionType

    @classmethod
    def derivative(cls, arg):
        """ Return derivative function of cls at arg.
        """
        raise NotImplementedError
