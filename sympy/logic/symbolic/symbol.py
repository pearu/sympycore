
from ...core.symbol import BasicSymbol, BasicDummySymbol, BasicWildSymbol
from .basic import BasicBoolean

__all__ = ['Boolean', 'DummyBoolean', 'WildBoolean']

class Boolean(BasicBoolean, BasicSymbol):
    """ Boolean symbol"""

class DummyBoolean(BasicDummySymbol, Boolean):
    """ Dummy boolean symbol"""

class WildBoolean(BasicWildSymbol, Boolean):
    """ Wild boolean symbol.
    """

BasicBoolean._symbol_cls = Boolean
