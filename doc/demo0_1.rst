.. -*- rest -*-

==========================
SympyCore Release 0.1 Demo
==========================

Getting started
===============

To use sympycore package from Python, one must import it:

>>> from sympycore import *

Constructing symbolic expressions
=================================

Generally speaking, symbolic expressions consist of symbols and
operation between them. To create symbolic expressions using
sympycore, one can either create symbol objects and perform operations
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

sympycore converts symbolic expressions to a canonical form that is
efficient for further manipulations and are also often obvious
simplifications that users may expect:

>>> x + x
Calculus('2*x')

>>> x - x
Calculus('0')

Manipulatins with symbolic expressions
======================================

The most obvious manipulation task applied to symbolic expressions, is
substitution -- replacing a subexpression of a given expression with a
new expression. For example,

>>> expr = x + y
>>> expr.subs(y, sin(x))
Calculus('x + sin(x)')

Other tasks include accessing parts of symbolic expressions:

>>> sorted(expr.args)
[Calculus('x'), Calculus('y')]

and constructing new expressions:

>>> Mul(*expr.args)
Calculus('x*y')

An important presumption for implementing varios algorithms is pattern
matching. Pattern matching means that given a pattern expression, the
pattern match method should first decide whether an expression can be
expressed in a form that the pattern defines, and second. it should
return information what subexpression parts correspond to the pattern
subexpressions. For example, given a pattern

>>> w = Symbol('w')
>>> pattern = x * w ** 3

where symbol ``w`` is assumed to match any subexpression, then expressions

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
with the propert

>>> pattern.subs(d1.items())==expr1
True
>>> pattern.subs(d2.items())==expr2
True

If no match is found, then the ``match`` returns ``None``:
>>> print (y*x**2).match(pattern, w)
None

Transformation methods
======================

The most common transformation task is expansion of subexpressions by
opening parenthesis:

>>> expr = (x+y)*z
>>> expr
Calculus('z*(x + y)')
>>> expr.expand()
Calculus('x*z + y*z')

In general, sympycore ``expand`` method expands products of sums and
integer powers of sums:

>>> expr = (x+y)*(1+x)**3
>>> expr.expand()
Calculus('x + y + x**4 + 3*x**2 + 3*x**3 + 3*x*y + 3*y*x**2 + y*x**3')

Calculus methods
================

sympycore provides methods to differentiate symbolic expressions:

>>> expr = x+sin(x*y)*x
>>> expr.diff(x)
Calculus('1 + sin(x*y) + x*y*cos(x*y)')

as well as integrate symbolic expression representing polynomials:

>>> expr = x + 3*z*x**2
>>> expr.integrate(x)
Calculus('1/2*x**2 + z*x**3')
>>> expr.integrate((x, 2, y))
Calculus('1/2*y**2 + z*(y**3 - 8) - 2')

