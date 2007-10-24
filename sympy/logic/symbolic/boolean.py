
from ...core.symbol import BasicSymbol, BasicDummySymbol
from .basic import BasicBoolean

__all__ = ['Boolean', 'DummyBoolean']

class Boolean(BasicBoolean, BasicSymbol):

    def as_dummy(self):
        return DummyBoolean(self.name)
    def compute_truth_table(self):
        return [self],{1:[True]}
    def conditions(self, type=None):
        return set()
    def minimize(self):
        return self

class DummyBoolean(BasicDummySymbol, Boolean):

    pass


