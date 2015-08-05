# Introduction #

Currently Algebra.convert is used to convert algebra operation
operands to operands algebra. This does not cover cases where
different algebra convert method should be used. For example,
the operand algebras of Logic.Lt and Logic.And are Calculus
and Logic, respectively. In such a case the convert method
depends on the expression head.

SOLUTION: See http://sympycore.googlecode.com/svn/trunk/doc/html/structure.html#how-does-it-work-in-sympycore

Please add questions and issues to comments.

# Overview of existing algebras #

All algebras may have `APPLY` operations or callable heads that must
defined their own argument algebras.


## `Verbatim` algebra ##

Operands algebras to all operations is `Verbatim`.

## `CollectingField` algebra ##

### `Calculus` algebra ###

| Operation head     | Operand LHS  | Operand RHS        |
|:-------------------|:-------------|:-------------------|
| NUMBER             |    -         | ll-number          |
| SYMBOL             |    -         | str                |
| ADD, SUB, MUL, DIV | Calculus     | Calculus           |
|                    | ll-number    | Calculus           |
|                    | Calculus     | ll-number          |
| POW                | Calculus     | Calculus           |
|                    | ll-number    | Calculus           |
|                    | Calculus     | ll-number          |
| APPLY              | FunctionRing | argument algebras  |
| callable           | -            | Calculus arguments |

_ll-number_ is low-level number (int, long, mpq, mpf, mpqc, mpc).

### `Unit` algebra ###

| Operation head     | Operand LHS  | Operand RHS       |
|:-------------------|:-------------|:------------------|
| NUMBER             |    -         | Calculus          |
|                    |    -         | ll-nunber         |
| SYMBOL             |    -         | str               |
| ADD, SUB, MUL, DIV | Unit         | Unit              |
|                    | ll-number    | Unit              |
|                    | Unit         | ll-number         |
| POW                | Unit         | int               |
| APPLY              | FunctionRing | argument algebras |
| callable           | -            | Unit arguments    |

### `FunctionRing` algebra ###

| Operation head     | Operand LHS  | Operand RHS            |
|:-------------------|:-------------|:-----------------------|
| NUMBER             |    -         | Calculus               |
|                    |    -         | ll-number              |
| SYMBOL             |    -         | str                    |
| ADD, SUB, MUL, DIV | FunctionRing | FunctionRing           |
|                    | ll-number    | FunctionRing           |
|                    | FunctionRing | ll-number              |
| POW                | FunctionRing | int                    |
| APPLY              | FunctionRing | argument algebras      |
| callable           |    -         | FunctionRing arguments |

### `Differential` algebra ###

| Operation head     | Operand LHS  | Operand RHS            |
|:-------------------|:-------------|:-----------------------|
| NUMBER             |    -         | Calculus               |
|                    |    -         | ll-number              |
| SYMBOL             |    -         | Calculus               |
|                    |    -         | str                    |
| ADD, SUB, MUL      | Differential | Differential           |
|                    | Calculus     | Differential           |
|                    | Differential | Calculus               |
|                    | ll-number    | Differential           |
|                    | Differential | ll-number              |
| DIV                | Differential | Calculus               |
|                    | Differential | ll-number              |
| POW                | Differential | int                    |
| APPLY              | FunctionRing | argument algebras      |
| callable           |    -         | Differential arguments |

## `Logic` algebra ##

| Operation head     | Operand LHS  | Operand RHS            |
|:-------------------|:-------------|:-----------------------|
| NUMBER             |    -         | bool                   |
| SYMBOL             |    -         | str                    |
| AND, OR            | Logic        | Logic                  |
| NOT                |    -         | Logic                  |
| LT, GT, LE, GE     | Calculus     | Calculus               |
| EQ, NE             | Calculus     | Calculus               |
| IN, NOTIN          | object       | Set                    |
| APPLY              | FunctionRing | argument algebras      |
| callable           |    -         | Logic arguments        |

Need to implement quantifier support: `ForAll`, `Exists`, `Any`, `All`. Their argument algebras may vary.

## `Set` algebra ##

| Operation head     | Operand LHS  | Operand RHS            |
|:-------------------|:-------------|:-----------------------|
| NUMBER             |    -         | frozenset              |
| SYMBOL             |    -         | str                    |
| APPLY              | FunctionRing | argument algebras      |
| callable           |    -         | Set arguments          |

Currently `Set` lacks operations but we need `Union`, `Intersection` etc.

Need to introduce optional `Set` element algebra, eg for `Integers`, `Reals`, and other
set symbols.

## `MatrixRing` algebra ##

| Operation head     | Operand LHS     | Operand RHS            |
|:-------------------|:----------------|:-----------------------|
| NUMBER             |    -            |    N/A                 |
| SYMBOL             |    -            | N/A                    |
| ADD, SUB, MUL      | MatrixRing      | MatrixRing             |
|                    | MatrixRing      | element algebra        |
|                    | element algebra | MatrixRing             |
| DIV                | MatrixRing      | element algebra        |
| POW                | MatrixRing      | int                    |
| APPLY              |    -            | N/A                    |
| callable           |    -            | N/A                    |

Need to introduce optional `Matrix` element algebra.

## `PolynomialRing` algebra ##

| Operation head     | Operand LHS         | Operand RHS            |
|:-------------------|:--------------------|:-----------------------|
| NUMBER             |    -                | dict                   |
| SYMBOL             |    -                | N/A                    |
| ADD, SUB, MUL      | PolynomialRing      | PolynomialRing         |
|                    | PolynomialRing      | coefficent algebra     |
|                    | coefficient algebra | PolynomialRing         |
| DIV                | PolynomialRing      | coefficient algebra    |
| POW                | PolynomialRing      | int                    |
| APPLY              |    -                | N/A                    |
| callable           |    -                | N/A                    |

# Convert methods #

All algebras should use default `convert` class method. It first tries
`convert_number` class method and then tries to do the conversion via
`Verbatim` algebra `as_algebra` method. Here the proper conversion
methods should be called. For that we need to have callback conversion
methods to original algebras. The aim of this wiki page is to workout
these callback hooks.