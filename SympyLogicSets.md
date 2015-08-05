**This page is obsolete**

# The `BasicSet` class #

All symbolic set classes have a base class `BasicSet` (derived from Basic)
that defined the following default methods to set classes:

  * `superset(self)` property method should return a container set of `self`. The `superset` property is used in computing complementary set of a set, for instance.

  * `domain(self)` property method should return a predefined set symbol that includes `self`. For number sets it can be one of the following instances: `Complexes`, `Reals`, `Rationals`, `Integers`.

  * `try_element(self, other)` method should return truth value of the statement _`other` is an element of a set `self`_ or `None` if the statement cannot be evaluated.

  * `try_subset(self, other)` method should return truth value of the statement _`other` is a subset of a set `self`_ or `None` if the statement cannot be evaluated. Derived classes should use the following template when redefining `try_subset` method:
```
def try_subset(self, other):
    # evaluate `other` is subset of `self` and return truth value
    ..
    return BasicSet.try_subset(self, other)
```
> where `BasicSet.try_subset(..)` method implements default support for the case where `other` is a `Set` instance.

  * `try_union(self, other)` method should evaluate the union of `self` and `other` sets or return `None` if no evaluation can be carried out.

  * `try_intersection(self, other)` method should evaluate the intersection of `self` and `other` sets or return `None` if no evaluation can be carried out.

  * `try_difference(self, other)` method should evaluate the set difference operation of `self` and `other` sets or return `None` if no evaluation can be carried out.

  * `try_complementary(self, superset)` method should evaluate the complementary set of `self` within `superset` or return `None` if no evaluation can be carried out.



## Set symbols ##

The `sympy.logic.sets.symbol` module defines symbolic set symbol base class `SetSymbol`
(derived from `BasicSet` and `BasicSymbol`) and singleton classes `UniversalSet` and
`EmptySet`. The singletons are exposed as `Universal` and `Empty` variables.

## Set function symbols ##

The `sympy.logic.sets.function` module defines `SetFunction` class (derived from
`BasicSet` and `BasicFunction`) that is used as a base class to symbolic set functions.

## Sets of symbolic objects ##

The `sympy.logic.sets.set` module defines `Set` class (derived from `BasicSet`,
`Composite`, and `frozenset`) to construct a set of symbolic objects.

## Set operations ##

The `sympy.logic.sets.operations` module defines the following
symbolic set operation functions:
  * `Union(set1[,set2,..])` - represents an union of sets.
  * `Intersection(set1[,set2,..])` - represents an intersection of sets.
  * `Difference(set1, set2)` - represents a [set difference](http://en.wikipedia.org/wiki/Complement_(set_theory)) operation.
  * `Complementary(set, superset=None)` - represents a complementary set within `superset`. By default `superset = set.superset`.

## Set predicate functions ##

The `sympy.logic.sets.predicate` modules defines the following symbolic
predicate functions on sets:
  * `Element(obj, set)` - represents the statement _`obj` is an element of the `set`_.
  * `Subset(obj, set)` - represents the statement _`obj` is a subset of the `set`_.