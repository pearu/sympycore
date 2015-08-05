# Introduction #

In the following we consider how the performance of the
sympy packages has been changed in the projects Sympy Core
and SymPy over the time of their development. The SVN history
of both projects are used to produce the results.
For comparison, the performance results of other symbolic
manipulation packages such as symbolic, swiginac, Maxima are given.

# Some historical notes #

SymPy project was established by Ondrej Certik in autumn 2006
when he made first commit to SVN repository that contained a
python package called `sym` that he has developed in year 2005.
The project was inactive until February 2007.

During 2006 - early 2007 Pearu Peterson developed independetly
a python package [symbolic](http://sympycore.googlecode.com/svn/misc/symbolic/).

In February 2007 the development of SymPy became active again
and that resulted a python package called `sympy`.

In May-June 2007 Pearu joined the SymPy project and adapted
the `symbolic` package to use sympy interface as at the time
symbolic used a more efficient way to create symbolic objects.

After that, Pearu continued working on the branch called sympy-research
that was merged with the trunk in July-August 2007. This merge
was called the _painful_ one.

In the middle of September 2007 Pearu started to work on
another idea that looked promising for increasing the
performance even further. As a result, the branch sympy-sandbox
was created.

In the middle of October 2007 the sympy-sandbox forked to a
separated project, now called Sympy Core.
The aim of Sympy Core was to find most efficient
ways to implement CAS for Python and to resolve few fundamental
issues in sympy core such as assumptions and functions support.
The work is in-progress.

The first two-fold speedup in January 2008 was due to introducing
algebra package that implements the ideas from Fredrik Johansson research
on directadd5.py implementation. And the second two-fold speedup was
obtained by using another rational number implementation by Fredrik.

The 1.6x speedup in the middle of February 2008 that made sympycore
fastest system for this benchmark was due to using generated code
for arithmetic operations implemented by Pearu.

The 1.3x speedup in early March 2008 is due to introducing
extension type `Expr` that implements hash computation of
`frozenset(dict.items())` in C by Pearu.

The 1.08x slowdown in late March 2008 is due to cleaning up
the code that added some overhead. We'll need to see if we can
restore the original speed without sacrificing the code readability too much.

Sympycore is about 3.5x slower than Singular via Sage. The 3.5 seems to be
universal factor for comparing the speeds of C and pure Python solutions.

# Test case #

To measure the performance of Python CAS packages, we use
the following simple problem: transform the following expression
```
3 * (a * x + b * y + c * z)
```
to
```
3/2 * x + 2 * y + 12/5 * z
```
where `a=1/2`, `b=2/3`, `c=4/5` are pre-created fractions and
`x`, `y`, `z` are pre-created symbols.

The problem involves the following basic operations:
```
a * x -> Mul(1/2, x)
b * y -> Mul(2/3, y)
c * y -> Mul(4/5, z)
a * x + b * y + c * z -> Add(Mul(1/2, x), Mul(2/3, y), Mul(4/5, z))
3 * Mul(1/2, x) -> Mul(3/2, x)
3 * Mul(2/3, x) -> Mul(2, x)
3 * Mul(4/5, x) -> Mul(12/5, x)
3 * (a * x + b * y + c * z) -> Add(Mul(3/2, x), Mul(2, y), Mul(12/5, z))
```
Hence by measuring the performance of the above transformation
means measuring the effieciency of creating symbolic objects
and of arithmetic operations in general.

# Measuring performance #

In order to measure the performance of the test case, it is executed
`n=5000` times in row using timeit.Timer, the execution is repeated
three times and the best (shortest) time is used to compute the following measure:
```
number executions per second = n / time
```

## Caching ##

In order to measure the efficiency of basic operations in the test
case, each execution in the performance measurment must contain
the same number of operations as the first execution.

Hence, it is crucial that the caching is disabled when running the
test case.

# Results #

![http://sympycore.googlecode.com/svn/misc/performance_history/sympy_performance_history.png](http://sympycore.googlecode.com/svn/misc/performance_history/sympy_performance_history.png)

All scripts to produce the above plot as well as computed data are available in http://sympycore.googlecode.com/svn/misc/performance_history/

## Comments ##

  * The SVN history shows that all new developments start with a high performance and in time it decreases. This is related to the fact that development adds new features that means extra code and longer execution time.

  * A nice overview about the performance results on expanding expressions is given in http://ondrejcertik.blogspot.com/2008/01/sympysympycore-pure-python-up-to-5x.html

  * The fact that Maxima(GCL) performs better than swiginac is because swiginac has an overhead in the interface to GiNaC that the given test case uses alot. The expand tests in the link above show that swiginac is still much faster than Maxima(GCL) as there more time is spent in the underlying library compared to the time spent in the interface.

  * The sympycore results are produced with pure python code. There are well-defined modules in sympycore that are responsiple for its performance in arithmetic operations and these modeles are design to be easily translated to a C codes. So, there are realistic possibilities to improve sympycore performance.

  * More comments and discussion can be found in http://groups.google.com/group/sympy/browse_thread/thread/f5b0390f62c4943e