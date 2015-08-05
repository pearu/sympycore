**This page is obsolete**

# Predicate function #

Predicate function is a function with two possible values: `True` or `False`.

`sympy.logic.symbolic` defines the base class `Predicate` (derived from `Function`) to various predicate functions and logical operations. Predicate functions may return
Python `bool`, `Boolean` instances or logical expressions.

## Boolean symbols ##

To define symbols that are usable in logical expressions, use `Boolean` class:
```
>>> a=Boolean('a')
>>> a
a
```

## Logical expressions ##

Logical expressions can be constructed using the following predicate
operations:

  * `Not(<logical expression>)` - logical NOT
  * `And([<logical expression>, ]...)` - logical AND
  * `Or([<logical expression>, ]...)` - logical OR
  * `XOr([<logical expression>, ]...)` - logical XOR

Number of logical expressions can be expressed using the above operations:

  * `Implies(<logical expr1>, <logical expr2>)` - logical IMPLIES relation
  * `Equiv(<logical expr1>, <logical expr2>)` - logical EQUVALENCE relation

```
>>> a=Boolean('a')
>>> b=Boolean('b')
>>> Implies(a, b)
Or(b, Not(a))
>>> Equiv(a, b)
Not(XOr(a, b))
```