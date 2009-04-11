
from ...core import init_module, classes
from ...functions import FunctionRing, DifferentialRing

from ..algebra import Calculus

init_module.import_heads()

class CalculusFunctionRing(FunctionRing):

    """
    Functions ring with Calculus value algebra.
    """

    def __call__(self, *args):
        result = self.head.apply(Calculus, self.data, self, args)
        if result is not NotImplemented:
            return result
        return Calculus(APPLY, (self, args))

    @classmethod
    def get_differential_algebra(cls):
        return CalculusDifferentialRing

    @classmethod
    def get_value_algebra(cls):
        return Calculus
    
class CalculusDifferentialRing(DifferentialRing):

    @classmethod
    def get_apply_algebra(cls):
        return CalculusFunctionRing

    @classmethod
    def get_value_algebra(cls):
        return Calculus

classes.CalculusFunctionRing = CalculusFunctionRing
classes.CalculusDifferentialRing = CalculusDifferentialRing
