"""SympyCore - An efficient pure Python Computer Algebra System.

See http://sympycore.googlecode.com/ for more information.
"""
__docformat__ = "restructuredtext"
__date__ = '2008'
__author__ = 'Pearu Peterson, Fredrik Johansson'
__license__ = 'New BSD License'

from .version import version as __version__

from .core import classes, defined_functions, DefinedFunction, Expr
from basealgebra import *
from arithmetic import *
from logic import *
from sets import *
from calculus import *
from polynomials import *
from matrices import *
from physics import *
from functions import *

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

# This function is taken from sympy (and originally sage?)
def var(s):
    """
    var('x y z') creates symbols x, y, z
    """
    import inspect
    frame = inspect.currentframe().f_back
    try:
        if not isinstance(s, list):
            s = s.split(" ")
        res = []
        for t in s:
            # skip empty strings
            if not t:
                continue
            sym = Symbol(t)
            frame.f_globals[t] = sym
            res.append(sym)
        res = tuple(res)
        if len(res) == 0:   # var('')
            res = None
        elif len(res) == 1: # var('x')
            res = res[0]
                            # otherwise var('a b ...')
        return res
    finally:
        # we should explicitly break cyclic dependencies as stated in inspect
        # doc
        del frame

sin = Function(Sin, Calculus, Calculus)
cos = Function(Cos, Calculus, Calculus)
tan = Function(Tan, Calculus, Calculus)
cot = Function(Cot, Calculus, Calculus)
exp = Function(Exp, Calculus, Calculus)
log = Function(Log, (Calculus, Calculus), Calculus)
ln = Function(Ln, Calculus, Calculus)


# Define test() method:

class _Tester:
        
    def test(self, nose_args=''):
        """ Run sympycore tests using nose.
        """
        import os
        import sys
        import nose
        d = os.path.dirname(os.path.abspath(__file__))
        cmd = '%s %s %s %s' % (sys.executable, nose.core.__file__, d, nose_args)
        print >>sys.stderr, 'Running %r' % cmd
        s = os.system(cmd)
        if s:
            print >>sys.stderr, "TESTS FAILED"

    def check_testing(self):
        import os, sys
        import nose
        d = os.path.dirname(os.path.abspath(__file__))
        if sys.argv[:2] == [nose.core.__file__, d]:
            self.show_config()

    def show_config(self):
        import os, sys, nose
        if 'sympycore.expr_ext' in sys.modules:
            s = 'compiled'
        else:
            s = 'pure'
        print >>sys.stderr, 'Python version: %s' % (sys.version.replace('\n',''))
        print >>sys.stderr, 'nose version %d.%d.%d' % nose.__versioninfo__
        print >>sys.stderr, 'sympycore version: %s (%s)' % (__version__, s)
        print >>sys.stderr, 'sympycore is installed in %s' % (os.path.dirname(__file__))
        mpmath = sys.modules['sympycore.arithmetic.mpmath']
        fn = os.path.join(os.path.dirname(mpmath.__file__), 'REVISION')
        l = ['mode=%s' % (mpmath.settings.MODE)]
        if mpmath.settings.MODE=='gmpy':
            gmpy = mpmath.settings.gmpy
            l.append('gmpy_version=%s' % (gmpy.version()))
        if os.path.isfile(fn):
            f = open(fn, 'r')
            l.append('revision=%s' % (f.read().strip()))
            f.close()
        else:
            rev = ''
        print >>sys.stderr, 'mpmath version: %s (%s)' % (mpmath.__version__, ', '.join(l))

_tester = _Tester()
_tester.check_testing()
test = _tester.test
del _Tester, _tester

