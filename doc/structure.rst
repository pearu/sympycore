.. -*- rest -*-

======================
Structure of SympyCore
======================

:Author: Pearu Peterson
:Created: March 2008

.. section-numbering::

.. sidebar:: Table of contents

    .. contents::
        :depth: 2
        :local:

Basic principles
================

Any symbolic expression can be expressed as a pair of *expression
head* and *expression data*. The expression head contains information
how expression data should be interpreted.

To add a mathematical meaning to a symbolic expression, one needs to
specify to what *algebraic structure* possible values of a symbolic
expression belong to. The algebraic structure defines how symbolic
expressions are combined when used in an operation defined by the
given algebraic structure.

In the following we call algebraic structures as algebras for brevity.

Implementation of principles
============================

In sympycore, a symbolic expression is defined as an instance of a
``Expr`` class (the actual implementation of any code that follows
below may differ because of efficiency, here we just explain some
basic ideas)::

  class Expr(object):

      def __init__(self, head, data):
          self.pair = (head, data)
          self.head = head
	  self.data = data

In a way, the ``Expr`` class represents an algebra with no
mathematical properties - it just holds some *head* and some *data*.

To define an algebra with additional features such as opertions
between its elements, a Python class is derived from the ``Expr``
class:

  class AlgebraicStructure(Expr):
      
       def operation(self, other):
           ...
           return result

where the operation result is implemented in a method ``operation``.

For example. a commutative ring element can be represented as an
instance of the following class::

  class CommutativeRing(Expr):
 
       def __add__(self, other):
           return CommutativeRing('+', (self, other))

       __radd__ = __add__ # addition is commutative

       def __mul__(self, other):
           return CommutativeRing('*', (self, other))

For convenience, some additional methods can be provided to simplify
creating instances of the ``Expr`` based classes. For example, to
define a symbol of a commutative ring::

  def Symbol(name):
      return CommutativeRing('S', name)

To define a number of a commutative ring::

  def Number(value):
      return CommutativeRing('N', value)

To define an applied unary function with a value in a commutative
ring::

  def F(x):
      "Return the value of function F"
      return <result>

  def Apply(function, argument):
      return CommutativeRing(function, argument)

Since sympycore defines many classes representing different algebras,
the functions above are usually implemented as Python class methods of
the corresponding algebra classes. Also, the used ``head`` parts may
be changed to anything more appropiate.

Low-level numbers
=================

Many algebras define numbers as generalized repetitions of the algebra
unit element. Sympycore uses and defines the following number types
for purely numerical task, i.e. both operands and operation results
are numbers):

+-----------+----------------------------------------------------+
| int, long | integers of arbitrary size                         |
+-----------+----------------------------------------------------+
| mpq       | fractions                                          |
+-----------+----------------------------------------------------+
| mpf       | arbitrary precision floating point numbers         |
+-----------+----------------------------------------------------+
| mpqc      | complex numbers with rational parts                |
+-----------+----------------------------------------------------+
| mpc       | arbitrary precision complex floating point numbers |
+-----------+----------------------------------------------------+

Python ``float`` and ``complex`` instances are converted to ``mpf``
and ``mpc`` instances, respectively.

These number types are called "low-level" numbers because some of
their properties may be unusual for generic numbers but these
properties are introduced to improve the efficiency of number
operations.

For example, ``mpq`` number is assumed to hold a normalized rational
number that is not integer.  Operation between ``mpq`` instances that
would produce integer result, will return ``int`` (or ``long``)
instance. Similarly, the real valued result of an operation between
complex numbers ``mpqc`` (or ``mpc``) will be an instance of ``int``
or ``long`` or ``mpq`` (or ``mpf``) type.


Various representations
=======================

Consider the following symbolic expression::

  x**3 + 2*y

This expression may have at least three different representations::

  Ring(head='ADD',   data=(x**3, 2*y))
  Ring(head='TERMS', data=((x**3, 1), (y, 2)))
  Ring(head=(x,y),   data=(((3,0), 1), ((0,1), 2)))

where the data structures are interpreted as follows::

  (x**3) + (2*y)
  (x**3) * 1 + y * 2
  x**3 * y**0 * 1 + x**0 * y**1 * 2

respectively.

In general, there is no preferred representation for symbolic
expressions, each have their pros and cons depending on the tasks.


Verbatim algebra
================

Sympycore defines ``Verbatim`` class that represents verbatim algebra.
Verbatim algebra contains expressions in unevaluated form.

