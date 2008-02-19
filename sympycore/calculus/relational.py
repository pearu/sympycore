from sympycore.arithmetic.numbers import numbertypes, realtypes, ExtendedNumber
from sympycore.calculus import Calculus, pi, E
from sympycore.calculus.algebra import Positive, Nonnegative
from sympycore.utils import NUMBER, ADD, MUL, POW

def is_number(x):
    return isinstance(x, numbertypes) or (isinstance(x, Calculus) \
        and x.head is NUMBER)

class Assumptions:

    def __init__(self, statements=[]):
        self.pos_values = []
        self.nonneg_values = []
        for stmt in statements:
            if stmt is True:
                continue
            if stmt is False:
                raise ValueError("got False as assumption")
            if isinstance(stmt, Positive):
                self.pos_values.append(stmt.a)
            elif isinstance(stmt, Nonnegative):
                self.nonneg_values.append(stmt.a)
            else:
                raise ValueError("unknown assumption type: " + repr(stmt))

    def __repr__(self):
        ps = [repr(Positive(a)) for a in self.pos_values]
        ns = [repr(Nonnegative(a)) for a in self.nonneg_values]
        return "Assumptions([%s])" % ", ".join(ps + ns)

    def __enter__(self):
        globalctx.assumptions = self

    def __exit__(self, *args):
        globalctx.assumptions = no_assumptions

    def check(self, cond):
        if isinstance(cond, (bool, type(None))):
            return cond
        if isinstance(cond, Positive): return self.positive(cond.a)
        if isinstance(cond, Nonnegative): return self.nonnegative(cond.a)
        raise ValueError

    def eq(s, a, b): return s.zero(a-b)
    def ne(s, a, b): return s.nonzero(a-b)
    def lt(s, a, b): return s.positive(b-a)
    def le(s, a, b): return s.nonnegative(b-a)
    def gt(s, a, b): return s.positive(a-b)
    def ge(s, a, b): return s.nonnegative(a-b)

    def negative(s, x):
        t = s.positive(x)
        if t is None:
            return t
        return not t

    def nonpositive(s, x):
        t = s.nonnegative(x)
        if t is None:
            return t
        return not t

    def zero(s, x):
        if is_number(x):
            return x == 0
        if s.positive(x) or s.negative(x):
            return False
        return None

    def nonzero(s, x):
        if is_number(x):
            return x != 0
        if s.positive(x) or s.negative(x):
            return True
        return None

    def positive(s, x):
        x = Calculus(x)
        if x.head is NUMBER:
            val = x.data
            if isinstance(x.data, realtypes):
                return val > 0
            if isinstance(x.data, ExtendedNumber) and x.direction:
                return x.direction > 0
        elif x.is_Add:
            args = x.as_Add_args()
            if any(s.positive(a) for a in args) and all(s.nonnegative(a) for a in args): return True
            if any(s.negative(a) for a in args) and all(s.nonpositive(a) for a in args): return False
        elif x.is_Mul:
            args = x.as_Mul_args()
            if any(not s.nonzero(a) for a in args):
                return None
            neg = sum(s.negative(a) for a in args)
            return (neg % 2) == 0
        elif x.is_Pow:
            b, e = x.as_Pow_args()
            if s.positive(b) and s.positive(e):
                return True
        elif x == pi or x == E:
            return True
        if s.pos_values:
            # NOTE: this should check both x-p and x+p, i.e. bounds from both directions
            t1 = any(no_assumptions.nonnegative(x-p) for p in s.pos_values)
            t2 = any(no_assumptions.nonpositive(x-p) for p in s.pos_values)
            if t1 and not t2: return True
        return None

    def nonnegative(s, x):
        x = Calculus(x)
        if x.head is NUMBER:
            val = x.data
            if isinstance(x.data, realtypes):
                return val >= 0
            if isinstance(x.data, ExtendedNumber) and x.direction:
                return x.direction > 0
        elif x.is_Add:
            args = x.as_Add_args()
            if all(s.nonnegative(a) for a in args): return True
            if all(s.negative(a) for a in args): return False
        elif x.is_Mul:
            args = x.as_Mul_args()
            if all(s.nonnegative(a) for a in args): return True
        elif x.is_Pow:
            b, e = x.as_Pow_args()
            if s.nonnegative(b) and s.nonnegative(e):
                return True
        elif x == pi or x == E:
            return True
        if s.nonneg_values:
            # NOTE: this should check both x-p and x+p, i.e. bounds from both directions
            t1 = any(no_assumptions.nonnegative(x-p) for p in s.nonneg_values)
            t2 = any(no_assumptions.negative(x-p) for p in s.nonneg_values)
            if t1 and not t2: return True
        return None

no_assumptions = Assumptions([])

class GlobalContext(object):
    pass

globalctx = GlobalContext()

globalctx.assumptions = no_assumptions

is_positive = lambda e: globalctx.assumptions.positive(e)
