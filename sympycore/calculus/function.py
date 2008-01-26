
from ..core import Basic

class Function(Basic):
    """ Base class to calculus functions.
    """

    @classmethod
    def derivative(cls, arg):
        """ Return derivative function of cls at arg.
        """
        raise NotImplementedError
