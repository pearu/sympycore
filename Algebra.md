**This page needs update corresponding to
http://sympycore.googlecode.com/svn/trunk/doc/html/structure.html**

# Introduction #

See:
  * http://wiki.sympy.org/index.php/Algebras_in_SymPyCore.
  * http://groups.google.com/group/sympycore/browse_thread/thread/619a228a1afc6305

# Definitions #

Algebra is a mathematical structure of a set and operations on the set.

Here follows a hierarchy of algebraic operations:

  * [Magma](http://en.wikipedia.org/wiki/Magma_(algebra)) - a set with one closed binary operation
  * Quasigroup - a magma with division
  * Loop - a quasigroup with identity
  * Semigroup - a magma with associativity
  * Monoid - a semigroup with identity
  * Group - a loop with associativity or a monoid with inversibility
  * Abelian group - a group with commutativity

The following notation is used:

  * Additive group - a group with `+` operation, `0` is identity, `-` denotes inverse
  * Multiplicative group - a group with `*` operation, `1` is identity, `**(-1)` denotes inverse
  * `(G, *)` - denotes a group with operation `*`.

Examples:
  * `(Z, +)` - additive abelian group
  * `(Z/pN, *)` - multiplicative abelian group
  * `(Q\{0}, *)` - multiplicative abelian group
  * permutations of a set

Algebras with two operations:
  * Ring `(R, +, *)` - `(R,+)` is abelian group, `(R,*)` is monoid, with distributivity.
  * Commutative ring - a ring with commutative `*` operation.
  * Field `(F, +, *)` - a commutative division ring where `1 != 0`.

Examples:
  * `(Z, +, *)` - commutative ring
  * `R[X]` - polynomials over `R` is a ring
  * `n`-by-`n` matrices with elements in `R` form a noncommutative ring
  * `(Q, +, *)`, `(R, +, *)`, `(C, +, *)` are fields
  * `(Z/pZ, +, *)` is a field where p is prime (integers module prime p), `GF(p)`.

Algebras with scalar multiplication:
  * Left `R`-module M - `(M, +)` is abelian group, `R` is ring, `R x M -> M`
  * Right `R`-module
  * Bimodule `M` - left and right R-module with compatible scalar `*`.
  * Vector space - a bimodule over a field
  * `K`-algebra - a vector space over a field `K` with `*` operation between elements


## Algebra ##

An algebra is a tuple `(A, +, *)` where `A` is a set and `+`, `*`,
are binary operations that are defined between the elements of `A`.
Repeated usage of binary operations on the same element, say `x` and
using `+` operation,
```
  x + x + ... + x
```
is denoted by
```
  x * n
```
where `n` is the number counting how many times the element `x` is used in
the above sum expression. The number `n`, called as a _coefficient_, can
be an integer but the above concept of repetition can be generalized
to other sets of numbers such as rationals, real numbers, algebraic
numbers etc.

In above we defined the multiplication operation between an algebra
element and a number. Similarly is defined exponentation operation
```
  x ** m
```
that means of using element `x` `m`-times in the product
```
  x * x * ... * x
```
The number `m` is called an _exponent_.

Operations `-` and `/` can be defined using the concepts above:
```
  x - y == x + y * (-1)
  x / y == x * y ** (-1)
```
Operation `+` can be also defined between an algebra element and
a number:
```
  x + n == x + e * n
```
where `e` is identity element of an algebra with respect to `*` operation
(`x * e == x`).

So, instead of the tuple `(A, +, *)`, we can consider equivalent tuple
`(A, +, *, -, /, **, N, M)` where `N`, `M` are set of numbers where the
coefficients and exponents of algebraic expressions belong, respectively.

See also http://en.wikipedia.org/wiki/Universal_algebra

## Ring ##

Note that the sets of numbers may also form algebras but often they
are rings `(R, +, *)`. Examples:

  * Sets (fields) of intergers, rational, real, complex numbers are commutative rings.

  * Sets of (multivariate) polynomials with coefficients in ring, are rings.

See also http://en.wikipedia.org/wiki/Ring_(algebra).

# Specification of algebraic structures #

The `sympycore.algebra` package defines the following classes to represent
algebras (their instances are actually representing algebra elements):
```
  AlgebraicStructure
    BasicAlgebra
      PrimitiveAlgebra
      CommutativeRingWithPairs
        IntegerAlgebra
        StandardCommutativeAlgebra
      UnivariatePolynomial
```

The `BasicAlgebra` class is a base class to all algebras and it collects various
implementation specific methods. For example, it defines default methods for `+`,
`-`, `*`, `/`, `**` operations. The actual implmentations of algebra operations
are implmented by the following static methods:
  * `.Add(seq)` - performs summation over an sequence `seq` items,
  * `.Mul(seq)` - performs multiplication over an sequence `seq` items,
  * `.Pow(base, exponent)` - performs exponentation.
By default, these methods raise `NotImplementedError` meaning that derived algebra
classes must redefine these classes.

### PrimitiveAlgebra ###

Many algebras are subalgebras of others and in order to provide a way to transform
an algebra element to an other one, the `PrimitiveAlgebra` class is used as an universal
language between algebras. The `PrimitiveAlgebra` represents symbolic expressions
in most general way - no evaluation is carried out in operations. The elements of
primitive algebra are represented as instances of the `PrimitiveAlgebra` class
that hold a `tree` attribute containing a tuple
```
  (<head>, <operands tuple|object>)
```
where `<head>` is a symbol of operation and the `<operands tuple>` contains
operands of the operation. If `<head>` is `NUMBER` or `SYMBOL` then `<object>`
can be any Python object (some implementations of algebras may set additional
requirments to 

&lt;object&gt;

, e.g. it may need to be hashable).
The following constants are defined as valid values to `<head>`:
```
  TUPLE, LAMBDA, APPLY
  OR, AND, NOT
  LT, LE, GT, GE, EQ, NE
  BOR, BXOR, BAND, BNOT
  POS, NEG, ADD, SUB, MOD, MUL, DIV, POW
  NUMBER, SYMBOL
```

To transform an algebra to primitive algebra, the algebra class must implement
`as_primitive` method. When doing so, the algebra can be transformed
to any other algebra via
```
  .as_algebra(<algebra class>, source=None)
```
method where the `<algebra class>` is the class of the target algebra. The
transformation means that any operations between the operands of the given
algebra are performed with the methods of the target algebra. By default,
SYMBOL elements are mapped to SYMBOL elements of the target algebra,
ditto for NUMBER elements.

Since an element of one algebra may be a number of another algebra
(e.g. the coefficents algebra) then the target algebra needs interpret
the operands correctly. XXX: we need a shortcut to source-algebra
-> primitive-algebra -> target-algebra as the information about the
source algebra is lost.


### CommutativeRingWithPairs ###

The `CommutativeRingWithPairs` is a base class to many commutative
algebras that define `+` and `*` operations. The sums and products
in this algebra are represented in the forms of terms (
expression-coefficient pairs) and factors (base-exponent pairs).

To construct `CommutativeRingWithPairs` instance, use
```
CommutativeRingWithPairs(<obj>, head=None)
```
where `head` can either be `SYMBOL`, `NUMBER`, `ADD`, or `MUL`.  If it
is `None`, then `<obj>` is converted to given algebra using
`CommutativeRingWithPairs.convert` method (subclasses may redefine
this class method). If `<obj>` is string then it will be
parsed. Otherwise `<obj>` is saved in the `.data` attribute of the
algebra instance.

When using `CommutativeRingWithPairs` algebra class, one needs to talk
about the algebra of coefficients and the algebra of exponents.  The
elements of these algebras are usually numbers but they can also be
elements of other algebras that support `+` and `*` operations. The
`.convert`, `.convert_coefficient`, `.convert_exponent` methods define
how arbitrary python objects are treated in operations `+`, `*`, and `**`.

A summary of valid Python objects for coefficient/exponent algebras
is given in the table below:
| Algebra | Coefficient algebra | Exponent algebra |
|:--------|:--------------------|:-----------------|
| CommutativeRingWithPairs | int, long           | int, long        |
| StandardCommutativeAlgebra | int, long, float, complex, mpq, mpf, mpc, extended\_number | StandardCommutativeAlgebra, int, long |

The `.convert` method must return an instance in the first column.
The `.convert_coefficient` method must return an instance of the second column.
The `.convert_exponent` method must return an instance of the third column.

### Integer algebra ###

The class `Integers` represents a symbolic integer algebra that
consists of integer numbers and symbolic expressions that may contain
sums and products of integer symbols.  The exponents of symbolic
integers are always nonnegative integer objects (Python `int` or
`long` instances).

Examples:
```
>>> from sympycore.algebra import *
>>> Integers(2)
Integers(2, head=NUMBER)
>>> Integers('a*b**2')
Integers({Integers('a', head=SYMBOL): 1, Integers('b', head=SYMBOL): Integers(2, head=NUMBER)}, head=MUL)
>>> Integers('2*a+3+b')
Integers({Integers('a', head=SYMBOL): 2, Integers(1, head=NUMBER): 3, Integers('b', head=SYMBOL): 1}, head=ADD)
>>> print Integers('2*a+3+b')
3 + b + 2*a
```