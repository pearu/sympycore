"""
This package provides:
  - base class for set expressions: BasicSet
  - set operations: Union, Intersection, Minus, Complementary
  - singleton sets: Empty, Universal
  - explicit set of elements: Set
  - predicate functions: Element, Subset
"""

from ...core import Basic
from .basic import BasicSet, classes

from .symbol import SetSymbol, DummySet, WildSet, UniversalSet, EmptySet
from .function import SetFunction, SetFunctionType
from .set import Set
from .operations import Union, Intersection, Difference, Complementary

from .predicate import Element, Subset

set_classes = (BasicSet,)



def AsSet(obj, Basic=Basic):
    if isinstance(obj, set_classes):
        return obj
    if isinstance(obj, Basic):
        if isinstance(obj, classes.BasicSymbol):
            # XXX: check for dummy, wild
            return classes.SetSymbol(str(obj))
        if isinstance(obj, classes.BasicFunctionType):
            # XXX: check for dummy, wild function
            return classes.SetFunctionType(str(obj))
    return obj

# initialize singletons
Empty = EmptySet()
Universal = UniversalSet()


# initialize signatures:
from ...core.function import FunctionSignature
Union.signature = FunctionSignature([set_classes], set_classes)
Intersection.signature = FunctionSignature([set_classes], set_classes)
Difference.signature = FunctionSignature((set_classes, set_classes), set_classes)
Complementary.signature = FunctionSignature((set_classes,set_classes), set_classes)

Element.signature = FunctionSignature((Basic,set_classes), (bool,))
Subset.signature = FunctionSignature((set_classes,set_classes), (bool,))

del FunctionSignature, Basic

