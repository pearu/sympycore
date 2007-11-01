"""
This package defines:

  - symbolic logic support features
  - set theory support features
"""

from .symbolic import (Boolean, DummyBoolean,
                       Not, And, Or, Xor, Equiv, Implies,
                       Predicate, PredicateType)

from .sets import (BasicSet, Union, Intersection, Difference, Complementary, Set,
                   SetSymbol, Empty, Universal, Element, Subset,
                   SetFunction, SetFunctionType, AsSet)

    
