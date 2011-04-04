
import sympycore

def obj2num(s, abs_tol=1e-16):
    if isinstance(s, str):
        f = eval(s)
    else:
        f = s
    #return float(f) # will induce numerical errors and incorrect rank for GJE algorithm.
    i = int (f)
    if i==f:
        return i
    return sympycore.f2q(f, abs_tol)
