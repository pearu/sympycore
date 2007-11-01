
from ...core.function import BasicFunction, BasicFunctionType
from .basic import BasicSet

__all__ = ['SetFunction', 'SetFunctionType']

class SetFunctionType(BasicSet, BasicFunctionType):
    pass

class SetFunction(BasicSet, BasicFunction):
    """ Base class for Set functions.
    """
    __metaclass__ = SetFunctionType
    
    @property
    def domain(self):
        return self[0].domain

    @property
    def superset(self):
        return self[0]

