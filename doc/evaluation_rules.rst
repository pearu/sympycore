.. -*- rest -*-

==================================================
Automatic evaluation rules of symbolic expressions
==================================================

:Authors:
  Pearu Peterson <pearu.peterson AT gmail DOT com>

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

Expressions containing extended numbers require special rules as
distributivity laws are not valid for extended numbers. Note that the
distributivity law is not strictly valid also for operations with
floating point numbers.

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
  may not be equivalent to *mathematical equality*.

  For example::

    x + x -> 2*x
    x * x -> x**2


.. admonition:: Rule 4: operations with zero.

  Multiplication by zero is zero only when a non-zero operand does not
  contain extended numbers explicitly.

  For example::

    0 * x -> 0
    0 * (x + oo) -> 0 * (x + oo)

  Exponentiation by zero results one.

  For example::

    x**0 -> 1
    oo**0 -> 1

.. admonition:: Rule 5: distributivity

  `Distributivity`__ law of multiplication over addition is applied
  only when a sum is multiplied by a number that is not extended
  number.

  For example::

    3*(x + y) -> 3*x + 3*y
    (3 + x)/2 -> 3/2 + 1/2*x
    oo*(2 + x) -> oo*(2 + x)

__ http://en.wikipedia.org/wiki/Distributivity


Operations with numbers
-----------------------

Addition and multiplication operations with numbers always result in a number.

XXX: add rules for exponentiation with integers, fractions.

Operations with extended numbers
--------------------------------

http://code.google.com/p/sympycore/wiki/ExtendedNumbers


Function evaluations
====================

XXX: explain the rules for evaluating elementary functions such as
``sin``, ``cos``, etc.