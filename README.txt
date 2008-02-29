
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

Download and installation
=========================

sympycore package requires Python 2.5 or newer.

The latest release can be downloaded from sympycore website.

To install sympycore, unpack the archive file and run::

  python setup.py install

The latest development code is available via SVN. To check it out,
run::

  svn checkout http://sympycore.googlecode.com/svn/trunk/ sympycore

Testing
=======

Make sure that sympycore directory is in python path (e.g. it should
be listed in sys.path or PYTHONPATH) and then run in the parent
directory of the sympycore source one of the following commands::

  nosetests sympycore
  py.test sympycore

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

  http://sympycore.googlecode.com/svn/trunk/doc/html/demo0_1.html

Additional documentation, including SympyCore User's Guide and API
documentation, is available online in SympyCore website.

Help and bug reports
====================

You can report bugs at the sympycore issue tracker:

  http://code.google.com/p/sympycore/issues/list

SympyCore website contains links to sympycore mailing lists where one
can ask support requests and discuss general sympycore related topics.
Any comments and questions can be sent also to the authors.
