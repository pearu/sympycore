.. -*- rest -*-

==================================================
Automatic evaluation rules of symbolic expressions
==================================================

:Authors:
  Pearu Peterson <pearu.peterson AT gmail DOT com>
  Fredrik Johansson

:Created:
  February 2008


.. section-numbering::

.. sidebar:: Table of contents

    .. contents::
        :depth: 2
        :local:

Introduction
============

This document gathers rules that are applied automatically when
performing operations with symbolic expressions.

Commutative ring operations
===========================

Operands
--------

In commutative ring operations, four types of operands are possible:

  * numbers, see examples below;
  * sums, e.g. ``3+x``, ``-1/2+x+y``;
  * products, e.g. ``3*x``, ``x**2 * z``;
  * symbols, e.g. ``x``, ``sin(x+z**2)``.

Depending on a particular ring, numbers can be

  * integers, e.g. ``-4``, ``0``, ``1``;
  * fractions, e.g. ``1/2``, ``-3/4``;
  * complex numbers, e.g. ``2+3/4*I``, ``-4*I``;
  * floating point numbers, e.g. ``1.2``, ``-3.14``;
  * extended numbers, e.g. ``+oo``, ``-oo``, ``zoo``, ``undefined``;

where real and imaginary parts of complex numbers can be integers,
fractions, or floating point numbers.

.. admonition:: Metarule 1

  Any rule containing symbols, should remain valid when the symbols
  are replaced by numbers.

Notes on extended numbers
`````````````````````````

Expressions containing extended numbers require special rules as
distributivity laws are not valid for extended numbers. An extended
number is defined as a quantity that has infinite or undefined
magnitude and has specified or undefined direction in the complex
plane. See below for detailed information.

Notes on floating point numbers
```````````````````````````````

Note that the distributivity law is not strictly valid also for
operations with floating point numbers but in the following we assume
it to hold for simplicity.

Operations
----------

In the following we consider three kinds of operations with operands:

  * addition: ``x + y``
  * multiplication: ``x * y``
  * exponentiation: ``x ** y``

These operations can be used to define other operations

  * negation: ``-x == x * (-1)``
  * subtraction: ``x - y == x + (-y)``
  * division: ``x / y == x * y**(-1)``

and hence there is no need to write rules for these operations.

.. admonition:: Rule 1: associativity

  In `associative`__ operations all parenthesis are eliminated
  (expressions are *flattened* and suboperands of operands are stored
  in the same set-like data structure).

  For example::

    x + (y + z) -> x + y + z
    (x + y) + z -> x + y + z
    x * (y * z) -> x * y * z
    (x * y) * z -> x * y * z

__ http://en.wikipedia.org/wiki/Associative

.. admonition:: Rule 2: commutativity

  In `commutative`__ operations the order of operands is insignificant
  (operands are stored in an unordered set-like data structure).

  For example::

    x + y == y + x
    x * y == y * x

__ http://en.wikipedia.org/wiki/Commutativity

.. admonition:: Rule 3: collecting equal expressions

  In commutative operations *equal* expressions are collected. The
  equality is defined as an *equality between data structures* which
  may not be equivalent to the notion of *mathematical equality*.

  For example::

    x + x -> 2*x
    x * x -> x**2


.. admonition:: Rule 4: operations with zero.

  Multiplication by zero is zero only when a non-zero operand does not
  contain extended numbers explicitly.

  For example::

    0 * x -> 0
    0 * (x + oo) -> undefined

  Division a non-zero number by zero is infinity with undefined direction::

    1/0 -> oo(+oo)
    0/0 -> undefined

  Exponentiation by zero results one.

  For example::

    x**0 -> 1
    oo**0 -> 1

.. admonition:: Rule 5: distributivity

  `Distributivity`__ law of multiplication over addition is applied
  only when a sum is multiplied by a number that is not an extended
  number.

  For example::

    3*(x + y) -> 3*x + 3*y
    (3 + x)/2 -> 3/2 + 1/2*x
    oo*(2 + x) -> oo*(2 + x)

__ http://en.wikipedia.org/wiki/Distributivity

The reason why distributivity law is not used in case of extended numbers
is that it might lead to undefined results that otherwise would be defined.
For example, if ``x=-1`` then::

  oo*(2 + x) -> oo*1 -> oo

but

::

  oo*(2 + x) -> oo + oo*x -> oo + oo*(-1) -> oo - oo -> undefined

All number sets (integers, rationals, complex numbers) are closed with
respect to addition and multiplication operations.  Hence:

.. admonition:: Rule 6: additing and multiplying numbers

  Addition and multiplication operations with numbers always result in
  a number.

Exponentiation operation with numbers are evaluated to a number when
possible. In case of algebraic numbers, suppresed evaluation may be
carried out. For example::

  2**3 -> 8
  2**(-3) -> 1/8
  4**(1/2) -> 2
  8**(1/2) -> 2*2**(1/2)

Integer powers
``````````````

.. admonition:: Rule 7: ``m ** n`` for a number ``m`` and integer ``n``.

  If ``n`` is ``0`` then the result is ``1``.

  If ``n`` is positive then the result is a number. Different
  algorithms are possible for cases where ``m`` is integer, or
  fraction, or floating point number, or complex number, or purely
  imaginary complex number.

  If ``n`` is negative then the result is ``1/(m**(-n))`` (or
  ``(1/m)**(-n)``).

.. admonition:: Rule 8: ``z ** n`` for extended number ``z=oo(theta)`` and integer ``n``.

  If ``n`` is ``0`` then the result is ``1``.

  If ``n`` is positive then::

    oo(theta)**n -> oo(n*theta)

  If ``n`` is negative then::

    oo(theta)**n -> 0

.. admonition:: Rule 9: ``(w*z) ** n`` for symbols ``w``, ``z``, and integer ``n``.

  The result is ``w**n * z**n``.

.. admonition:: Rule 10: ``(w**z) ** n`` for symbols ``w``, ``z``, and integer ``n``.

  The result is ``w**(n*z)``.

Fraction powers
```````````````

.. admonition:: Rule 11: ``m ** (1/q)`` for integers ``m``, ``q>0``.

  If ``m`` is positive then the result is a product of algebraic numbers.

  If ``m`` is negative then the result is ``(-1)**(1/q) * (-m)**(1/q)``

.. admonition:: Rule 12: ``m ** (p/q)`` for integers ``m``, ``p!=1``, ``q>0``.

  The result is evaluated result of ``(m ** (1/q))**p``.


Extended numbers
================

See also http://code.google.com/p/sympycore/wiki/ExtendedNumbers.

An extended number is defined as a quantity that has infinite or
undefined magnitude and has specified or undefined direction in the
complex plane.

Infinity with direction ``theta = Arg(direction)`` can be defined as
follows:

.. admonition:: Definition: infinity with direction

  ::

    oo(direction) =  lim     r * direction
                    r -> oo

  where ``direction`` is a complex number. 

.. admonition:: Definition: quantity with undefined magnitude.

  A quantity with undefined magnitude and undefined direction is defined as ``oo(0)``.

.. admonition:: Definition: projective infinity.

  Infinity with undefined direction is defined as ``oo(undefined)``.

The following notation is used::

  +oo = oo(1)
  -oo = oo(-1)
  zoo = oo(oo(0))

An operation ``<op>`` with an infinity and a finite number is defined
as follows:

.. admonition:: Definition: operations with finite numbers

  ::

    oo(direction) <op> number =   lim    r * direction <op> number
                                r -> oo

An operation ``<op>`` with two infinities with different directions is
defined as follows:

.. admonition:: Definition: operations with infinite numbers

  ::

    oo(dir1) <op> oo(dir2) =   lim      r1 * dir1 <op> r2 * dir2
                            r1, r2 -> oo

  where the limit processes ``r1->oo`` and ``r2->oo`` are independent.

  If ``lim(r1->oo, r2->oo)`` is different from ``lim(r2->oo, r1->oo)``
  then the result is defined as ``undefined``.

.. admonition:: Addition with infinities

  ::

    oo(x) + oo(y) -> oo(EqualArg(x,y)*x)
    oo(x) + z     -> oo((1+IsUnbounded(z)*(EqualArg(x,y)-1))*x)

.. admonition:: Multiplication with infinities

  ::

    oo(x) * oo(y) -> oo(x*y)
    oo(x) * z     -> oo(x*z)

.. admonition:: Dividing by infinity

  ::

    1/oo(x)       -> 0 for nonzero x

.. admonition:: Exponentiation with infinities

  ::

     oo(x) ** 0     -> 1
     1 ** oo(x)     -> 1
     oo(x) ** oo(y) -> 0                 if y < 0
     oo(x) ** oo(y) -> oo(IsPositive(x)) if y > 0
     oo(x) ** z     -> 0 if z < 0
     oo(x) ** z     -> oo(x**z) if z>0
     z ** oo(x)     -> (z**x) ** oo(1)

TODO: define more rules for defined results.

Function evaluations
====================

General rules
-------------

.. admonition:: Function evaluation.

  A function should automatically evaluate back to a number when given
  an input for which it assumes a rational or complex rational
  value.

An exception to this rule can be made if the computation required to
produce the number is extremely time-consuming.

.. admonition:: Floating-point function evaluation.

  Given a floating-point number ``x``, ``f(x)`` should return a
  floating-point approximation.

Exponentials
------------

``exp(x)`` is equivalent to ``E**x``, and implemented as a simple
wrapper for this operation.

Likewise, ``sqrt(x)`` is equivalent to ``x**(1/2)``.

Logarithms
----------

``log(x,b)`` is defined as ``log(x)/log(b)``. ``log(x)`` denotes the
natural logarithm with base ``b`` = ``E``. In general ``x`` and ``b``
are assumed to be complex numbers (meaning that some transformations
familiar for positive real numbers cannot be performed automatically
with symbolic arguments). If no simplifications can be found,
``log(x,b)`` is expanded automatically to ``log(x)/log(b)``.

.. admonition:: Evaluating ``log``: integer input.

  If ``x`` and ``b`` are both positive integers, ``log(x, b)``
  evaluates to an integer when exact (note that ``log(x)/log(b)`` does
  not).

.. admonition:: Evaluating ``log``: complex input.

  For complex arguments, ``log(x)`` is taken to be the principal
  branch of the natural logarithm, with the branch cut placed
  infinitesimally below the negative real half axis.

``log(x)`` evaluates to an explicit value at ``x`` = ``1``, ``E``,
``I`` and ``-I``. ``log(0)`` evaluates to ``-oo`` and ``log(oo)``
evaluates to ``oo``.

.. admonition:: Evaluating ``log``: power input.

  ``log(b**x, b)`` evaluates to ``x`` if ``b`` is positive and ``x``
  is real (in particular, if ``b`` is ``E`` and ``y`` is rational).
  By extension, ``log(b**x, b**y)`` evaluates to ``x/y`` if ``b`` is
  positive and ``x`` and ``y`` are both real.

TODO: log(-x), log(I*x), log(-I*x), ...


Trigonometric functions
-----------------------

Trigonometric functions are automatically evaluated to algebraic
values if the argument is an integral multiple of ``pi/6``.  (Direct
evaluation is currently also performed at all multiples of ``pi/12``;
this behavior could be adjusted.) The poles in ``tan`` and ``cot``
evaluate to ``zoo``. Trigonometric functions are kept unevaluated at
``-oo`` and ``oo`` (this can be useful when computing limits).

If the argument to a trigonometric function contains an explicit
rational multiple of ``pi`` as a term, this term is replaced by
a multiple of pi in the interval ``[0, pi/2)`` using
trigonometric identities. This may involve replacing a sine
by a cosine, etc.

Explicit signs are moved out of the function, e.g.
``sin(-x) -> -sin(x)``. If the argument is a sum of several terms,
a sign is moved out if and only if all terms have an explicit
minus sign.

Trigonometric functions of products containing an explicit
imaginary factor ``I`` evaluate to hyperbolic functions and vice versa.



References
==========

http://code.google.com/p/sympycore/wiki/ExtendedNumbers
