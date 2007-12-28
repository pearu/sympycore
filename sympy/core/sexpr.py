"""
S-expression constants.

See sympy/arithmetic/sexpr.py that implements add, mul, pow, expand of
arithmetic s-expressions.

TODO:
- implement union, intersection, complementary oprations in sympy/logical/set/sexpr.py
- implement and, or, not operations in sympy/logical/symbolic/sexpr.py
"""

__all__ = ['ARITHMETIC', 'LOGICAL_SYMBOLIC', 'LOGICAL_SET',
           'NUMBER','SYMBOLIC', 'TERMS', 'FACTORS'
           ]

# context words:
ARITHMETIC = 'arithmetic'
LOGICAL_SYMBOLIC = 'symbolic'
LOGICAL_SET = 'set'

# s-expr car symbols
NUMBER = intern('N')
# a number object that supports arithmetic operations with Python integers,
# the code uses operations +, *, and ** with integer exponent.
SYMBOLIC = intern('S')
# any immutable object that supports __eq__ with other such objects
TERMS = intern('+')
# terms (stored in a frozenset) are in the form (term, coeff)
# where coeff is number, a numeric term is in the form (1, number)
FACTORS = intern('*')
# factors (stored in a frozenset) are in the form (base, exp)
# where exp is integer and base is non-numeric (factors with
# numeric part is expressed as (TERMS, (<non-numberic> factor,1),(one, <numeric>)))
