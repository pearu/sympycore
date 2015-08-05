# News #
  * 23 May, 2011 - Published a [paper](http://www.biomedcentral.com/1752-0509/5/81) on SteadyStateFluxAnalysis.
  * 26 Mar, 2009 - Pearu [slides](http://sympycore.googlecode.com/files/CSE09_pearu_slides.pdf) in [SIAM Conference on Computational Science and Engineering](http://www.siam.org/meetings/cse09/)
  * 27 Aug, 2008 - Pearu [slides](http://sympycore.googlecode.com/files/PearuEuroScipy08Slides.pdf) in [EuroScipy 2008](http://www.scipy.org/EuroSciPy2008)
  * 7 Apr, 2008 - Review conversation methods: ReviewConversionMethods3
  * 5 Apr, 2008 - Introduced new algebras: Set, FunctionRing, Differential
  * 3 Apr, 2008 - Review function support: FunctionSupportIdeas
  * 1 Apr, 2008 - Implemented And, Or, Not. Improved boolean expression support.
  * 15 Mar, 2008 - Reviewing matrix support: MatrixSupportIdeas
  * 10 Mar, 2008 - Introduced SymbolicEquality context where `__eq__` and `__ne__` methods would return Logic instance.
  * 6 Mar, 2008 - Added pickling support to Expr.
  * 5 Mar, 2008 - All algebra classes are derived from `Expr` class holding a pair.
  * 2 Mar, 2008 - Implemented extension type `Pair` giving 1.5-2x speed up.
  * 29 Feb, 2008 - [SympyCore version 0.1 released](ReleaseNotes0_1.md)

[Older news](OldNew.md)

# SympyCore #

The aim of the _SympyCore_ project
is to seek out new high [Performance](Performance.md) solutions to represent and manipulate symbolic
expressions in the [Python](http://www.python.org) programming language, and to try out
new symbolic models to achive fundamentally consistent
and sufficiently general symbolic model that would be easy to
extend to a Computer Algebra System (CAS).

See [SympyCore Demo](http://sympycore.googlecode.com/svn/trunk/doc/html/demo0_1.html) and [SympyCore User's Guide](http://sympycore.googlecode.com/svn/trunk/doc/html/usersguide.html) for examples. Various performance improvements are reported in [Performance History](http://code.google.com/p/sympycore/wiki/PerformanceHistory) and [SympyCore Benchmark](http://cens.ioc.ee/~pearu/sympycore_bench/) sites.

Sympycore is inspired by many attempts to implement CAS for Python and it is created to fix [SymPy](http://sympy.googlecode.com) performance and robustness issues. Sympycore does not yet have nearly as many features as SymPy. Our goal is to work on in direction of merging the efforts with the SymPy project in the future.
21 Oct 2011 update: Recent comments in SymPy issues list indicate that this goal is unrealistic because the projects have diverged so much.


---


**Question:** What is the main difference between SympyCore and SymPy projects?

**Answer:** SympyCore is a research project while SymPy is a software project.


---


# Usage #

Sympycore package is avaliable for [download](http://code.google.com/p/sympycore/downloads/list) as a [gzipped tar archive](http://sympycore.googlecode.com/files/sympycore-0.1.tar.gz) and as a [Windows binary installer](http://sympycore.googlecode.com/files/sympycore-0.1.win32.exe).
To install sympycore from an archive, unpack the tar file
and run the following command inside `sympycore-<VERSION>` directory:
```
  python setup.py install
```

The development code is available in the
[SVN repository](http://sympycore.googlecode.com/svn/).
Non-members can check out `sympycore` using the command (see
[Source](http://code.google.com/p/sympycore/source) for more information):
```
svn checkout http://sympycore.googlecode.com/svn/trunk/ sympycore-svn
```
Use `python setup.py install` to install sympycore or add the location of checked out
sympycore to `PYTHONPATH` to make it available for python import. Note that starting
from version 0.2, sympycore implements some features in C for speed. However, parallel
to that, pure python versions of these features are provided in case one cannot
build the provided extension modules. To build the extension modules inside
sympycore source tree, use one of the following commands:
```
  python setup.py build_ext --inplace
  python setup.py build_ext --inplace --compiler=mingw32  # when using MinGW compiler on windows
```


Import sympycore with
```
>>> from sympycore import *
>>> a,b=map(Symbol,'ab')
>>> (a+b)**3
Calculus('(a + b)**3')
>>> ((a+b)**3).diff(a)
Calculus('3*(a + b)**2')
>>> ((a+b)**3).diff(a).expand()
Calculus('3*a**2 + 3*b**2 + 6*a*b')
```
See [Documentation](Documentation.md) page for SympyCore User's Guide as well as other documentation bits.

To run sympycore tests without installing it, execute:
```
python setup.py [ build_ext --inplace [--compiler=mingw32] ] test [--coverage | --nose-args='...']
```
in sympycore source directoryl.

To test installed sympycore, run
```
>>> from sympycore import *
>>> test(nose_args='...')
```

# Feedback and bug reports #

You can report bugs at the [Sympycore Issue Tracker](http://code.google.com/p/sympycore/issues/list). Any feedback can also be sent to [SympyCore mailing list](http://groups.google.com/group/sympycore).