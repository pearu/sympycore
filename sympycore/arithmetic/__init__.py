"""Low-level arithmetics support.

Arithmetic package provides:

  * low-level number types ``FractionTuple``, ``Float``, ``Complex``
  * base class ``Infinity`` for extended numbers
  * various low-level number theory functions: ``gcd``, ``multinomial_coefficients``, etc.

"""
__docformat__ = "restructuredtext"

__all__ = ['FractionTuple', 'Float', 'Complex', 'Infinity',
           'gcd', 'multinomial_coefficients']

from .numbers import FractionTuple, Float, Complex
from .number_theory import gcd, multinomial_coefficients
from .infinity import Infinity
