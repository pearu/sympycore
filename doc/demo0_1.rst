.. -*- rest -*-

==========================
SympyCore Release 0.1 Demo
==========================

:Authors:
  Pearu Peterson <pearu.peterson AT gmail DOT com>

:Created:
  February 2008

:Website:

  http://sympycore.googlecode.com/

.. sidebar:: Table of contents

    .. contents::
        :depth: 2
        :local:

Getting started
===============

This document gives a short overview of SympyCore basic features. For
more information see the `SympyCore User's Guide`__.

__ http://sympycore.googlecode.com/svn/trunk/doc/html/userguide.html

To use the ``sympycore`` package from Python, one must import it:

>>> from sympycore import *

Constructing symbolic expressions
=================================

Generally speaking, symbolic expressions consist of symbols and
operation between them. To create symbolic expressions using
SympyCore, one can either create symbol objects and perform operations
between them:

>>> x = Symbol('x')
>>> y = Symbol('y')
>>> z = Symbol('z')
>>> x + y
Calculus('x + y')

or one can use symbolic expression parser to construct symbolic
expressions from a string:

>>> Calculus('x + y')
Calculus('x + y')

SympyCore converts symbolic expressions to a canonical form that is
efficient for further manipulations and are also often obvious
simplifications that users may expect:

>>> x + x
Calculus('2*x')

>>> x - x
Calculus('0')

General symbolic arithmetic expressions are instances of the Calculus
class. Using the ``print`` statement (or ``str()``) hides this information:

>>> print x + y
x + y

Manipulations with symbolic expressions
=======================================

The most obvious manipulation task applied to symbolic expressions, is
substitution -- replacing a sub-expression of a given expression with a
new expression. For example,

>>> expr = x + y
>>> print expr.subs(y, sin(x))
x + sin(x)

Other tasks include accessing parts of symbolic expressions:

>>> sorted(expr.args)
[Calculus('x'), Calculus('y')]

and constructing new expressions:

>>> print Mul(*expr.args)
x*y

An important presumption for implementing various algorithms is pattern
matching. Pattern matching means that given a pattern expression, the
pattern match method should first decide whether an expression can be
expressed in a form that the pattern defines, and second. it should
return information what sub-expression parts correspond to the pattern
sub-expressions. For example, given a pattern

>>> w = Symbol('w')
>>> pattern = x * w ** 3

where symbol ``w`` is assumed to match any sub-expression, then expressions

>>> expr1 = x*sin(y)**3
>>> expr2 = x*(x+y)**3

do match the given pattern:

>>> d1 = expr1.match(pattern, w)
>>> print d1
{Calculus('w'): Calculus('sin(y)')}

>>> d2 = expr2.match(pattern, w)
>>> print d2
{Calculus('w'): Calculus('x + y')}

The result of ``match`` method, when the match is found, is a dictionary
with the property

>>> pattern.subs(d1.items())==expr1
True
>>> pattern.subs(d2.items())==expr2
True

If no match is found, then the ``match`` returns ``None``:

>>> print (y*x**2).match(pattern, w)
None

Transformation methods
======================

The most common transformation task is expansion of sub-expressions by
opening parenthesis:

>>> expr = (x+y)*z
>>> print expr
z*(x + y)
>>> print expr.expand()
x*z + y*z

In general, the ``expand`` method expands products of sums and
integer powers of sums:

>>> expr = (x+y)*(1+x)**3
>>> print expr.expand()
x + y + x**4 + 3*x**2 + 3*x**3 + 3*x*y + 3*y*x**2 + y*x**3

Arithmetic methods
==================

SympyCore provides exact rational and complex numbers:

>>> Calculus('3/12')
Calculus('1/4')
>>> print (2 + 3*I/4)**4
721/256 + 165/8*I

Fractional powers of integers are evaluated to simpler
expressions when possible:

>>> Calculus('8**(1/3)')
Calculus('2')
>>> Calculus('243**(1/5)')
Calculus('3')

SympyCore supports converting symbolic expressions with exact numbers
such as integers and rational numbers to expressions with arbitrary
precision floating-point numbers:

>>> expr = 2*pi + E**x
>>> print expr
E**x + 2*pi
>>> print expr.evalf(5)
6.2832 + 2.7183**x
>>> print expr.evalf(25)
6.283185307179586476925287 + 2.718281828459045235360287**x

Calculus methods
================

SympyCore provides methods to differentiate symbolic expressions:

>>> expr = x+sin(x*y)*x
>>> print expr.diff(x)
1 + sin(x*y) + x*y*cos(x*y)

as well as integrate symbolic expression representing polynomials:

>>> expr = x + 3*z*x**2
>>> print expr.integrate(x)
1/2*x**2 + z*x**3
>>> print expr.integrate((x, 2, y))
1/2*y**2 + z*(y**3 - 8) - 2

SympyCore implements the elementary functions ``exp``, ``log``,
``sqrt``, ``cos``, ``sin``, ``tan``, ``cot``, and simplifies
their values in basic cases:

>>> print log(10000,10)
4
>>> print sin(5*pi/6)
1/2
>>> print cos(x+pi/2)
-sin(x)

Polynomial rings
================

SympyCore provides efficient ways to represent univariate and
multivariate polynomials. Currently there are two representation
supported. The first one is suitable for univariate dense polynomials:

>>> poly1 = UnivariatePolynomial([2,0,3,4], symbol='x')
>>> poly2 = UnivariatePolynomial([0,1,0,5,6], symbol='x')
>>> poly1
2 + 3*x**2 + 4*x**3
>>> poly2
x + 5*x**3 + 6*x**4
>>> poly1 + poly2
2 + x + 3*x**2 + 9*x**3 + 6*x**4

And the other representation is suitable for multivariate sparse
polynomials:

>>> P = PolynomialRing[(x,y)]
>>> poly1 = P({(1,2):7, (300,4):5})
>>> poly2 = P({(3,4):-7, (2,500):12})
>>> poly1
PolynomialRing[(x, y), Calculus]('5*x**300*y**4 + 7*x*y**2')
>>> print poly2
((-7))*x**3*y**4 + 12*x**2*y**500
>>> print poly1 + poly2
5*x**300*y**4 + ((-7))*x**3*y**4 + 12*x**2*y**500 + 7*x*y**2

Here the ``PolynomialRing[symbols, Algebra]`` represents a factory of
a polynomial ring over ``Algebra`` with ``symbols``.

Matrix rings
============

SympyCore supports representing rectangular matrix ring elements using
similar idea of ring factory:

>>> M = MatrixRing[(3,4)]
>>> matrix = M({(1,2):x+y, (0,0):x+z})
>>> print matrix
 x + z  0      0  0
     0  0  x + y  0
     0  0      0  0

Note that matrices are mutable in SympyCore and indexes start from 0:

>>> matrix[1,0] = 5
>>> print matrix
 x + z  0      0  0
     5  0  x + y  0
     0  0      0  0

SympyCore provides ``SquareMatrix`` and ``PermutationMatrix``
factories for convenience:

>>> SqM = SquareMatrix[3]
>>> m = SqM({(0,0): 1, (2,1): 3, (2,2):6, (1,2):-2, (2,0): -1})
>>> print m
  1  0   0
  0  0  -2
 -1  3   6
>>> print PermutationMatrix[4]([2,1,3,0])
 0  0  1  0
 0  1  0  0
 0  0  0  1
 1  0  0  0

One can perform LU factorization on any rectangular matrix:

>>> p, l, u = m.lu()
>>> print p
 1  0  0
 0  0  1
 0  1  0
>>> print l
  1  0  0
 -1  1  0
  0  0  1

>>> print u
 1  0   0
 0  3   6
 0  0  -2

The ``*`` denotes matrix multiplication:

>>> print p * l * u == m
True

SympyCore supports computing inverses of square
matrices:

>>> print m.inv()
   1     0    0
 1/3     1  1/3
   0  -1/2    0

>>> m.inv() * m == SqM.one
True

Physical units
==============

SympyCore has a basic support for dealing with symbolic expressions with
units:

>>> mass1 = 5 * kilogram
>>> mass2 = x * kilogram
>>> print mass1 + mass2
(5 + x)*kg
