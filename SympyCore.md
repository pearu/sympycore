**This page is obsolete**

# Defining symbolic objects #

The `sympy.core.basic` module defines two basic classes, `BasicType` and `Basic`,
that are used as base classes to all symbolic classes in `sympy`.

Symbolic classes define mathematical concepts and methods to manipulate and
to inquire information from symbolic expressions.

## The `BasicType` class ##

The class `BasicType` is derived from Python `type`
and implements the following features:

  * It sets `classes.<ClassName>` attributes so that modules in subpackages can have access to all classes that `sympy` defines via `classes` instance attribute access. This avoids the need to import modules that implement classes and therefore reduces the possibility for cyclic module import occurence. For example,
```
>>> from sympy.core import Basic
>>> classes.Add
Add
>>> classes.Union
Union
>>> classes.Symbol
<class 'sympy.arithmetic.symbol.Symbol'>
```


## The `Basic` class ##

The class `Basic` is derived from Python `object`
and uses `BasicType` as a metaclass.

The `Basic` class implements default methods
for manipulating symbolic expressions and acquiring various information from these.

### The `Basic.tostr(...)` method ###

The `Basic.tostr(self, level=0)` method is used in `__str__` method to return a pretty string representation of `self`.
Subclasses of `Basic` should not reimplement the `__str__` method but instead
implement the `tostr` method using the following template:
```
def tostr(self, level=0):
    precedence = self.precedence
    result = '<pretty string of self>'
    if precedence<=level:
        return '(%s)' % (result)
    return result
```

### The `Basic.torepr(...)` method ###

The `Basic.torepr(self)` method is used in `__repr__` method to return a reproducible string representation of `self`.
Subclasses of `Basic` should not reimplement the `__repr__`
method but only implement the `.torepr()` method.

The `Basic.__repr__(self)` method uses `Basic` data attribute `repr_level` to
decide whether to return the output of the `tostr` or `torepr` method calls:
```
>>> expr = 1 + Symbol('x')
>>> Basic.repr_level = 0
>>> expr
Add({Integer(1): Integer(1), Symbol('x'): Integer(1)})
>>> Basic.repr_level = 1  # `1` is default value
>>> expr
1 + x
```

### The `Basic.precedence(...)` property ###

The `Basic.precedence(self)` property method should return a Python `int`
that value determince whether or not the string represetnation of `self`
should have parenthesis when it is a subexpression of a parent expression.
The following rule is applied:

> If the precedence of `self` is smaller or equal to the precedence of a parent expression (that is passed to the `tostr` method as the argument `level`) then `self` string expression should have parenthesis around.

### The `Basic.compare(...)` method ###

The `Basic.compare(self, other)` method returns -1,0, or 1 if `self` is _smaller
than_, _equal to_, or _greater than_ `other`, respectively, in the sense of
natural ordering of Basic subclass instances.

Subclasses of `Basic` seldomly need to redefine the `compare` method. If they
do, then use the following template:
```
def compare(self, other):
    if self is other: return 0
    c = cmp(self.__class__, other.__class__)
    if c: return c
    # self and other are instances of the same class
    c = <compute customized value of compare>
    return c
```
One can use `Basic.compare` method to sort a list of symbolic expressions:
```
>>> l = [1+Symbol('x'),2,Symbol('x')]
>>> l
[1 + x, 2, x]
>>> l.sort()
>>> l
[2, 1 + x, x]
>>> l.sort(Basic.compare)
>>> l
[2, x, 1 + x]
```

### The `Basic.__eq__(...)` and `Basic.__hash__(...)` methods ###

All `Basic` subclasses that use customized constructors should redefine
the `Basic.__eq__(self, other)` and `Basic.__hash__(self)` methods.

The `__eq__` method should always return Python `True`
or `False` values depending on whether the objects `self` and `other` are
equal or not in the sense of internal representations of the objects.

Methods `__eq__` and `__hash__` allow using symbolic expressions
as keys of Python dictionary objects. Hence, symbolic expressions
must be immutable objects, in general.

> Subclasses of `Basic` should **not** redefine `__nonzero__(self)` method.
> Codes should **not** use idioms like:
```
  if <symbolic expression>:
    ...
```

### the `Basic.replace(...)` method ###

The `Basic.replace(self, old, new)` replaces subexpression `old` in `self` with
expression `new` and returns result.

When implementing `replace` method, note that `old` and `new` may be
arbitrary Python objects and the method code may need the following
statements:
```
old = sympify(old)
new = sympify(new)
```

### The `Basic.atoms(...)` method ###

The `Basic.atoms(self, type=None)` method returns a Python `set` instance
containing the atoms (of given type) that form the object `self`:
```
>>> expr = 2 + Symbol('x')
>>> expr.atoms()
set([1, 2, x])
>>> expr.atoms(Symbol)
set([x])
```

### The `Basic.has(...)` method ###

The `Basic.has(self, *patterns)` returns `True` if `self` has any of
the patterns:
```
>>> expr = 2 + Symbol('x')
>>> expr.has(Symbol('x'))
True
>>> expr.has(Symbol('y'))
False
```

### The `Basic.clone(...)` method ###

The `Basic.clone(self)` method returns a recreated composite object of `self`
without using caching.

## Other basic classes ##

The `Atom` and `Composite` classes are derived from `Basic`. These classes
should be used as base classes to atomic and composite classes, respectively.
To decide whether a class is _atomic_ or _composite_, use the following rule:

> A class instance is _composite_ if its data attributes contain objects that are `Basic` instances, otherwise the class instance is _atomic_.

See also [BasicSymbol](SympyCoreSymbol.md) and [BasicFunction](SympyCoreFunction.md).