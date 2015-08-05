**This page is obsolete**

# The `BasicBoolean` class #

The `sympy.logic.symbolic.basic` module implements a base class
`BasicBoolean` (derived from `Basic`) for logical symbols and operations.
Logical expressions have always two possible values: `True` or `False`.

## Logical symbols ##

The `sympy.logic.symbolic.boolean` defines `Boolean` (derived from `BasicBoolean`
and `BasicSymbol`) and `DummyBoolean`
classes to create logical symbols.

## Logical operators ##

The `sympy.logic.symbolic.predicate` defines `Predicate` function that
is a base class to the following logical operators:
  * `And(bool1 [, bool2, ..])` - represents logical AND operator
  * `Or(bool1 [, bool2, ..])` - represents logical OR operator
  * `Xor(bool1 [, bool2, ..])` - represents logical XOR operator
  * `Not(bool1)` - represents logical NOT unary operator
  * `Implies(bool1, bool2)` - represents logical IMPLIES binary operator
  * `Equiv(bool1, bool2)` - represents logical EQUIV binary operator