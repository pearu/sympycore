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
  head* and *expression data*. The *expression head* defines
  how the *expression data* is interpreted. 

* Symbolic expression represents an unevaluated element of an
  *algebraic structure* under consideration. In the following we call
  a algebraic structure as an algebra for brevity.  An algebra is
  represented by a Python class (an *algebra class*) and the
  instances of this class represent symbolic expressions.

* An algebra may define *operations* between its elements
  to form *composite* symbolic expressions. Each operation is
  represented by the corresponding expression head. Since the same
  operation may be defined for different algebras then the
  same expression head (defining evaluation rules and other methods)
  is used for symbolic expressions of different algebra classes.

* Symbolic expressions can be constructed directly from expression
  head and data parts, or indirectly from performing operations with
  other symbolic operations. Direct construction, ``<Algebra
  class>(<head>, <data>)``, results an unevaluated symbolic expression
  instance while indirect construction, ``<expr1> <operation>
  <expr2>``, evaluates the symbolic expression instance to a canonical
  form. Direct construction does not have any argument validity checks for
  efficiency and should be used internally by evaluation methods.

Implementation of principles
----------------------------

The assertions of the fundamental idea is implemented as follows:

* To hold the head and data parts of symbolic expressions, a class
  ``Expr`` is defined that instances will have an attribute ``pair``
  holding the head and data pair.  In a way, the ``Expr`` class
  represents an algebra with no mathematical properties - it just
  holds some *head* and some *data*.

* To define the algebra operations for symbolic expressions,
  subclasses of ``Expr`` implement the corresponding methods.

* The head parts of symbolic expressions are instances of
  ``sympycore.heads.Head`` classes that implement the evaluation rules
  of the corresponding algebra operations. Since head instances are
  singletons then Python ``is`` operation can be used for comparing
  expression heads.

The following section gives an overview of pre-defined expression heads.

Pre-defined expression heads
============================

All head instances are available as attributes to the holder object
``sympycore.core.heads``.

Atomic heads
------------

SYMBOL

  A symbolic expression with ``SYMBOL`` head represents any element of
  the algebra. The corresponding expression data part can be any
  Python object (usually it is a string). ``SYMBOL`` head defines no
  interpretation rules for the data.

NUMBER

  A symbolic expression with ``NUMBER`` head represents a generalized
  repetition operation of algebra elements. The data part can be any
  Python object that supports Python numbers protocol, that is, the
  objects type must define all basic arithmetic operations. Usually
  the data part contains number instances such as integers, floats,
  complex numbers or numbers defined by the
  ``sympycore.arithmetic.numbers`` module: rational numbers and
  arbitrary precision floating point numbers. The data part can also
  contain symbolic expression of some other algebra (*coefficient
  algebra*), then such expressions are considered as coefficients that
  always commute with the elements of the given algebra.

Arithmetic heads
----------------

POS

  A symbolic expression with ``POS`` head represents unevaluated unary
  positive sign operation. The data part must be a symbolic expression.
  For example, ``Algebra(POS, a)`` represents ``+a``.
  

NEG

  A symbolic expression with ``NEG`` head represents unevaluated unary
  negative sign operation. The data part must be a symbolic
  expression.
  For example, ``Algebra(NEG, a)`` represents ``-a``.

ADD

  A symbolic expression with ``ADD`` head represents unevaluated n-ary
  addition operation. The data part must be a Python list of symbolic
  expression. For example, ``Algebra(ADD, [a, b, c])`` represents ``a
  + b + c``.

SUB

  A symbolic expression with ``SUB`` head represents unevaluated n-ary
  subtraction operation. The data part must be a Python list of symbolic
  expression. For example, ``Algebra(SUB, [a, b, c])`` represents ``a
  - b - c``.

MUL

  A symbolic expression with ``MUL`` head represents unevaluated n-ary
  multiplication operation. The data part must be a Python list of symbolic
  expression. For example, ``Algebra(MUL, [a, b, c])`` represents ``a
  * b * c``.

NCMUL

  A symbolic expression with ``NCMUL`` head represents unevaluated n-ary
  non-commutative multiplication operation. The data part must be a
  Python list of symbolic expression that are not numbers. For
  example, ``Algebra(NCMUL, [a, b, c])`` represents ``a * b * c``.

DIV

  A symbolic expression with ``DIV`` head represents unevaluated n-ary
  division operation. The data part must be a Python list of symbolic
  expression. For example, ``Algebra(DIV, [a, b, c])`` represents ``a
  / b / c``.

POW

  A symbolic expression with ``POW`` head represents unevaluated
  exponentiation operation. The data part must be a Python 2-tuple of
  symbolic expressions representing base and exponent parts. For
  example, ``Algebra(POW, (a, b))`` represents ``a ** b``.

TERM_COEFF_DICT

  A symbolic expression with ``TERM_COEFF_DICT`` head represents
  unevaluated unordered addition operation. The data part must be a
  Python dictionary of symbolic expression and coefficient pairs.
  Coefficients must support number operations.
  For example, ``Algebra(TERM_COEFF_DICT, {a:2, b:1})`` represents
  ``2*a + b``.

BASE_EXP_DICT

  A symbolic expression with ``BASE_EXP_DICT`` head represents
  unevaluated unordered multiplication operation. The data part must be a
  Python dictionary of symbolic expression and exponent pairs.
  Exponent objects must support number operations.
  For example, ``Algebra(BASE_EXP_DICT, {a:2, b:1})`` represents
  ``a**2 * b``.

EXP_COEFF_DICT

  A symbolic expression with ``EXP_COEFF_DICT`` head represents
  unevaluated unordered polynomial addition operation. The data part
  must be a ``Pair`` instance containing a tuple of variable
  expressions and a dictionary of integer exponents and coefficient
  pairs.  Coefficient objects must support number operations. For
  example, ``Algbera(EXP_COEFF_DICT, Pair((x, sin(x)), {(0,1):2,
  (2,3):5}))`` represents ``2*sin(x) + 5*x**2*sin(x)**3``.

LSHIFT, RSHIFT

  Symbolic expressions with ``LSHIFT`` and ``RSHIFT`` heads represent
  unevaluated n-ary *left-shift* and *right-shift* operations. The
  data part must be a list of symbolic expressions.
  For example, ``Algebra(LSHIFT, [a, b, c])`` represents ``a<<b<<c``.

INVERT, BOR, BXOR, BAND, FLOORDIV

  Binary operations.

Comments
++++++++

It is possible to represent arithmetic operations with a subset of the
above defined heads. For example, using only the heads ``ADD``,
``MUL``, ``POW``, or alternatively, ``TERM_COEFF_DICT``,
``BASE_EXP_DICT`` heads. Symbolic expressions with heads ``POS``,
``NEG``, ``SUB``, and ``DIV`` can be represented as expressions with
one or other group of heads.

Logic heads
-----------

NOT

  A symbolic expression with ``NOT`` head represents unevaluated unary
  logical *negation* operation. The data part must be a symbolic
  expression that is an instance of a ``Logic`` algebra class. For
  example, ``Logic(NOT, a)`` represents ``not a``.

OR

  A symbolic expression with ``OR`` head represents unevaluated n-ary
  logical *disjunction* operation. The data part must be a list of
  ``Logic`` instances. For example, ``Logic(OR, [a, b, c])``
  represents ``a or b or c``.

XOR

  A symbolic expression with ``XOR`` head represents unevaluated n-ary
  logical *exclusive disjunction* operation. The data part must be a
  list of ``Logic`` instances. For example, ``Logic(XOR, [a, b, c])``
  represents ``a xor b xor c``.

AND

  A symbolic expression with ``AND`` head represents unevaluated n-ary
  logical *conjunction* operation. The data part must be a list of
  ``Logic`` instances. For example, ``Logic(AND, [a, b, c])``
  represents ``a and b and c``.

IMPLIES

  A symbolic expression with ``IMPLIES`` head represents unevaluated
  binary logical *conditional* operation (if-then). The data part must
  be a 2-tuple of ``Logic`` instances. For example, ``Logic(IMPLIES,
  (a, b))`` represents ``a implies b``.

EQUIV

  A symbolic expression with ``EQUIV`` head represents unevaluated
  binary logical *biconditional* operation (if-and-only-if). The data part must
  be a 2-tuple of ``Logic`` instances. For example, ``Logic(EQUIV,
  (a, b))`` represents ``a equiv b``.

Relational heads
----------------

The symbolic expressions of relational operations are instances of the
``Logic`` algebra class. The data parts of relational operations are Python
2-tuples of symbolic expressions.

EQ, NE, LT, LE, GT, GE

  Symbolic expressions with ``EQ``, ``NE``, ``LT``, ``LE``, ``GT``, or
  ``GE`` heads represent unevaluated binary relational operations
  *equal*, *not-equal*, *less-than*, *less-equal*, *greater-than*, or
  *greater-equal*, respectively.  For example, ``Logic(LT, (a, b))``
  represents ``a < b``.

IN, NOTIN

  Symbolic expressions with ``IN`` or ``NOTIN`` heads represent
  unevaluated binary relational operations *in* or *not-in*,
  respectively. The left-hand-side operand should be an element of the
  right-hand-side operand which is a ``Set`` instance.

IS, ISNOT

  Symbolic expressions with ``IN`` or ``NOTIN`` heads represent
  unevaluated binary relational operations *in* or *not-in*,
  respectively.

Container heads
---------------

TUPLE, LIST, DICT

  Symbolic expressions with ``TUPLE``, ``LIST``, or ``DICT`` heads
  represent unevaluated tuple, list, or dict expressions,
  respectively. The data parts must be Python tuple, list, or dict
  instances, respectively, of symbolic expressions. For example,
  ``Algebra(TUPLE, (a, b, c))`` represents ``(a,b,c)``.

Special heads
-------------

CALLABLE

  A symbolic expression with ``CALLABLE`` head represents an element
  of functions algebra. The data part must be Python callable object
  that returns a symbolic expression representing an element of
  functions values algebra. Symbolic expressions with ``CALLABLE``
  head are usually used in connection with ``APPLY`` head to represent
  unevaluated applied function expressions. In fact, if the callable
  data part cannot evaluate its arguments then it should return 
  ``Algebra(APPLY, (FunctionAlgebra(CALLABLE, <callable>), <argument1>, ...))``.

SPECIAL

  A symbolic expression with ``SPECIAL`` head does not represent any
  element of the given algebra. That said, the data part can hold any
  Python object. In practice, data can be Python ``Ellipsis`` or
  ``None`` objects. Also, data can hold extended number instances
  (e.g. infinities) of the given algebra.

APPLY

  A symbolic expression with ``APPLY`` head represents an unevaluated
  applied function expression. The data part must be a tuple of
  symbolic expressions where the first element belongs to functions
  algebra and the rest of the elements are function arguments.
  For example, ``Algebra(APPLY, (f, x, y))`` represents ``f(x, y)``.

KWARG

  A symbolic expression with ``KWARG`` head represents a keyword
  argument to symbolic functions. The data part must be a 2-tuple of
  symbolic expressions. For example, ``Algebra(KWARG, (a,b))``
  represents ``a=b``.

SUBSCRIPT

  A symbolic expression with ``SUBSCRIPT`` head represents an
  unevaluated applied subscript expression. The data part must be a
  tuple of symbolic expressions. For example, ``Algebra(SUBSCRIPT,
  (f,i,j))`` represents ``f[i,j]``.

SLICE

  A symbolic expression with ``SLICE`` head represents an
  unevaluated slice expression. The data part must be a
  3-tuple of symbolic expressions. For example, ``Algebra(SLICE,
  (i:Algebra(SPECIAL, None):k))`` represents ``i::k``.

ATTR

  A symbolic expression with ``SUBSCRIPT`` head represents an
  unevaluated applied attribute expression. The data part must be a
  2-tuple of symbolic expressions. For example, ``Algebra(ATTR, (f,
  a))`` represents ``f.a``.

LAMBDA

  A symbolic expression with ``SUBSCRIPT`` head represents a
  lambda expression. The data part must be a 2-tuple of a tuple
  (lambda arguments) and symbolic expression (lambda body). For
  example, ``Algebra(LAMBDA, ((a,b), c))`` represents ``lambda a, b:
  c``. 

Classes in SympyCore
====================

The following diagram summarizes what classes ``sympycore`` is going
to define::

  object
    Expr
      Pair
      Algebra
        Verbatim
        Logic
	Ring
          CommutativeRing
            Calculus
            Unit
	  Matrix

    Infinity

    tuple
      mpq
    mpqc
    mpf, mpc
    int, long, float, complex

Low-level numbers
-----------------

Many algebras define numbers as generalized repetitions of the algebra
unit element. Sympycore uses and defines the following number types
for purely numerical tasks, i.e. both operands and operation results
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
and ``mpc`` instances, respectively, when used in operations with
symbolic expressions.

These number types are called "low-level" numbers because some of
their properties may be unusual for generic numbers (e.g. mpf is
derived from Python tuple) but these properties are introduced to
improve the efficiency of number operations.

For example, ``mpq`` number is assumed to hold a normalized rational
number that is not integer.  Operations between ``mpq`` instances that
would produce integer result, will return ``int`` (or ``long``)
instance. Similarly, the real valued result of an operation between
complex numbers ``mpqc`` (or ``mpc``) will be an instance of ``int``
or ``long`` or ``mpq`` (or ``mpf``) type.


.. warning::

  THE CONTENT BELOW NEEDS A REVISION.

.. warning::

  The Python code fragments shown in this section are presented only
  for illustration purposes. The ``sympycore`` may use slightly
  different implementation (explained in the following sections) that
  gives a better performance. However, the basic idea remain the same.

In ``sympycore``, any symbolic expression is defined as an instance of a
``Expr`` class (or one of its subclasses)::

  class Expr(object):

      def __init__(self, head, data):
          self.pair = (head, data)

      head = property(lambda self: self.pair[0])
      data = property(lambda self: self.pair[1])



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
``classmethod``-s of the corresponding algebra classes. Also, the
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


Constructing instances
----------------------

There are two types of symbolic expressions: atomic and composites.
Atomic expressions are symbols and numbers. Symbols can be considered
as unspecified numbers. Composite expressions are unevaluated forms of
operators or operations defined between symbolic expressions.

In SympyCore, each algebra class defines classmethods
``Symbol(<obj>)`` and ``Number(<obj>)`` that can be used to construct
atomic expressions. In fact, they will usually return ``<Algebra
class>(SYMBOL, <obj>)`` and ``<Algebra class>(NUMBER, <obj>)``,
respectively. Regarding nubers, it is callers responsibility to ensure
that ``<obj>`` is usable as a number.  Some algebra classes also
define class attributes ``zero`` and ``one`` holding identity numbers
with respect to addition and multiplication operations. In ``Logic``
algebra, these numbers are aliases to ``false`` and ``true`` values,
respecitvely.

Depending on the callers need, there are at least three possibilities
in SympyCore to construct composite expressions:

#. Use ``<Algebra class>(<head>, <data>)`` that will return an algebra
   class instance with given head and data. No evaluation or
   canonization is performed. This construction is usually used by
   low-level methods that must ensure that the data part contains
   proper data, that is, data in a form that the rest of sympycore
   can assume.

#. Use ``<Algebra class>.<Operation>(<operands>)`` class method call
   that will perform basic canonization of the operation applied to
   operands and returns canonized result as an instance of the algebra
   class. This construction is usually used by high-level methods that
   must ensure that operands are instances of operands algebra.

#. Use ``<Operation>(<operands>)`` function call that will convert
   operands to operands algebra instances and then returns the result
   of ``<Algebra class>.<Operation>`` classmethod. This construction
   should be used by end-users.

There exist also some convenience and implementation specific
possibilities to construct expressions:

4. Use ``<Algebra class>.convert(<obj>, typeerror=True)`` to convert
   Python object ``<obj>`` to algebra instance. If conversation is not
   defined then ``TypeError`` is raised by default. When
   ``typeerror=False`` then ``NotImplemented`` is returned instead of
   raising the exception.

#. Use ``<Algebra class>(<obj>)`` that is an alias to ``<Algebra
   class>.convert(<obj>)`` call.

Verbatim algebra
----------------

SympyCore defines ``Verbatim`` class that represents verbatim algebra.
Verbatim algebra contains expressions in unevaluated form. The
verbatim algebra can be used to implement generic methods for
transforming symbolic expressions to strings, or to instances of other
algebras.

Logic algebra
-------------

SympyCore defines ``Logic`` class that represents n-ary predicate
expressions. The following operations are defined by the ``Logic``
class:

#. ``Not(x)`` represents boolean expression ``not x``. Operand algebra
   class is ``Logic``.

#. ``And(x,y,..)`` represents boolean expression ``x and y and ..``.
   Operand algebra class is ``Logic``.

#. ``Or(x,y,..)`` represents boolean expression ``x or y or ..``.
   Operand algebra class is ``Logic``.

#. ``Lt(x, y)`` represents relational expression ``x < y``.
   Operand algebra class is ``Calculus``.

#. ``Le(x, y)`` represents relational expression ``x <= y``.
   Operand algebra class is ``Calculus``.

#. ``Gt(x, y)`` represents relational expression ``x > y``.
   Operand algebra class is ``Calculus``.

#. ``Ge(x, y)`` represents relational expression ``x >= y``.
   Operand algebra class is ``Calculus``.

#. ``Eq(x, y)`` represents relational expression ``x == y``.
   Operand algebra class is ``Calculus``.

#. ``Ne(x, y)`` represents relational expression ``x != y``.
   Operand algebra class is ``Calculus``.

Collecting field
----------------

SympyCore defines ``CollectingField`` class to represent sums and
products in ``{<term>:<coefficent>}`` and ``{<base>:<exponent>}``
forms, respectively. The class name contains prefix "Collecting"
because in operations with ``CollectingField`` instances, equal terms
and equal bases are automatically collected by upgrading the
coefficient and exponent values, respectively.

The following operations are defined by the ``CollectingField`` and
its subclasses ``Calculus``, ``Unit``:

#. ``Add(x, y, ..)`` represents addition ``x + y + ..``.
   Operand algebra class is the same as algebra class.

#. ``Mul(x, y, ..)`` represents multiplication ``x * y * ..``.
   Operand algebra class is the same as algebra class.

#. ``Terms((x,a), (y,b), ..)`` represents a sum ``a*x + b*y + ..``
   where ``x, y, ..`` must be non-numeric instances of the algebra
   class and ``a, b, ..`` are low-level numbers.
 
#. ``Factors((x,a), (y,b), ..)`` represents a product ``x**a * y**b * ..``
   where ``x, y, ..`` must be instances of the algebra
   class and ``a, b, ..`` are either low-level numbers or instances of
   exponent algebra.

#. ``Pow(x, y)`` represents exponentiation ``x ** y`` where ``x`` must
   be instance of the algebra class and ``y`` must be either low-level
   number or an instance of exponent algebra.

#. ``Sub(x, y, ..)`` represents operation ``x - y - ..`` where operands
   must be instances of the algebra class.

#. ``Div(x, y, ..)`` represents operation ``x / y / ..`` where operands
   must be instances of the algebra class.

#. ``Apply(f, (x, y, ..))`` represents unevaluated function call
   ``f(x, y, ..)``.

Defining functions in SympyCore
===============================

In general, unevaluated applied functions in ``sympycore`` are
represented as a pair::

  <Algebra class>(<callable>, <arguments>)

where ``<Algebra class>`` defines an algebra where the function values
belong to, ``<callable>`` is a Python callable object that may define
some basic canonization rules, and ``<arguments>`` is either a tuple
of function arguments or for single argument functions, the argument
itself.

To simplify the infrastructure for handling defined functions, the
defined functions in ``sympycore`` should be defined as classes
derived from ``DefinedFunction`` class (defined in
``sympycore.core``). Such defined functions will be available as
attributes of the ``defined_functions`` holder object, and most
importantly, the expression string parser will recognize symbols with
defined function names as defined functions.

Here follows a typical definition of a defined function ``myfunc`` for
a given ``Algebra`` class::

  class myfunc(DefinedFunction):

      def __new__(cls, *args):
          # perform any canonization of arguments (including
          # converting arguments to operands algebra) and return
          # simplified result. Otherwise,
          return Algebra(cls, args)

How does it work in SympyCore?
==============================

How strings are parsed to expressions?
--------------------------------------

Expressions represent elements of some algebra.  Therefore, to parse a
string and to create an expression from it, one needs to specify to
which algebra the expression should belong to. In sympycore, this is
done by calling the corresponding algebra constructor with a single
string argument::

  Algebra('<expr>')

that will return the result of ``Algebra.convert('<expr>')``. Continue
reading the next section about the ``convert`` method.

How arbitrary Python objects are converted to expressions?
----------------------------------------------------------

Each algebra class has classmethod ``convert(<obj>, typeerror=True)``
that is used to convert arbitrary Python objects to Algebra instances.
The following algorithm is used:

#. If ``<obj>`` is already ``Algebra`` instance, then it is returned
   immidiately.

#. Next, the classmethod ``Algebra.convert_number(<obj>, typeerror) ->
   r`` is called. On success, ``Algebra.Number(r)`` is returned. In
   most cases, ``Algebra.Number`` class method just returns
   ``cls(NUMBER, r)``. But there exist exceptions.

#. Next, if ``<obj>`` is Python string or ``Verbatim`` instance, then
   ``Verbatim.convert(<obj>).as_algebra(Algebra)`` is returned.

#. Next, if ``<obj>`` is some algebra instance then
   ``<obj>.as_algebra(Algebra)`` is returned.

#. Finally, if none of the above did not return a result, then
   ``TypeError`` will be raised when ``typeerror`` is
   ``True``. Otherwise ``NotImplemented`` will be returned.

Continue reading the next section about the ``as_algebra`` method.

How algebra expressions are converted to other algebras?
--------------------------------------------------------

Each algebra class has instance method ``as_algebra(<other algebra
class>)`` that is used to convert instances of one algebra class to
instances of another algebra class. By default, the conversion is
carried out using the intermediate ``Verbatim`` algebra. First, the
instance of one algebra is converted to ``Verbatim`` algebra and then
the instance of a ``Verbatim`` algebra is converted to another
algebra. So, every algebra class must define ``as_verbatim()``
instance method that should return a ``Verbatim`` instance containing
verbatim representation of the algebra expression.

Of course, if an expression in one algebra does not make sense as an
expression of the other algebra, the ``TypeError`` will be raised.

Continue reading the next section about the ``Verbatim.as_algebra``
method.

How verbatim expressions are converted to other algebras?
---------------------------------------------------------

Verbatim expressions are converted to another algebras in ``<Verbatim
instance>.as_algebra(<Algebra class>)`` instance method. ``Verbatim``
instance holds a pair ``(<expression head>, <expression data>)`` and
the task of ``as_algebra`` method is to use information in triple
``<expression head>, <expression data>, <Algebra class>`` and
construct an ``<Algebra>`` instance representing expression in the
given algebra.

First, let us consider atomic expressions such as numbers and symbols.

In general, numbers can be low-level numbers such as ``int``,
``long``, ``mpq``, ``mpf``, ``mpc``, ``mpqc``, but numbers of one
algebra can be expressions of some other algebra. So, in case of
verbatim numbers, ``Algebra.convert(<Verbatim instance>.data)`` is
returned.

In general, symbols are Python string objects but certain string
values may be names of mathematical constants or predefined functions
for the given algebra. So, in the case of verbatim symbols,
``Algebra.convert_symbol(<Verbatim instance>.data)`` is returned.  It
also means that ``Algebra`` classes must define classmethod
``convert_symbol`` that can either return a algebra symbol instance
``Algebra(SYMBOL, data)`` or a predefined function or mathematical
constant.

Expressions are operations with operands. Therefore, to convert
verbatim expression to an expression of a given algebra, the algebra
must have a support for the given operation. The following table
summarizes how algebras can support different operations.

+-----------------+-------------------------------------------------+
| Expression head | Support hooks in ``Algebra`` class              |
+-----------------+-------------------------------------------------+
| POS             | ``Algebra.__pos__(operand)``                    |
+-----------------+-------------------------------------------------+
| NEG             | ``Algebra.__neg__(operand)``                    |
+-----------------+-------------------------------------------------+
| ADD             | ``Algebra.Add(*operands)``                      |
+-----------------+-------------------------------------------------+
| SUB             | ``Algebra.Sub(*operands)``                      |
+-----------------+-------------------------------------------------+
| MUL             | ``Algebra.Mul(*operands)``                      |
+-----------------+-------------------------------------------------+
| DIV             | ``Algebra.Div(*operands)``                      |
+-----------------+-------------------------------------------------+
| POW             | ``Algebra.Pow(*operands)``                      |
+-----------------+-------------------------------------------------+
| MOD             | ``Algebra.Mod(*operands)``                      |
+-----------------+-------------------------------------------------+
| LT              | ``Algebra.Lt(*operands)``                       |
+-----------------+-------------------------------------------------+
| GT              | ``Algebra.Gt(*operands)``                       |
+-----------------+-------------------------------------------------+
| LE              | ``Algebra.Le(*operands)``                       |
+-----------------+-------------------------------------------------+
| GE              | ``Algebra.Ge(*operands)``                       |
+-----------------+-------------------------------------------------+
| EQ              | ``Algebra.Eq(*operands)``                       |
+-----------------+-------------------------------------------------+
| NE              | ``Algebra.Ne(*operands)``                       |
+-----------------+-------------------------------------------------+
| AND             | ``Algebra.And(*operands)``                      |
+-----------------+-------------------------------------------------+
| OR              | ``Algebra.Or(*operands)``                       |
+-----------------+-------------------------------------------------+
| NOT             | ``Algebra.Not(*operands)``                      |
+-----------------+-------------------------------------------------+
| IN              | ``Algebra.Element(*operands)``                  |
+-----------------+-------------------------------------------------+
| NOTIN           | ``Algebra.Not(Algebra.Element(*operands))``     |
+-----------------+-------------------------------------------------+
| APPLY           | XXX                                             |
+-----------------+-------------------------------------------------+

Note that the operands to operations of a given algebra do not always
belong to the same algebra. For example, the operands of ``LT`` can be
``Calculus`` instances but the operation result is ``Logic`` instance.
The algebras can also vary within a list of operands. For example, the
first operand to ``IN`` should be an instance of set element algebra
while the second operand is a ``Set`` instance.
To support all these cases, the algebra class may need to define the
following additional methods:

#. ``Algebra.get_operand_algebra(head, index=0)`` - return the algebra
   class of ``index``-th operand in operation defined by ``head``.

#. ``<Algebra instance>.get_element_algebra()`` - return the element
   algebra class. The method must be defined by ``Set`` and
   ``MatrixRing`` classes, for instance. This method is instance
   method because the result may depend the instance content. For
   example, ``Set('Reals').get_element_algebra()`` would return
   ``Calculus`` while ``Set('Functions').get_element_algebra()``
   should return ``FunctionRing``.

