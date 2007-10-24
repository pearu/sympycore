"""
This package provides:
  - base class for set expressions: BasicSet
  - set operations: Union, Intersection, Minus, Complementary
  - singleton sets: Empty, Universal
  - explicit set of elements: Set
  - predicate functions: Element, Subset
"""

from ...core import Basic
from .basic import BasicSet

from .symbols import SetSymbol, UniversalSet, EmptySet
from .setfunction import SetFunction
from .set import Set
from .operations import Union, Intersection, Minus, Complementary

from .functions import Element, Subset

set_classes = (BasicSet,)

# initialize singletons
Empty = EmptySet()
Universal = UniversalSet()

# initialize signatures:
from ...core.function import FunctionSignature
Union.signature = FunctionSignature([set_classes], set_classes)
Intersection.signature = FunctionSignature([set_classes], set_classes)
Minus.signature = FunctionSignature((set_classes, set_classes), set_classes)
Complementary.signature = FunctionSignature((set_classes,set_classes), set_classes)

Element.signature = FunctionSignature((Basic,set_classes), (bool,))
Subset.signature = FunctionSignature((set_classes,set_classes), (bool,))

del FunctionSignature, Basic
