from core import *
from logic import *
from arithmetic import *
from functions import *




def profile_expr(expr):
    import sys
    import hotshot, hotshot.stats
    prof = hotshot.Profile("/tmp/stones.prof")
    frame = sys._getframe(1)
    g = frame.f_globals
    l = frame.f_locals
    def foo():
        exec expr in g,l
    prof.runcall(foo)
    prof.close()
    stats = hotshot.stats.load("/tmp/stones.prof")
    stats.strip_dirs()
    stats.sort_stats('time','calls','time')
    stats.print_stats(20)
    return stats
