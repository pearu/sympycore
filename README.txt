
============================================================
SympyCore - an efficient pure Python Computer Algebra System
============================================================

:Authors:

  Pearu Peterson <pearu.peterson AT gmail DOT com>

  Fredrik Johansson <fredrik.johansson AT gmail DOT com>

:Website:

  http://sympycore.googlecode.com/

:License:

  New BSD License

History
=======

 * Version 0.1 released on February 29, 2008.

Download
========

The latest release can be downloaded from sympycore website.

The latest development code is available via SVN. To check it out,
run::

  svn checkout http://sympycore.googlecode.com/svn/trunk/ sympycore-svn
  cd sympycore-svn

Installation
============

To use sympycore, the following is required:

  * Python 2.5 or newer
  * optionally, a C/C++ compiler for compiling sympycore
  * nose for running sympycore tests

To install compiled sympycore, unpack the archive file, change to the
sympycore source directory ``sympycore-?.?*`` (that contains setup.py
file and sympycore directory), and run (requires C/C++ compiler)::

  python setup.py install

To install pure sympycore, copy sympycore source directory to Python
path or just add it to PYTHONPATH or sys.path.

To build and use compiled sympycore without installing it, run:: 

  python setup.py build_ext --inplace

Testing
=======

To test pure Python sympycore from source directory, run::

  python setup.py test

To test compiled sympycore from source directory, run::

  python setup.py build_ext --inplace test

To test installed sympycore, run::
  
  python -c 'from sympycore import test; test()'

Basic usage
===========

Import sympycore with

>>> from sympycore import *

that will provide classes like Symbol, Number, Calculus to construct
symbolic expressions:

>>> x = Symbol('x')
>>> y = Symbol('y')
>>> x + y
Calculus('x + y')

See the following demo page for more examples:

  http://sympycore.googlecode.com/svn/trunk/doc/html/demo0_2.html

Additional documentation, including SympyCore User's Guide and API
documentation, is available online in SympyCore website.

Help and bug reports
====================

You can report bugs at the sympycore issue tracker:

  http://code.google.com/p/sympycore/issues/list

SympyCore website contains links to sympycore mailing lists where one
can ask support requests and discuss general sympycore related topics.
Any comments and questions can be sent also to the authors.

