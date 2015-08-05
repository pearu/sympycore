# Renames #

  * `CommutativeRingWithPairs` -> `CollectingField` **Done**
  * `EnableLogic` -> `SymbolicEquality`, enable symbolic `<`, `<=`, `>`, `>=` by default but when in `__str__` use disabled symbolic comparisons. **Done**
  * `FractionTuple` -> `mpq` **Done**, `Float` -> `mpf` **Done**, `Complex` -> `mpc` **Done**; maybe create high-level functions `Float`, `Complex` that return `Calculus` instances,

# Needs a review #

  * Pattern matching algorithm as a whole, improve efficiency and define rules
  * Substitution methods (usage of patterns)
  * `Expr` heads, make function heads work with `is` (create a wrapper singleton).

# Document #

  * User's Guide
  * Structure
  * Demo 0.2
  * API docs

# Implement #

  * Inplace sub and div methods
  * Multivariate polynom division
  * Polynomial methods
  * Matrix methods
  * Undefined functions support

# Develop #

  * Assumptions model

# Test #

  * Increase unit test coverage

# Other #

  * Upgrade mpmath **Done (using rev 415)**