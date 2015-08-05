
Instructions to update performance history wiki
===============================================

Step 1
------

Before running any scripts, gunzip all files in the current
directory and subdirectories::

  ./unpack.sh

Step 2
------

Find out what is the last revision that has results. Usually
this is listed in the first line of the sympycore_svn.log file.

Step 3
------

Compute new results using::

  cd  sympycore_svn/
  START_REVISION=<last revision from Step 2> python scan_svn.py
  cd ..

Step 4
------

Update sympycore_svn.log file::

  svn log -q http://sympycore.googlecode.com/svn/ > sympycore_svn.log

Step 5
------

Update sympy/sage results in show_results.py file using the output of::

  # make sure that sympy disables caching:
  export SYMPY_USE_CACHE=no
  cd hg/sympy
  # fix the backend name in main() call of run1test.py and run
  python run1test.py

Step 6
------

Generate plots::

  python show_results.py

Save the plot to sympy_performance_history.png file.


Step 7
------

Pack all log and pickle files and clean up sympycore_svn directory::

  ./pack.sh

Step 8
------

Commit results to SVN repository.
