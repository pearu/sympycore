
from ..utils import LE, LT, GT, GE, EQ, NE
from .algebra import Logic

def Eq(a, b):
    return Logic(EQ, (a,b))
def Ne(a, b):
    return Logic(NE, (a,b))
def Lt(a, b):
    return Logic(LT, (a,b))
def Le(a, b):
    return Logic(LE, (a,b))
def Gt(a, b):
    return Logic(GT, (a,b))
def Ge(a, b):
    return Logic(GE, (a,b))

