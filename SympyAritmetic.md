**This page is obsolete**

# Arithmetic methods #

The `sympy.arithmetics` module defines arithmetic methods
such as addition, multiplication, etc for Basic objects
that can be used as operants of arithmetic operations.
Such objects must be instances of `Number`, `Symbol`,
or `Function` classes.

The following basic arithmetic methods are defined:
  * `diff(self, *symbols)` returns a derivative of `self` with respect to symbols in `symbols`. The tuple `symbols` may contain an integer number, say `n`, after some `Symbol`  item to take the `n`-th derivative with respect to the corresponding symbol.

  * `try_power(self, exponent)` that should return an evaluated `self ** exponent` result or `None` if no evaluation is possible.

  * `try_derivative(self, s)` that should return a derivative of `self` with respect to symbol `s` or `None` if the derivative cannot be computed.

  * TOBEREMOVED(ise split instead): `as_factors(self)` - return `self` as a list of base-exponent pairs where all the absolute values of all exponets are different:
```
>>> sympify('4*x**2*y**-2').as_factors()
[(2*1/y*x, 2)]
```

  * TOBEREMOVED(use split instead): `as_terms(self)` - return `self` as a list of term-coefficient pairs where all the fractional parts of coefficients are different:
```
>>> sympify('2/3-x/3+y/2').as_terms()
[(y, 1/2), (2 - x, 1/3)]
```

  * `iterAdd(self)` - return an iterator such that `self == Add(*self.iterAdd())`.
  * `iterMul(self)` - return an iterator such that `self == Mul(*self.iterMul())`.
  * `iterPow(self)` - return an iterator such that if `it=list(self.iterPow())` then `self == it[0] ** it[1] ** .. ** it[-1]`.
  * `iterLogMul(self)` - return an iterator such that `Log(self) == Add(*self.iterLogMul())`.
  * `iterTermCoeff(self)` - return an iterator such that `self == Add(*[t*c for (t,c) in self.iterTermCoeff()])` where `c.is_Number==True and t.is_Number==False`.
  * `iterBaseExp(self)` - return an iterator such that `self == Mul(*[b**e for (b,e) in self.iterBaseExp()])`.
  * `as_term_coeff(self)` - return `(term, coeff)` such that `self==term * coeff` and `coeff.is_Number==True and term.is_Number==False`.
  * `as_base_exponent(self)` - return `(base, exponent)` such that `self == base ** exponent`.
  * `split(self,cls=self.__class__)` - return `(cls, iterobj)` such that `self==cls(*iterobj)`. Here `cls` can be one of the following classes: `Add`, `Mul`, `Pow`. (TODO: introduce similar split method also for BasicSet and BasicBoolean classes).

## Number classes ##

The `sympy.arithmetic.number` module implements
`Integer`, `Fraction`, and `Float` number classes
that are parts of the following class tree:
```
Number(NumberMethods, Atom)
  Real(Number)
    Float(Real, tuple)
    Rational(Real)
      Fraction(Rational, tuple)
      Integer(Rational, long)
```

## Symbol classes ##

The `sympy.arithmetic.symbol` defines classes `Symbol`,
`Dummy`, and `Wild`.

## Arithmetic operations ##

The following classes `Add`, `Mul`, and `Pow` are defined to
represent arithmetic operations like addition, multiplication, and
exponentation, respectively. All these classes are subclasses
of the `Function` class.

## Function classes ##

The `sympy.arithmetic.function` defines classes `FunctionType`,
`Function`, and `Lambda`.

### Defining new function symbols ###

For more general notes on defining new function symbols, see [BasicFunction](SympyCoreFunction.md).
Basic evaluation should be done in the class method `canonize(cls, args)`.

Arithmetic function symbols define the following methods:

  * `fdiff(obj, index=1)` that is [UniversalMethod](SympyCoreUtils.md) and returns a derivative function of the given arithmetic function. When redefining it, use the following template:
```
@UniversalMethod
def fdiff(obj, index=1):
    if isinstance(obj, BasicType):
        # return derivative function symbol with respect to index-th argument
    return obj._fdiff(index)
```
> where `Function._fdiff(obj, index=1)` implements differentiation chain rule to deal with expressions like `Sin(Cos).fdiff()` -> `-Cos(Cos) * Sin`.

If an arithmetic function does not redefine `fdiff` method but defines classmethod `fdiff1(cls)` then it will be used to compute the derivative function with respect to the first argument. Similarly, a function may define methods like `fdiff2`, `fdiff3`, etc that
should return derivatives with respect to the second, third, etc arguments, respectively.

The following example demonstrates how to define a new function `Sinc`,
how to carry out basic evaluation in `canonize` method,
and how to define new functions (`Sinc_1`) on fly:
```
class Sinc(Function):
    @classmethod
    def canonize(cls, (x,)):
        if x.is_Number:
            if x==0:
                return objects.one
            return Sin(x)/x
    @classmethod
    def fdiff1(cls):
        def canonize(cls, (x, )):
            if x.is_Number:
                if x==0:
                    return objects.zero
                return (Cos(x) - Sinc(x))/x
        attrdict = dict(
             canonize = classmethod(canonize)
        )
        return FunctionType('Sinc_1', attrdict=attrdict)

>>> x = Symbol('x')
>>> Sinc(0)
1
>>> Sinc.fdiff()
Sinc_1
>>> Sinc.fdiff()(0)
0
>>> Sinc(2)
Sin(2)/2
>>> Sinc.fdiff()(2)
-1/4*Sin(2) + 1/2*Cos(2)
```

## Set classes ##

For more general notes on set classes, see [BasicSet](SympyLogicSets.md).

The `sympy.arithmetic.sets` module defines classes for number sets like `ComplexSet`,
`RealSet`, `RationalSet`, `IntegerSet`, and `PrimeSet` (the instances of these
classes are singletons), set symbol classes, and functions for constructing open, semi-open, closed ranges.