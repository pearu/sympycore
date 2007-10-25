
from ...core.function import BasicFunction
from .basic import BasicSet

class SetFunction(BasicSet, BasicFunction):
    """ Base class for Set functions.
    """
    @property
    def domain(self):
        return self[0].domain

    @property
    def superset(self):
        return self[0]

