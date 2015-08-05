**This page is obsolete**

# Predicate function #

Assumption model is based on the implementation of a Predicate
function. The Predicate function is derived from Function and it
represents a function that values are either Python boolean objects
True or False, or boolean symbolic expressions.

Boolean symbolic expressions can be constructed using the following
functions (derived from the Predicate class): And, Or, XOr, Not,
Implies, Equiv.

```
>>> from sympy import *
>>> a=Boolean('a')
>>> b=Boolean('b')
>>> And(Not(a),Or(a,b))
And(Not(a), Or(a, b))
```

Predicate classes implement basic simplification rules. For example,
```
>>> Or(a,Not(a),False)
True
>>> And(a,Not(a))
False
```

To simplify logical expressions even further, use `.minimize()`
method:
```
>>> And(Not(a),Or(a,b)).minimize()
And(b, Not(a))
```
The `minimize` method uses
[Quine-McCluskey](http://en.wikipedia.org/wiki/Quine-McCluskey_algorithm)
algorithm to compute minimal logical expression in
terms of And, Or, and Not objects. Note that expressions involving XOr
are rewritten in terms of And, Or, and Not instances and therefore may
not always be minimal:
```
>>> XOr(a,b).minimize()
Or(And(a, Not(b)), And(b, Not(a)))
```

Predicate class implements `<boolean-expression>.test(<test-expression>)`
method to find out under which conditions given `<test-expression>`
is True assuming that `<boolean-expression>` is True. For example:
```
>>> And(a,Not(b)).test(a)
Not(b)
>>> And(a,Not(b)).test(Not(a))
False
>>> Or(a,Not(b)).test(a)
True
```

The `test` method will be the most important method in the developed
assumption model.  It can be used to verify if certain conditions are
satisfied and then return a simplified form of some exprepression:
```
>>> x = Symbol(x)
>>> Sqrt(x**2)
Sqrt(x**2)
>>> Sqrt(x**2).refine(IsReal(x))
Abs(x)
>>> Sqrt(x**2).refine(IsNonNegative(x))
x
```

## `test` method ##

In general, logical expressions may contain boolean variables
(instances of Boolean class) and conditional expressions (predicate
functions with arbitrary symbolic arguments). For example:
```
>>> x=Symbol('x')
>>> And(a,IsReal(x))
And(a, (IsReal(x)))
```

In the following we'll assume that conditional expressions are
replaced by dummy boolean variables and therefore some of the boolean
variables may have hidden implication relations. For example,
`And(a,IsReal(x),IsPositive(x))` will be replaced by `And(a,b,c)`
where `c,b` are related: `c` implies `b`.

The `A.test(T)` method returns a result of the following algorithm:

  1. Let _A_ be a predicate of boolean variables _B=(B1,..,Bn)_ in _{True,False}<sup>n</sup>_: _A=A(B)_.

  1. Let _T_ be a predicate of boolean variables _(B1,...,Bm,C1,..,Ck)_: _T=T(B',C)_, where _m<=n_ and _Ci_ are boolean variables that are not subexpressions of _A_. However, there may exists implications between boolean variables _B_ and _C_.

  1. Find all combinations of boolean values _B_ such that _A(B)_ evaluates to `True`, denote this set as _True<sup>A</sup>_
  1. The result of `A.test(T)` is _Or(A(B', C'),B in True<sup>A</sup>, C'=C(B))_. **This is incomplete!** See below the improvement of the algorithm and the actual code in `test` method.

As follows from the algorithm, one must be able to resolve hidden
implications between different boolean variables. It is possible to
write logical expressions in terms of boolean atoms such that all
hidden implications between variables are resolved. However, this is
not practical as such logical expressions grow in size very fast.

An alternative is smart evaluation of logical expressions that takes
into account relations between logical variables. The evaluation of
logical expressions boils down to `.subs()` method. For example, the
following behaviour is expected:
```
>>> IsReal(x).subs(IsPositive(x), True)
True
>>> IsReal(x).subs(IsPositive(x), False)
IsNonPositive(x)
>>> IsPositive(x).subs(IsReal(x), True)
IsPositive(x)
>>> IsPositive(x).subs(IsReal(x), False)
False
```

### Improved `test` method algorithm ###

  1. Let _A_ be a predicate of boolean variables: _A=A(B0,B1,B2,B3,B4,B5)_.
  1. Let _T_ be a predicate of boolean variables: _T=T(B0,C1,C2,C3,C4,C5)_.
  1. Assume the following relations: _C1 implies B1_, _B2 implies C2_, _C3 implies complement of B3_, _B4 implies complement of C4_, _A is invariant with respect to C5_, _T is invariant with respect to B5_.
  1. Find all combinations of boolean values _B_ such that _A(B0,..,B5)_ evaluates to `True`, denote this set as _True<sup>A</sup>_
  1. Apply the following substitution rules when substituting the values of _B_ to _T_:
    1. _C1.subs(B1,True)->C1_. Example: `IsInteger.subs(IsReal, True)->IsInteger`.
    1. _C1.subs(B1,False)->False_. Example: `IsInteger.subs(IsReal, False)->False`.
    1. _C2.subs(B2,True)->True_. Example: `IsReal.subs(IsInteger,True)->True`.
    1. _C2.subs(B2,False)->complementary of C2_. Example: `IsReal.subs(IsInteger,False)->IsIntegerC`.
    1. _C3.subs(B3,True)->False_. Example: `IsInteger.subs(IsRealC,True)->False`.
    1. _C3.subs(B3,False)->C3_. Example: `IsInteger.subs(IsRealC,False)->IsInteger`.
    1. _C4.subs(B4,True)->False_. Example: `IsRealC.subs(IsInteger,True)->False`.
    1. _C4.subs(B4,False)->False_. Example: `IsRealC.subs(IsInteger,False)->False` (note that _IsInteger is False_ implies _IsIntegerC is True_ and therefore _IsReal is True_)
  1. Compose a disjunction list _R_ as follows:
    1. Ignore all combinations of _B in True<sup>A</sup>_ such that _T.subs(B) is False_.
    1. Append _X_ to _R_ where _X_ is such that _Equiv(A,XOr(T,X)) is True_ with _T.subs(B) is not False_.
  1. Return the result of `A.test(T)` which is `Or(*R)`.

# Conditional functions #

Conditions are used to define statements stating that if a given
variable or expression belongs to a certain field or to its certain
subset.

For example, `IsPositive(x)` represents the statement that `x` is a
positive number, or equvalently, `x` satisfies the relation
`x>0`. From the condition `IsPositive(x)` one can also conclude that
`x` is a real number. To restrict `x` to be a positive integer number,
for instance, one must use a conjunction of conditions:
`And(IsPositive(x), IsInteger(x))`.

Each condition has a complementary condition. When a condition and its
complementary condition are used together in a disjunction then they
result a field. For example, The set of even integers has a
complementary set of odd integers and therefore `Or(IsEven(x),IsOdd(x))`
results in `IsInteger(x)`.

In `sympy` conditions are subclasses of the `Condition` function
(derived from the `Predicate` class). The following conditional functions
are defined (names ending with `C` indicate complementary functions):
```
IsComplex(<expr>)
  IsFixedC(<expr>,value=0)           alias to IsNonZero(<expr>)
  IsFixed(<expr>,value=0)            alias to IsZero(<expr>)
  IsRealC(<expr>)                    alias to IsImaginary(<expr>)
  IsReal(<expr>)
    IsRationalC(<expr>)              alias to IsIrrational(<expr>)
    IsRational(<expr>)
      IsIntegerC(<expr>, module=1)   alias to IsFraction(<expr>)
      IsInteger(<expr>, module=1)
        IsPrimeC(<expr>)             alias to IsComposite(<expr>)
        IsPrime(<expr>)
    IsPositiveC(<expr>, shift=0)     alias to IsNonPositive(<expr>, shift=0)
    IsPositive(<expr>, shift=0)
    IsNegativeC(<expr>, shift=0)     alias to IsNonNegative(<expr>, shift=0)
    IsNegative(<expr>, shift=0)
```
Note that
```
IsEven(<expr>) is IsInteger(<expr>, module=2)
IsOdd(<expr>) is IsIntegerC(<expr>, module=2)
IsLess(<expr>, <other>) is IsNegative(<expr>, shift=<other>)
IsGreater(<expr>, <other>) is IsPositive(<expr>, shift=<other>)
IsLessEqual(<expr>, <other>) is IsPositiveC(<expr>, shift=<other>)
IsGreaterEqual(<expr>, <other>) is IsNegativeC(<expr>, shift=<other>)
IsEqual(<expr>,<other>) is IsFixed(<expr>, value=<other>)
```

## Open issues ##

Note that `IsPositiveC(x)` implies that `x` is any non-positive
real number. So, `Or(IsPositive, IsPositiveC)` results in `IsReal`.
Should we introduce conditions like `IsPositiveInteger` and
`IsPositiveIntegerC` to obtain minimal fields in disjunction?