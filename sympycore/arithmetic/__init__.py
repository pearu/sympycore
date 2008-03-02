"""Low-level arithmetics support.

Arithmetic package provides:

  * low-level number types ``FractionTuple``, ``Float``, ``Complex``
  * base class ``Infinity`` for extended numbers
  * various low-level number theory functions: ``gcd``, ``multinomial_coefficients``, etc.

"""
__docformat__ = "restructuredtext"

__all__ = ['FractionTuple', 'Float', 'Complex', 'Infinity',
           'gcd', 'lcm', 'multinomial_coefficients', 'setdps', 'getdps', 'mpmath']

from . import mpmath
from .numbers import FractionTuple, Float, Complex, setdps, getdps
from .number_theory import gcd, lcm, multinomial_coefficients
from .infinity import Infinity
