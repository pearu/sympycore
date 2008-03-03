.. -*- rest -*-

======================
Structure of SympyCore
======================

:Author: Pearu Peterson
:Created: March 2008

Basic principles
================

Any symbolic expression can be expressed as a pair of *expression
head* and *expression data*. The expression head contains information
how expression data should be interpreted.

To add a mathematical meaning to a symbolic expression, one needs to
specify to what kind of *algebraic structure* the possible values of
symbolic expression belong to. The algebraic structure defines how the
symbolic expressions are combined when used in an operation defined by
the specified algebraic structure.

Implementation of principles
============================

In sympycore, a symbolic expression is defined as an instance of a
``Pair`` class (the actual implementation of any code that follows
below may be different because of efficiency, here we just explain the
ideas)::

  class Pair(object):

      def __init__(self, head, data):
          self.head = head
	  self.data = data

In a way, the ``Pair`` class represents an algebraic structure with no
mathematical properties - it just holds some *head* and some *data*.

To define a richer algebraic structures that may be define operations
between its elements, one can derive a class from a ``Pair`` that
implements the correspondig operation as an method, for instance::

  class AlgebraicStructure(Pair):
      
       def operation(self, other):
           ...
           return result

For example. a commutative ring element can be represented as an
instance of the following class::

  class CommutativeRing(Pair):
 
       def __add__(self, other):
           return CommutativeRing('+', (self, other))

       __radd__ = __add__ # addition is commutative

       def __mul__(self, other):
           return CommutativeRing('*', (self, other))

For convenience, some additional methods can be provided to
simplify creating instances of ``Pair`` based classes. For example,
to define a symbol of a commutative ring::

  def Symbol(name):
      return CommutativeRing('S', name)

To define a number of a commutative ring::

  def Number(value):
      return CommutativeRing('N', value)

To define applied function with a value in a commutative ring::

  def F(x):
      "Return the value of function F"
      return <result>

  def Apply(function, argument):
      return CommutativeRing(function, argument)

Since sympycore defines classes representing different algebraic
structures, the functions above are usually implemented as Python
class methods of the corresponding algebra classes.

