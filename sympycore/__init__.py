from .core import Basic, classes
from basealgebra import *
from arithmetic import *
from calculus import *
from polynomials import *
from physics import *

def profile_expr(expr):
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
    stats.strip_dirs()
    stats.sort_stats('time','calls','time')
    stats.print_stats(40)
    return stats
