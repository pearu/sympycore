We are proud to present a new Python package:

> sympycore - an efficient pure Python Computer Algebra System

Sympycore is available for download from

> http://sympycore.googlecode.com/

Sympycore is released under the New BSD License.

Sympycore provides very efficient data structures for representing
symbolic expressions and methods to manipulate them. Sympycore uses
a very clear algebra oriented design that can be easily extended.

Sympycore is a pure Python package with no external dependencies,
it requires Python version 2.5 or higher to run. Sympycore uses
[Mpmath](http://mpmath.googlecode.com) for fast arbitrary-precision
floating-point arithmetic that is included into sympycore package.

Sympycore is to our knowledge the most efficient pure Python
implementation of a Computer Algebra System. Its speed is comparable
to Computer Algebra Systems implemented in compiled languages. Some
comparison benchmarks are available in

  * http://code.google.com/p/sympycore/wiki/Performance

  * http://code.google.com/p/sympycore/wiki/PerformanceHistory

and it is our aim to continue seeking for more efficient ways
to manipulate symbolic expressions:

> http://cens.ioc.ee/~pearu/sympycore_bench/

Sympycore version 0.1 provides the following features:

  * symbolic arithmetic operations
  * basic expression manipulation methods: expanding, substituting, and pattern matching.
  * primitive algebra to represent unevaluated symbolic expressions
  * calculus algebra of symbolic expressions, unevaluated elementary functions, differentiation and polynomial integration methods
  * univariate and multivariate polynomial rings
  * matrix rings
  * expressions with physical units
  * SympyCore User's Guide and API Docs are available online.

Take a look at the demo for sympycore 0.1 release:

> http://sympycore.googlecode.com/svn/trunk/doc/html/demo0_1.html

However, one should be aware that sympycore does not implement many
features that other Computer Algebra Systems do. The version number 0.1
speaks for itself:)

Sympycore was inspired by many attempts to implement CAS for Python and it is created to fix SymPy performance and robustness issues. Sympycore does not yet have nearly as many features as SymPy. Our goal is to work on in direction of merging the efforts with the SymPy project in the near future.

Enjoy!

  * Pearu Peterson
  * Fredrik Johansson

Acknowledgments:

  * The work of Pearu Peterson on the SympyCore project is supported by a Center of Excellence grant from the Norwegian Research Council to Center for Biomedical Computing at Simula Research Laboratory.