**This page is obsolete**

# Sets #

_Set_ is a collection of elements.

`sympy.logic.sets` defines symbolic data structures and functionality to support
representing the mathematical notion of a _set_ and performing operations with
sets within Python.

`sympy.arithmetic.sets` defines sets representing open, semi-open, and closed ranges
as well as sets of complex, real, rational, integer, and prime numbers.

## Defined sets ##

To construct a set of symbolic objects,
use `Set` class (that is derived from Python set).
Set instances are immutable objects.

To check if an object is in a set, use `Element` predicate:
```
>>> x=Symbol('x')
>>> y=Symbol('y')
>>> s=Set(1,x)
>>> s
Set(1, x)
>>> Element(1,s)
True
>>> Element(2,s)
False
>>> Element(x,s)
True
>>> Element(y,s)
False
```

## Symbolic sets ##

To construct a set symbol, use `SetSymbol` class.
```
>>> s=SetSymbol('s')
>>> s
s
>>> Element(x,s)
Element(x, s)
>>> Element(1,s)
Element(1, s)
```

## Predefined sets ##

`sympy.arithmetic.sets` defines several symbolic sets with predefined properties on their
elements:

  * `Complexes` is a `ComplexSet` instance and represents the field of complex numbers.
```
>>> Complexes
Complexes
>>> Element(2,Complexes)
True
>>> Element(I,Complexes)
True
>>> Element(x,Complexes)
Element(x, Complexes)
```
  * `Reals` is a `RealSet` instance and represents the field of real numbers.
  * `Rationals` is a `RationalSet` instance and represents the field of rational numbers.
  * `Integers` is a `IntegerSet` instance and represents the set of integers.
  * `Primes` is a `PrimeSet` instance and represents the set of positive prime integers: 2, 3, 5, 7, ..
```
>>> [i for i in range(20) if Element(i, Primes)]
[2, 3, 5, 7, 11, 13, 17, 19]
```
  * `Empty` is a `EmptySet` instance and represents the empty set.
  * `Universal` is a `UniversalSet` instance and represents the set of all objects.
```
>>> Complementary(Universal)
EMPTYSET
>>> Complementary(Empty)
UNIVERSALSET
>>> Element(Reals, Universal)
True
>>> Element(2, Universal)
True
```


## Constructing new sets ##

`sympy.logic.sets` and `sympy.arithmetic.sets` define the following set functions to construct new sets:

  * `Complementary(set, superset)` is a complementary set in superset
```
>>> Complementary(Integers, Rationals)
Integers^C
>>> Complementary(Integers, Reals)
Union(Integers^C, Rationals^C)
>>> Complementary(Primes, Reals)
Union(Complementary(P, Integers), Integers^C, Rationals^C)
```
  * `Positive(set)` is a set of positive numbers in a set.
  * `Negative(set)` is a set of negative numbers in a set.
```
>>> Zp = Positive(Integers)           # positive integers
>>> Zn = Negative(Integers)           # negative integers
>>> Zn0 = Complementary(Zp, Integers) # nonpositive integers
>>> [i for i in range(-10,10) if Element(i, Zp)]
[1, 2, 3, 4, 5, 6, 7, 8, 9]
>>> [i for i in range(-10,10) if Element(i, Zn)]
[-10, -9, -8, -7, -6, -5, -4, -3, -2, -1]
>>> [i for i in range(-10,10) if Element(i, Zn0)]
[-10, -9, -8, -7, -6, -5, -4, -3, -2, -1, 0]
>>> Positive(Primes)
Primes
>>> Negative(Primes)
EMPTYSET
```
  * `Shifted(set, s)` is a set of set elements that have been added s.
```
>>> Zp_2 = Shifted(Zp,2)
>>> [i for i in range(-10,10) if Element(i, Zp_2)]
[3, 4, 5, 6, 7, 8, 9]
>>> Zp_3 = Shifted(Zp,-3)
>>> [i for i in range(-10,10) if Element(i, Zp_3)]
[-2, -1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
```
  * `Divisible(set, d)` is a set of set elements that are divisible by d.
```
>>> Zp_d3=Divisible(Zp,3)
>>> [i for i in range(-10,10) if Element(i, Zp_d3)]
[3, 6, 9]
```

As an example, `sympy.arithmetic.sets` defines `Evens` and `Odds` set instances that
have the following definitions:
```
Evens = Divisible(Integers,2)
Odds = Complementary(Evens, Integers)
>>> [i for i in range(-10,10) if Element(i, Evens)]
[-10, -8, -6, -4, -2, 0, 2, 4, 6, 8]
>>> [i for i in range(-10,10) if Element(i, Odds)]
[-9, -7, -5, -3, -1, 1, 3, 5, 7, 9]
```

## Constructing ranges ##

`sympy.arithmetic.sets.ranges` defines 5 different functions to construct
ranges with different boundary conditions:

  * `RangeOO(a,b,set)` or `Range(a,b,set=Reals)` - represents open range `(a, b)` in `set`.
  * `RangeOC(a,b,set)` - represents semi-open range `(a, b]` in `set`.
  * `RangeCO(a,b,set)` - represents semi-open range `[a, b)` in `set`.
  * `RangeCC(a,b,set)` - represents closed range `[a, b]` in `set`.

```
>>> R=RangeCC(1,5,Integers)
>>> [i for i in range(-10,10) if Element(i, R)]
[1, 2, 3, 4, 5]
>>> RO=RangeCO(1,5,Integers)
>>> [i for i in range(-10,10) if Element(i, RO)]
[1, 2, 3, 4]
>>> RE=RangeCC(1,5,Evens)
>>> [i for i in range(-10,10) if Element(i, RE)]
[2, 4]
```

Ranges can be used as arguments Union, Minus, Intersection operations that
may lead to simplifications:
```
>>> Union(Range(-10,5),Range(0,10))
RangeOO(-10, 10, Reals)
>>> Union(Range(-10,5),Range(5,10))
Union(RangeOO(-10, 5, Reals), RangeOO(5, 10, Reals))
>>> Minus(Range(-10,5),Positive(Reals))
RangeOC(-10, 0, Reals)
>>> Intersection(Range(0,10), Range(3,15))
RangeOO(3, 10, Reals)
```

# Connection with [predicates](Predicate.md) #

Predicates `Element` and `Subset` are defined in `sympy.logic.sets` module:
  * `Element(<expr>, <set>)` to represent a statement _`<expr>` is an element of a `<set>`_.
  * `Subset(<subset>, <set>)` to represent a statement _`<subset>` is a subset of a `<set>`_.

```
>>> Element(2, Integers)
True
>>> Element(2.3, Integers)
False
>>> Subset(Set(2,3), RangeOO(0,10,Integers))
True
>>> Subset(Range(2,3), Range(1,5))
True
>>> Subset(Range(0,3), Range(1,5))
False
```