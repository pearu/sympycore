"""SympyCore - An efficient pure Python Computer Algebra System.

See http://sympycore.googlecode.com/ for more information.
"""
__docformat__ = "restructuredtext"
__version__ = '0.2-svn'
__date__ = '2008'
__author__ = 'Pearu Peterson, Fredrik Johansson'
__license__ = 'New BSD License'

from .core import classes
from basealgebra import *
from arithmetic import *
from calculus import *
from polynomials import *
from matrices import *
from physics import *

import utils

def profile_expr(expr):
    """ Printout the profiler information for executing ``expr``.
    """
    import sys
    import hotshot, hotshot.stats
    prof = hotshot.Profile("/tmp/sympycore_stones.prof")
    frame = sys._getframe(1)
    g = frame.f_globals
    l = frame.f_locals
    def foo():
        exec expr in g,l
    prof.runcall(foo)
    prof.close()
    stats = hotshot.stats.load("/tmp/sympycore_stones.prof")
    #stats.strip_dirs()
    stats.sort_stats('time','calls','time')
    stats.print_stats(40)
    return stats
