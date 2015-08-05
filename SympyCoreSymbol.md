**This page contains obsolete infromation**

# Defining symbols #

The module `sympy.core.symbol` provides a `Basic` class, `BasicSymbol`,
to define _symbols_.

Symbols are objects with names.

`BasicSymbol` is derived from `Atom` and Python `str`.

A symbol object has a name that can be accessed
via `.name` attribute.

Symbols are equal when their names are equal.
```
>>> a=BasicSymbol('a')
>>> b=BasicSymbol('a')
>>> a==b
True
>>> a.name
'a'
```

## Dummy symbols ##

Sometimes one needs to create an auxiliary symbol within an algorithm
and so that it will be always unique, ie, it is equal to itself and only
to itself.

The `sympy.core.symbol` provides a base class `BasicDummySymbol` to
define unique symbols.

Dummy symbols may have a name. To distinquish dummy symbols from
ordinary symbols in an expression, their names are prefixed with
one underscore.
```
>>> a=BasicDummySymbol('a')
>>> b=BasicDummySymbol('a')
>>> a==b
False
>>> a==a
True
>>> a
_a
```

## Wild symbols ##

Wild symbols are dummy symbols that match any expression but another
wild symbol.

The `sympy.core.symbol` provides a base class `BasicWildSymbol` to
define wild symbols.

In an expression, the names of wild symbols are suffixed with one underscore.
```
>>> w=BasicWildSymbol('w')
>>> w
w_
```

## Notes ##

  * `BasicSymbol` is a subclass of Python `str` and it does not define arithmetic operations (use `Symbol` from `sympy.arithemetic.symbol` for that). So, adding `BasicSymbol` objects is equivalent to concatenating strings:
```
>>> a=BasicSymbol('a')
>>> a+'bc'
'abc'
```
> In future the `BasicSymbol` methods like `__add__`, etc may be redefined to return `NotImplemented`.