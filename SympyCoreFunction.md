**This page is obsolete**

# Symbolic functions #

Symbolic functions in `sympy` are at the same time Basic instances and class
objects. Their base class is `Callable(Basic, BasicType)` that applies
special decorators to `Basic` and `BasicType` methods so that `Callable`
methods can be called both by instances and derived classes (without
these decorators one would get `TypeError` about calling unbound method).

There are two basic types of symbolic functions: function symbols and lambda functions.

Function symbols can be defined or undefined. In `sympy` these functions
are indistinguishable (undefined functions have default `canonize` class
methods that always return `None`).
However, as a rule, defined functions are "global", that is, the `classes` instance
has attributes `<FunctionName>` and the `Basic` class has `is_<FunctionName>` that
hold the function class object and the truth value if a function instance
(the value of a function at given point, evaluated function) is an
instance of `FunctionName` or not, respectively. But note that one can derive
non-global functions from global defined functions.

Lambda functions are unnamed functions that define a mapping
`<arguments>: <expression>`.

# Defining function symbols #

The `sympy.core.function` module defines `BasicFunctionType` (derived
from Atom and Callable) that is a metaclass to the `BasicFunction` class.
The `BasicFunction` is a base class to all function symbols in `sympy`.

Symbolic functions have `signature` attribute that defines the valid argument
types and return value types for a function. The `signature` must
be a `FunctionSignature` instance. `FunctionSignature` takes optional arguments
`argument_classes` and `value_classes` that values must follow the following rules:
  * `argument_classes`/`value_classes` is None - no rules or information is specified for arguments/return values of the function.
  * `argument_classes = (type_1, type_2, .., type_n)` - the function takes exactly `n` arguments and they must be of `type_1`, `type_2`,..,`type_n`, respectively. The tuple items may be tuples of types.
  * `argument_classes = [type]` - the function takes arbitrary number of arguments but they all must have `type` type. `type` may be also a tuple of types.
  * `value_classes = (type_1, .., type_n)` - the function returns `n` values of given types.
  * By default `argument_classes = (Basic,)` and `value_classes = (Basic,)`, that is, by default symbolic functions take exactly one argument that must be a `Basic` instance and they return one value that is `Basic` instance.


## Global function symbols ##

To define a global function symbol that is accessible via `Basic` attribute,
use the following template:
```
class MyFunc(BasicFunction):
    signature = ...
    @classmethod
    def canonize(cls, args):
        ...
        return
```
Here the `canonize` classmethod can define basic function evaluation rules
that are applied to arguments in tuple `args`. The `canonize` method can return either
a new expression or `None` if no evaluation can be carried out. If `canonize`
method canonizes arguments `args` to say, `new_args`, then the method should
return `cls(*new_args,dict(is_canonical = True))`. The `is_canonical=True` option
forces to skip calling `canonize` method and construct the instance immidiately.

If a function symbol and its instance can be used in arithemtic expressions,
then use `Function` (defined in `sympy.arithmetic.function`) as a base
class instead of `BasicFunction`.

Example:
```
class Foo(BasicFunction):
    """ Example function Foo that takes two arguments of type Basic and
    it has the following property:
      Foo(x,x) -> x
    """
    signature = FunctionSignature(argument_classes = (Basic, Basic))
    @classmethod
    def canonize(cls, (argument1, argument2)):
        if argument1 == argument2:
            return argument1
>>> Foo(1,1)
1
>>> Foo(1,2)
Foo(1, 2)
>>> 
```

## Generalized function symbols ##

In general, one can use `BasicFunctionType` for defining new symbolic
functions instead of the Python `class` statement. `BasicFunctionType`
has the following signature:
```
BasicFunctionType(name, bases=None, attrdict=None, is_global=None)
```
and it returns a new class object that is derived from `BasicFunction`
has a name `name`. Here `bases` argument can be either a `BasicFunction`
class or a tuple of base classes. `attrdict` is a dictionary containing
the attributes of newly created class. The `is_global` argument
defines whether the class will be global or non-global (see the definition
of "global" above).
Symbolic functions that are defined using Python `class` statement,
are always global.

An example of defining function symbol:
```
>>> Foo = BasicFunctionType('Foo')
>>> Foo(1,2)
Foo(1, 2)
```

If function symbols and their instances can be used in arithmetic
operations then use `FunctionType` (defined in `sympy.arithmetic.function`)
instead of `BasicFunctionType`. For example,
```
>>> mysin = FunctionType('mysin', Sin)
>>> mysin(0)
0
>>> mysin(1)+2
mysin(1) + 2
>>> Cos+mysin
Cos + mysin
>>> (Cos+mysin)(3)
mysin(3) + Cos(3)
```

# Defining lambda functions #

The `sympy.core.function` modules defines `BasicLambda` (derived from
`Composite` and Callable) that can be used to create new lambda
functions:
```
>>> x = BasicSymbol('x')
>>> y = BasicSymbol('y')
>>> l = BasicLambda((x,y),x)
>>> l(1,x)
1
```

If a lambda function or its expression can be used in arithmetic operations
the use `Lambda` class (defined in `sympy.arithmetic.function`) instead
of `BasicLambda`:
```
>>> x = Symbol('x')
>>> l = Lambda(x, 1+x)
>>> l(3-x)
4 - x
>>> f = Sin + l
>>> f
Lambda((_x,), 1 + _x) + Sin
>>> f(x)
Sin(x) + 1 + x
```