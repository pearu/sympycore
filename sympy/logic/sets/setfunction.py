
from ...core.function import Function
from .basic import BasicSet

class SetFunction(BasicSet, Function):
    """ Base class for Set functions.
    """
    @property
    def domain(self):
        return self[0].domain

    @property
    def superset(self):
        return self[0]

