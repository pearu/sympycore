# Introduction #

An undefined applied function, `f(x)`, can be currently
represented as
```
  Algebra(APPLY, (f, x))
```
where `f` and `x` are algebra symbols.

This representation is not optimal because

  1. `f` being an algebra element is not correct
  1. there is no clean way to represent derivatives of `f(x)`, currently `f(x).diff(x)` raises exception.

A solution is to introduce separate algebra for functions where undefined functions would be symbols, calculus elements would be numbers, and differential operators would be algebra functions. More details follow below.

References:
> http://en.wikipedia.org/wiki/Function_(mathematics)

# Constructing functions #

```
f = Function('f')        # undefined unapplied function with a name `f`
g = Function(g_callable) # defined unapplied function
h = Function(<Calculus instance>) # constant unapplied function
```

To specify the domain and value set of a function, use `Function(name, <domain>, <value algebra>)` where `<domain>` is a tuple of algebra classes or just a algebra class.
By default, `<domain>=Calculus` and `<value algebra>=Calculus`.

The number of arguments is specified by the length of the `<domain>` tuple.
For example,
```
Function('f', (Calculus, Calculus), Calculus) # undefined unapplied function with 2 arguments.
```

Will we support `Function('f', nargs=2)`?

## Implementation notes ##

  1. `Function` is a python function that returns a dynamically generated `FunctionRing` subclass instance. For example, Function('f') -> `FunctionRing_Calc_to_Calc('f')`
  1. `FunctionRing` is derived from `CollectingField`.
  1. Representations of FunctionRing instances:
```
<FunctionRing subclass>(SYMBOL, 'f')                 # undefined unapplied function
<FunctionRing subclass>(NUMBER, <Calculus instance>) # constant unapplied function
<FunctionRing subclass>(TERMS, {f:2, g:3})           # linear combination of unapplied functions: 2*f + 3*g
```

# Inquiring domain information #

If `f=Function('f')` then
```
f.nargs             -> number of arguments, default is 1
f.argument_algebras -> tuple of argument algebras, default is (Calculus,)
f.value_algebra     -> value algebra class, default is Calculus
```

# Differential operator support #

```
D[i] - 1-st partial derivative with respect to i-th argument, i is integer
D[x] - 1-st partial derivative with respect to x
D[i]**n - n-th partial derivative with respect to i-th argument
D[x]**n - n-th partial derivative with respect to x
D[i]**n * D[j]**m - (n+m)-th partial derivative with respect to i-th (n-times) and j-th (m-times) argument
D[x]**n * D[y]**m - (n+m)-th partial derivative with respect to x (n-times) and y (m-times)
D[i] + D[j] - represents a sum of differential operators.
```

Notes:
  1. `D[i]` can be applied only to unapplied functions.
  1. `D[x]` can be applied to expressions containing `x`.
  1. `D[i]` is a symbol of differential algebra `Differential(SYMBOL, i)`
  1. Differential algebra numbers are Calculus elements.
  1. `D[0](sin)` returns `cos`.
  1. `D[0](f)` returns `FunctionRing(D[0], f)`.
  1. `D[x](sin(x))` returns `cos(x)` that is `Calculus(cos, x)`
  1. `D[x](f(x))` returns `Calculus(FunctionRing(D[0], f), x)`
  1. Note that `D[x]` can only occure in differential algebra operations. When applying differential algebra elements to expressions, it will be replaced with using `D[0], D[1],..` operators.

# Unresolved issues #

  1. We are using `Function` as a base class to defined functions. Proposal: rename `Function` to `DefinedFunction` [DONE](DONE.md)

  1. Using `FUNCTION(nargs, TERMS)` instead of `TERMS` means that we cannot reuse the code from `CollectingField`. The alternative of using `TERMS` means that it will be expensive to check if the number of function arguments match in operations. [SOLUTION: the argument information is in automatically generated `FunctionRing` subclass]

  1. Should we raise an exception when doing `D[i] * D[x]`? Or would be there interesting applications so that we can allow that? For example, `D[a](a**2 * D[i]) -> 2*a*D[i]`.