from core import *
from logic import *
from arithmetic import *
from functions import *
from calculus import *

# expose predefined objects to sympy namespace
for _n,_v in objects.iterNameValue():
    exec '%s = _v' % _n

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
    stats.print_stats(40)
    return stats
