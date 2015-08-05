  * Fix Pow to handle all basic cases **Done**

  * Some more unit tests for basic algebra (e.g. everything in test\_arit.py)

  * .has **Done**

  * Substitution **Done**

  * Pattern matching **Done**

  * Differentiation **Done**

  * Integration **Done** (handling expanded polynomials is enough for now)

  * Basic support for exp, log and trigonometric functions - **Done** except for things like exp(log(x)); differentiation - **Done**

  * Clean up obsolete packages **Done**

  * evalf (using mpmath) **Done** (needs improvement, but not urgent)

  * Fix `oo ** oo` etc **Done**

  * Handle `((-1)**fraction) <operation> extended number`.

  * Support for multivariate functions, including differentiation **Done**.

  * Users manual. **Work-in-progress**

  * Calculus('sin(x)') - recognize sin as function. **Done**

## Proposal for library structure ##

```
  core.py        - defines Basic, classes
  /arithmetic/
    numbers.py   - implements Fraction, Float, Complex
    factoring /  - basic number theory
  /basealgebra/
    algebra.py   - defines BasicAlgebra
    ring.py      - defines CommutativeRing, later also NCommutativeRing
    pairs.py     - defines CommutativeRingWithPairs
    primitive.py - defines PrimitiveAlgebra
  /calculus/
    algebra.py   - defines Calculus
    constants.py - defines Constant for pi, E
    /functions/
       elementary.py - defines exp, log, sin, cos, tan, cot
       ..
    /limits/
    /integration/
    /rewriting/
      advanced simplification, etc
    /solvers/
  /logic/
    sets.py - defines SetAlgebra
    symbolic.py - defines BooleanAlgebra
    predicates and set algebra. These are independent of each other and
    may be they should be separate packages: setalgebra, booleanalgebra.
  /matrices/
    algebra.py - defines MatrixAlgebra
  /polynomials/
    algebra.py - defines PolynomialAlgebra, contains symbols
    univariate.py - defines UnivariatePolynomial, fast impl, no symbols
    multivariate.py - defines MultivariatePolynomila, fast impl, no symbols
  /functional/
    algebra.py - defines FunctionsRing (better name?), operators?
    algebra of functions. perhaps also algebra of differential and integral operators
  /physics/
    algebra.py - defines UnitAlgebra
```

(Note that the three most important packages form a-b-c at the top. This can be instructive for someone who browses the code for the first time. If we adopt these names, we should set a rule that no other package name may start with a-c :-)