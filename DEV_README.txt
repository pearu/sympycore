
Upgrading mpmath
================

In sympycore/trunk directory run::

  svn propedit svn:externals sympycore

and edit the mpmath revision number in ``-r`` option. Run ``svn up``
and ``nosetests sympycore`` to test the new version of mpmath. When
all tests pass, commit the svn property changes.

The following mpmath revisions are known to work: 1046, 1240.

