.. -*- rest -*-

======================
Structure of SympyCore
======================

:Author: Pearu Peterson
:Website: http://sympycore.googlecode.com
:Created: March 2008

.. section-numbering::

.. sidebar:: Table of contents

    .. contents::
        :depth: 2
        :local:

Introduction
============

This document gives an overview of data types that are used in
``sympycore`` to represent symbolic expressions. First, the fundametal
idea of defining a Python type ``Expr``, that holds a pair of Python
objects, is explained. Then ``Expr`` is used to implement classes that
represent different mathematical concepts --- the actual class
structure of ``sympycore`` is outlined. Subsequent sections document
the features of ``sympycore`` classes in detail.

Fundamental idea
================

The fundamental idea behind the implementation of ``sympycore``
classes is based on the following assertions: 

* Any symbolic expression can be expressed as a pair of *expression
  head* and *expression data*. The *expression head* contains
  information how the *expression data* is interpreted. The head and
  data pair will be saved as attributes of ``Expr`` class.

* The mathematical meaning of symbolic expressions depends on the
  assumption to what *algebraic structure* the possible values of a
  symbolic expression belong. The specified algebraic structure
  defines the rules for how the symbolic expressions can be combined
  in algebraic operations. These rules are implemented in classes
  derived from the ``Expr`` class.

In the following we call a algebraic structure as an algebra for
brevity.

Implementation of principles
----------------------------

.. warning::

  The Python code fragments shown in this section are presented only
  for illustration purposes. The ``sympycore`` may use slightly
  different implementation (explained in the following sections) that
  gives a better performance. However, the basic ideas remain the
  same.

In ``sympycore``, any symbolic expression is defined as an instance of a
``Expr`` class (or one of its subclasses)::

  class Expr(object):

      def __init__(self, head, data):
          self.pair = (head, data)
          self.head = head
	  self.data = data

In a way, the ``Expr`` class represents an algebra with no
mathematical properties - it just holds some *head* and some *data*.

To define an algebra with additional properties that define opertions
between its elements, a Python class is derived from the ``Expr``
class::

  class Algebra(Expr):
      
       def operation(self, other):
           ...
           return result

where an operation between algerba elements is implemented in a method
``operation``.

For example. a commutative ring element can be represented as an
instance of the following class::

  class CommutativeRing(Expr):
 
       def __add__(self, other):
           return CommutativeRing('+', (self, other))

       __radd__ = __add__ # addition is commutative

       def __mul__(self, other):
           return CommutativeRing('*', (self, other))

Constructing instances
----------------------

For convenience, one can provide additional methods or functions that
will simplify creating instances of the ``Expr`` based classes. For
example, to construct a symbol of a commutative ring, one can define
the following function::

  def Symbol(name):
      return CommutativeRing('S', name)

To construct a number of a commutative ring, one can define::

  def Number(value):
      return CommutativeRing('N', value)

To construct an applied unary function with a value in a commutative
ring, one can define::

  def F(x):
      "Return the value of function F"
      return <result>

  def Apply(function, argument):
      return CommutativeRing(function, argument)

Since ``sympycore`` defines many classes representing different
algebras, the functions above are usually implemented as Python
``classmethod``'s of the corresponding algebra classes. Also, the used
``head`` parts may be changed to anything more appropiate.

Various representations
-----------------------

Note that a fixed symbolic expression may have different but
mathematically equivalent representations. For example, consider the
following symbolic expression::

  x**3 + 2*y

This expression may have at least three different representations::

  Ring(head='ADD',   data=(x**3, 2*y))
  Ring(head='TERMS', data=((x**3, 1), (y, 2)))
  Ring(head=(x,y),   data=(((3,0), 1), ((0,1), 2)))

where the ``data`` structures are interpreted as follows::

  (x**3) + (2*y)
  (x**3) * 1 + y * 2
  x**3 * y**0 * 1 + x**0 * y**1 * 2

respectively.

In general, there is no preferred representation for a symbolic
expression, each representation has its pros and cons depending on
applications.

Classes in Sympycore
====================

The following diagram summarizes the class structure of ``sympycore``::

  object
    Expr
      Algebra
        Verbatim
        CommutativeRing
          CollectingField
            Calculus
            Unit
        PolynomialRing[<variables>, <coefficient ring>]
        MatrixRing[<shape>, <element ring>]

Low-level numbers
-----------------

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


Verbatim algebra
----------------

Sympycore defines ``Verbatim`` class that represents verbatim algebra.
Verbatim algebra contains expressions in unevaluated form.

