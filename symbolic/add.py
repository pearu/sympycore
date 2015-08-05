"""
Author: Pearu Peterson <pearu.peterson@gmail.com>
Created: 2006
"""

__all__ = ['Add']

from base import Symbolic, CommutativeSequence
from base import RelationalMethods, ArithmeticMethods, FunctionalMethods

def flatten_add_sequence(seq):
    """
    n + m + .. -> (n+m) + .., nm, are numbers
    (a+b+..) + (c+d+..) -> a+b+c+d+..
    (n*a) + (m*a) -> (n+m)*a, n,m are numbers
    0 + a + .. -> a + ..
    1*a + b + .. -> a + b + ..
    """
    coeff = Symbolic.Zero()
    seq = list(seq)
    terms = {}
    lambda_args = None
    while seq:
        t = seq.pop(0)
        lambda_args, t = Symbolic.process_lambda_args(lambda_args, t)
        if isinstance(t, Symbolic.Number):
            coeff += t
            continue
        if isinstance(t, Symbolic.Add):
            coeff += t.coeff
            seq.extend(list(t.seq))
            continue
        if isinstance(t, Symbolic.Mul):
            c = t.coeff
            if isinstance(c, Symbolic.One):
                s = t
            else:
                s = Symbolic.Mul(*t.seq)
        else:
            c = Symbolic.One()
            s = t
        assert not isinstance(s, Symbolic.Number)
        if terms.has_key(s):
            terms[s] += c
        else:
            terms[s] = c

    termseq = []
    for s,c in terms.items():
        if isinstance(c, Symbolic.Zero):
            continue
        if isinstance(c, Symbolic.One):
            termseq.append(s)
        else:
            termseq.append(Symbolic.Mul(c,s))

    if lambda_args is not None:
        return Symbolic.Lambda(*(lambda_args+(Add(coeff, *termseq),))), []

    return coeff, termseq


class Add(RelationalMethods, ArithmeticMethods, FunctionalMethods,
          CommutativeSequence):
    """ Represents sums a + b + c + ...
    """

    ###########################################################################
    #
    # Constructor methods
    #

    identity = 0
    flatten_sequence = staticmethod(flatten_add_sequence)

    def eval_power(base, exponent):
        return

    ############################################################################
    #
    # Informational methods
    #

    def get_precedence(self): return 40

    ###########################################################################
    #
    # Transformation methods
    #


    def tostr(self, level=0):
        precedence = self.get_precedence()
        coeff = self.coeff
        l = []
        if coeff!=self.identity:
            l.append(coeff.tostr(precedence))
        for factor in self.seq:
            f = factor.tostr(precedence)
            if f.startswith('-'):
                l.extend(['-',f[1:]])
            else:
                l.extend(['+',f])
        if l[0]=='+':
            l.pop(0)
        s = ' '.join(l)
        if precedence <= level:
            return '(%s)' % (s)
        return s
   
    ############################################################################
    #
    # Functional methods
    #

    def __call__(self, *args):
        """
        (f+g)(x) -> f(x) + g(x)
        """
        return Add(*[f(*args) for f in self.astuple()[1:]])
    
    def calc_diff(self, *args):
        if not args: return self.calc_diff
        return Add(*[f.diff(*args) for f in self.astuple()[1:]])

    def calc_integrate(self, *args):
        if not args: return self.calc_integrate
        return Add(*[f.integrate(*args) for f in self.astuple()[1:]])

#
# End of Add class
#
################################################################################

Symbolic.Add = Add
