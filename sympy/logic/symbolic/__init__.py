"""
This package defines:

  - base class for logical expressions: BasicBoolean
  - logical operations And, Or, Xor, Not, Implies, Equiv
  - logical symbols: Boolean, DummyBoolean
  - base class for predicate functions: Predicate

"""

from .basic import BasicBoolean
from .symbol import Boolean, DummyBoolean
from .function import Predicate
from .operations import And, Or, Xor, Not, Implies, Equiv

boolean_classes = (BasicBoolean, bool)

# initialize signatures:
from ...core.function import FunctionSignature
Predicate.signature = FunctionSignature(None, boolean_classes)
And.signature = FunctionSignature(list(boolean_classes), boolean_classes)
Or.signature = FunctionSignature(list(boolean_classes), boolean_classes)
Xor.signature = FunctionSignature(list(boolean_classes), boolean_classes)
Not.signature = FunctionSignature((boolean_classes,), boolean_classes)
del FunctionSignature
