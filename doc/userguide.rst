.. -*- rest -*-
.. To verify examples, use command ``python run_doctest.py``
.. To produce HTML file, use command ``rst2html userguide.rst html/userguide.html``
.. To produce PDF file, use command ``rst2latex userguide.rst userguide.tex; pdflatex userguide.tex``

=====================
SympyCore Users Guide
=====================

:Authors:
  `Pearu Peterson <pearu.peterson@gmail.com>`_

:Created:
  January 2008


.. contents::

Introduction
============

The aim of the SympyCore project is to develop a robust, consistent,
and easy to extend Computer Algebra System model for Python.

SympyCore projects home page is http://sympycore.googlecode.com/.

Editorial notes:
- This document is written in `reStructuredText <http://docutils.sourceforge.net/rst.html>`_ format.


Getting Started
===============

To use SympyCore from Python, one needs to import the ``sympycore`` package::

>>> from sympycore import *

The ``sympycore`` package provides ``Symbol`` and ``Number`` functions to
construct symbolic objects and numbers. By default, the symbolic
objects are the elements of ``Calculus`` algebra -- a commutative
ring of symbolic expressions where exponent algebra is also ``Calculus``
algebra.

>>> x = Symbol('x')
>>> n = Number(2,5)
>>> x+n
Calculus('x + 2/5')
>>> x,y,v,w=map(Symbol,'xyvw')

To construct expression from a string, use the corresponding algebra
class, for example,

>>> Calculus('x+y+1/4 + x**2')+x
Calculus('y + x**2 + 1/4 + 2*x')

XXX: need more examples on elementaty operations.


The CAS model
=============

Symbolic expressions represent mathematical concepts like numbers,
constants, variables, functions, operators, and various relations
between them. Symbolic objects, on the other hand, represent symbolic
expressions in a running computer program. The aim of a Computer
Algebra System (CAS) is to provide methods to manipulate symbolic
objects and by that manipulate symbolic expressions. These
manipulations of symbolic expressions have mathematical meaning when
the methods are consistent with the rules and theories from
mathematics.

There are many possible ways to represent a mathematical concept as a
structure of a computer program. SympyCore mimics mathematical
concepts via implementing the corresponding algebra and algebraic
operations in a class, say Algebra, that is derived from the
BasicAlgebra class. So, a symbolic object is an instance of the
Algebra class. This instance contains information about the
mathematical operator that when applied to operands forms the
corresponding symbolic object. The operator and operands of the given
symbolic object can be accessed via atrributes ``func`` and
``args``. The value of ``func`` is a callable object and ``args`` is a
sequence of symbolic objects. So, if ``A`` is a ``Algebra`` instance
then::

  <symbolic object> = A.func(*A.args)

The actual value of ``func`` is defined by the ``Algebra`` class. For
example, in the case of calculus algebra class ``Calculus``, the
``func`` value can be ``Add``, ``Mul``, ``Pow``, ``sin``, ``log``,
etc. If the symbolic object represents a symbol (eg a variable) or a
number of the algebra then ``func`` contains a callable that returns the
symbolic object (the ``args`` in this case will be an empty sequence).

The symbolic objects representing symbols and numbers can be
constructed via the ``Symbol`` and ``Number`` functions. Such symbolic
objects are called atomic.  One should note that functions ``Add``,
``Mul``, ``Pow``, ``Symbol``, ``Number``, etc are always specific to
the given algebra (in fact, they are defined as classmethods of the
corresponding algebra class).

While most of the algebra operators assume symbolic objects as their
operands then ``Symbol`` and ``Number`` functions may take various
Python objects as arguments. For example, the argument to
``Calculus.Symbol`` can be any python object that is immutable (this
requirement comes from the fact terms of sums and factors of products
are internally saved as Python dictionary keys), and the arguments to
``Calculus.Number`` can be Python number types such as ``int``,
``long``, ``float``, ``complex`` as well as ``Fraction``, ``Float``,
``Complex`` instances (these are defined in ``sympycore.arithmetic``
package).

One can construct symbolic objects from Python strings using them as
single arguments to algebra class constructor. For example,

>>> Calculus('a-3/4+b**2')
Calculus('a + b**2 - 3/4')
>>> Calculus('a-3/4+b**2').func
<bound method BasicType.Add of <class 'sympycore.calculus.algebra.Calculus'>>
>>> Calculus('a-3/4+b**2').args
[Calculus('a'), Calculus('-3/4'), Calculus('b**2')]

Package structure 
=================

SympyCore project provides a python package ``sympycore`` that consists of
several modules and subpackages:

1. ``core.py`` - provides a base class ``Basic`` to all symbolic
   objects. Note that almost any (hashable) python object can be used
   as an operand to algebraic operations (assuming the corresponding
   algebra class accepts it) and hence it is not always necessary to
   derive classes defining mathematical from ``Basic``. Only classes
   that could be used by other parts of the ``sympycore`` should be
   derived from ``Basic``. In such cases, these classes are available
   via ``classes`` holder (also defined in ``core.py``). For example,

   >>> from sympycore.core import classes
   >>> classes.Calculus
   <class 'sympycore.calculus.algebra.Calculus'>
   >>> classes.Unit
   <class 'sympycore.physics.units.Unit'>
   >>> classes.CommutativeRingWithPairs
   <class 'sympycore.basealgebra.pairs.CommutativeRingWithPairs'>
  
#. ``arithmetic/`` - provides ``Fraction``, ``Float``, ``Complex``
   classes that represent fractions, multiprecision floating point
   numbers, and complex numbers with rational parts. This package also
   defines symbols like ``oo``, ``zoo``, ``undefined`` that extend the
   number sets with infinities and undefined symbols (eg ``0/0 ->
   undefined``) to make the number sets closed with respect to all
   algebraic operations: ``+``, ``-``, ``*``, ``/``, ``**``. For more
   information about the package, see [section on number theory
   support].

#. ``basealgebra/`` - provides abstract base classes representing
   algebras: ``BasicAlgebra``, ``CommutativeRing``, etc, and base
   classes for algebras with implementations: ``Primitive``,
   ``CommutativeRingWithPairs``, etc.

#. ``calculus/`` - provides class ``Calculus`` that represents the
   algebra of symbolic expressions. The ``Calculus`` class defines the
   default algebra in ``sympycore``. For more information, see
   [section on calculus].  ``calculus/functions/`` - provides symbolic
   functions like ``exp``, ``log``, ``sin``, ``cos``, ``tan``,
   ``cot``, ``sqrt``, ...

#. ``physics/`` - provides class ``Unit`` that represents the algebra
   of symbolic expressions of physical quantities. For more
   information, see [section on physics].

#. ``polynomials/`` - provides classes ``Polynomial``,
   ``UnivariatePolynomial``, ``MultivariatePolynomial`` to represent
   the algebras of polynomials with symbols, univariate polynomials in
   (coefficient:exponent) form, and multivariate polynomials in
   (coefficients:exponents) form, respectively. For more information,
   see [section on polynomials].


Basic methods
=============

In ``sympycore`` all symbolic objects are assumed to be immutable. So, the
manipulation of symbolic objects means creating new symbolic objects
from the parts of existing ones.

There are many methods that can be used to retrive information and
subexpressions from a symbolic object. The most generic method is to
use attribute pair of ``func`` and ``args`` as described
above. However, many such methods are also algebra specific, for
example, classes of commutative rings have methods like
``as_Add_args``, ``as_Mul_args``, etc for retriving the operands of
operations and ``Add``, ``Mul``, etc for constructing new symbolic
objects representing addition, multiplication, etc operations. For
more information about such methods, see sections describing the
particular algebra classes. 


Output methods
--------------

``str(<symbolic object>)``
  return a nice string representation of the symbolic object. For example,

  >>> expr = Calculus('-x + 2')
  >>> str(expr)
  '2 - x'

``repr(<symbolic object>)``
  return a string representation of the symbolic object that can be
  used to reproduce an equal object:

  >>> expr=Calculus('-x+2')
  >>> repr(expr)
  "Calculus('2 - x')"

``<symbolic object>.as_tree()``
  return a tree string representation of the symbolic object. For example,

  >>> expr = Calculus('-x + 2+y**3')
  >>> print expr.as_tree()
  Calculus:
  ADD[
    -1:SYMBOL[x]
    1:MUL[
    1:  3:SYMBOL[y]
    1:]
    2:NUMBER[1]
  ]

  where the first line shows the name of a algebra class following the
  content of the symbolic object in tree form. Note how are
  represented the coefficients and exponents of the example
  subexpressions.

Conversation methods
--------------------

``<symbolic object>.as_primitive()``
  return symbolic object as an instance of ``PrimitiveAlgebra`` class. All
  algebra classes must implement ``as_primitive`` method as this allows
  converting symbolic objects from one algebra to another that is
  compatible with respect to algebraic operations. Also, producing the
  string representations of symbolic objects is done via converting
  them to PrimitiveAlgebra that implements the corresponding printing
  method. For example,

  >>> expr
  Calculus('2 + y**3 - x')
  >>> expr.as_primitive()
  PrimitiveAlgebra('2 + y**3 - x')

``<symbolic object>.as_algebra(<algebra class>)``
  return symbolic object as an instance of given algebra class. The
  transformation is done by first converting the symbolic object to
  ``PrimitiveAlgebra`` instance which in turn is converted to the instance
  of targer algebra class by executing the corresponding target
  algebra operators on operands. For example,

  >>> expr = Calculus('-x + 2')
  >>> print expr.as_tree()
  Calculus:
  ADD[
    -1:SYMBOL[x]
    2:NUMBER[1]
  ]
  >>> print expr.as_algebra(PrimitiveAlgebra).as_tree()
  PrimitiveAlgebra:
  ADD[
    NEG[
      SYMBOL[x]
    ]
    NUMBER[2]
  ]
  >>> print expr.as_algebra(CommutativeRingWithPairs).as_tree()
  CommutativeRingWithPairs:
  ADD[
    -1:SYMBOL[x]
    2:NUMBER[1]
  ]

Substitution of expressions
---------------------------

``<symbolic object>.subs(<sub-expr>, <new-expr>)``
  return a copy of ``<symbolic object>`` with all occurances of
  ``<sub-expr>`` replaced with ``<new-expr>``. For example,

  >>> expr = Calculus('-x + 2+y**3')
  >>> expr
  Calculus('2 + y**3 - x')
  >>> expr.subs('y', '2*z')
  Calculus('2 + 8*z**3 - x')

``<symbolic object>.subs([(<subexpr1>, <newexpr1>), (<subexpr2>, <newexpr2>), ...])``
  is equivalent to ``<symbolic object>.subs(<subexp1>,
  <newexpr1>).subs(<subexpr2>, <newexpr2>).subs``. For example,

  >>> expr
  Calculus('2 + y**3 - x')
  >>> expr.subs([('y', '2*z'),('z', 2)])
  Calculus('66 - x')

Pattern matching
----------------

``<symbolic object>.match(<pattern-expr> [, <wildcard1>, <wildcard2> ...])``
  check if the give symbolic object matches given pattern. Pattern
  expression may contain wild symbols that match arbitrary
  expressions, the ``wildcard`` must be then the corresponding
  symbol. Wild symbols can be matched also conditionally, then the
  ``<wildcard>`` argument must be a tuple ``(<wild-symbol>, <predicate>)``,
  where ``<predicate>`` is a single-argument function returning ``True`` if
  wild symbol matches the expression in argument. If the match is not
  found then the method returns. Otherwise it will return a dictionary
  object such that the following condition holds::

    pattern.subs(expr.match(pattern, ...).items()) == expr

  For example,

  >>> expr = 3*x + 4*y
  >>> pattern = v*x + w*y
  >>> d = expr.match(pattern, v, w)
  >>> print 'v=',d.get(v)
  v= 3
  >>> print 'w=',d.get(w)
  w= 4
  >>> pattern.subs(d.items())==expr
  True

Checking for atomic objects
---------------------------

A symbolic object is atomic if ``<symbolic object>.args == ()``.

``<symbolic object>.symbols``
  is a property that holds a set of all atomic symbols in the given
  symbolic expression.

``<symbolic object>.has(<symbol>)``
  returns ``True`` if the symbolic expression contains ``<symbol>``.

Primitive algebra
=================

XXX: explain ``PrimitiveAlgebra`` class.

Commutative ring
================

In SympyCore a commutative ring is represented by an abstract class
``CommutativeRing``.  The ``CommutativeRing`` class defines support
for addition, substraction, multiplication, division, and
exponentiation operations.

Operations
----------

Classes deriving from ``CommutativeRing`` must define a number of
method pairs ``(Operation, as_Operation_args)`` that satisfy the
following condition::

  cls.Operation(*obj.as_Operation_args()) == obj

Here ``Operation`` can be ``Add``, ``Mul``, ``Terms``, ``Factors``,
``Pow``, ``Log``. For example,

>>> print map(str, (2*x+y).as_Add_args())
['y', '2*x']
>>> print map(str, (2*x+y).as_Mul_args())
['y + 2*x']
>>> print map(str, (2*x+y).as_Pow_args())
['y + 2*x', '1']
>>> print (2*x+y).as_Terms_args()
[(Calculus('y'), 1), (Calculus('x'), 2)]


Differentation
--------------

``<symbolic object>.diff(*symbols)``
  return a derivative of symbolic expression with respect to given
  symbols. The diff methods argument can also be a positive integer
  after some symbol argument. Then the derivative is computed given
  number of times with respect to the last symbol.
  For example,

  >>> print sin(x*y).diff(x)
  y*cos(x*y)
  >>> print sin(x*y).diff(x,y)
  cos(x*y) - x*y*sin(x*y)
  >>> print sin(x*y).diff(x,4)
  sin(x*y)*y**4

Integration
-----------

``<symbolic object>.integrate(<symbol>, integrator=None)``
  return an antiderivative of a symbolic expression with respect to
  ``<symbol>``.
  For example,
  
  >>> from sympycore import *
  >>> print (x**2 + x*y).integrate(x)
  1/2*y*x**2 + 1/3*x**3

Commutative ring implementation
===============================

Commutative ring operations are implemented in the class
``CommutativeRingWithPairs`` (derived from ``CommutativeRing``).
