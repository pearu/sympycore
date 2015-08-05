"""
Author: Pearu Peterson <pearu.peterson@gmail.com>
Created: January 2007
"""
__all__ = ['NcMul']

from base import Symbolic, NonCommutativeSequence

def flatten_ncmul_sequence(seq):
    coeff = Symbolic.One()
    seq = list(seq)
    while seq and isinstance(seq[0], Symbolic.Number):
        coeff *= seq.pop(0)
    return [coeff, seq]
    powers = {}
    while seq:
        t = seq.pop()
        if isinstance(t, Symbolic.Number):
            coeff *= t
            continue
        if isinstance(t, Symbolic.Mul):
            coeff *= t.coeff
            seq.extend(list(t.seq))
            continue
        if isinstance(t, Symbolic.Power):
            b = t.base
            e = t.exponent
        else:
            if isinstance(t, Symbolic.NegativeImaginaryUnit):
                b = Symbolic.ImaginaryUnit()
                coeff = -coeff
            else:
                b = t
            e = Symbolic.One()
        if powers.has_key(b):
            powers[b] += e
        else:
            powers[b] = e
    powseq = []
    for b,e in powers.items():
        if isinstance(e, Symbolic.Zero):
            continue
        if isinstance(e, Symbolic.One):
            if isinstance(b, Symbolic.Number):
                coeff *= b
            else:
                powseq.append(b)
        else:
            powseq.append(Symbolic.Power(b,e))
    if isinstance(coeff, Symbolic.Zero):
        powseq = []
    if len(powseq)==1 and isinstance(powseq[0], Symbolic.Add):
        return Symbolic.One(),[Symbolic.Add(*[coeff*f for f in powseq[0].astuple()[1:]])]
    return coeff, powseq

class NcMul(NonCommutativeSequence):
    """ Represents noncommutative multiplication.
    """

    ###########################################################################
    #
    # Constructor methods
    #

    identity = 1
    flatten_sequence = staticmethod(flatten_ncmul_sequence)
    ops = '*/'

    def get_precedence(self): return 50

    def tostr(self, level=0):
        delim = ' * '
        this_precedence = self.get_precedence()
        upper_precedence = level
        coeff = self.coeff
        r = delim.join([s.tostr(this_precedence) for s in self.seq])
        if coeff==self.identity:
            pass
        elif coeff==-self.identity:
            r = '-' + r
        else:
            if coeff.numer < 0:
                r = '-' + (-coeff).tostr(this_precedence-1) + delim + r
            else:
                r = coeff.tostr(this_precedence-1) + delim + r
        if this_precedence<=upper_precedence:
            return '(%s)' % r
        return r

    def __call__(self, *args):
        """
        (2 * f)(x) -> 2 * f(x)
        (g * f)(x) -> g(f(x))
        """
        if not isinstance(self.coeff, Symbolic.One):
            return self.coeff * Symbolic.NcMul(*self.seq)(*args)
        return Symbolic.NcMul(*self.seq[:-1])(self.seq[-1](*args))

Symbolic.NcMul = NcMul
