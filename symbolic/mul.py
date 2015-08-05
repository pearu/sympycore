"""
Author: Pearu Peterson <pearu.peterson@gmail.com>
Created: 2006
"""
__all__ = ['Mul']

from base import Symbolic, CommutativeSequence
from base import RelationalMethods, ArithmeticMethods, FunctionalMethods

def flatten_mul_sequence(seq):
    """
    n * m * a * .. -> (n*m) * a * .., n,m are numbers
    (a * b *..) * (d * c * ..) -> a * b * c * d * ..
    (-I) * a * ..  -> -1 * I * a * ..
    a**c * a**d -> a**(c + d)
    a ** 0 * b * .. -> b * ..
    a ** 1 * b * .. -> a * b * ..
    0 * a * b * .. -> 0
    n * (a + b + ..) -> n * a + n * b + ..
    """
    coeff = Symbolic.One()
    seq = list(seq)
    powers = {}
    lambda_args = None
    while seq:
        t = seq.pop(0)
        lambda_args, t = Symbolic.process_lambda_args(lambda_args, t)
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
        coeff, powseq = Symbolic.One(),[Symbolic.Add(*[coeff*f for f in powseq[0].astuple()[1:]])]

    if lambda_args is not None:
        return Symbolic.Lambda(*(lambda_args+(Mul(coeff, *powseq),))), []
    
    return coeff, powseq


class Mul(RelationalMethods, ArithmeticMethods, FunctionalMethods,
          CommutativeSequence):
    """ Represents products a * b * c * ...
    """

    ###########################################################################
    #
    # Constructor methods
    #

    identity = 1
    flatten_sequence = staticmethod(flatten_mul_sequence)
    ops = '*/'

    def eval_power(base, exponent):
        if isinstance(exponent, Symbolic.Number):
            if isinstance(exponent, Symbolic.Integer):
                return Mul(*[s**exponent for s in base.astuple()[1:]])
            if not isinstance(base.coeff, Symbolic.One):
                return base.coeff ** exponent * Mul(*base.seq) ** exponent
        return

    ############################################################################
    #
    # Informational methods
    #

    def get_precedence(self): return 50

    ###########################################################################
    #
    # Transformation methods
    #

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
            if coeff.is_negative():
                r = '-' + (-coeff).tostr(this_precedence-1) + delim + r
            else:
                r = coeff.tostr(this_precedence-1) + delim + r
        if this_precedence<=upper_precedence:
            return '(%s)' % r
        return r

    def calc_expanded(self):
        """
        (a + b + ..) * c -> a * c + b * c + ..
        """
        seq = []
        for t in self.astuple()[1:]:
            t = t.expand()
            if not seq:
                if isinstance(t, Symbolic.Add):
                    seq = t.astuple()[1:]
                else:
                    seq.append(t)
            elif isinstance(t, Symbolic.Add):
                new_seq = []
                for f1 in seq:
                    for f2 in t.astuple()[1:]:
                        new_seq.append(f1 * f2)
                seq = new_seq
            else:
                seq = [f*t for f in seq]
        return Symbolic.Add(*seq)

    def calc_diff(self, *args):
        if not args: return self.calc_diff
        if len(args)>1: return self.calc_diff(args[0]).diff(*args[1:])
        terms = self.astuple()[1:]
        new_terms = []
        for i in range(len(terms)):
            t = terms[i].diff(*args)
            if isinstance(t, Symbolic.Zero):
                continue
            new_terms.append(Mul(t,*(terms[:i]+terms[i+1:])))
        return Symbolic.Add(*new_terms)

    def calc_integrate(self, *args):
        if not args: return self.calc_integrate
        if len(args)>1: return self.calc_integrate(args[0]).integrate(*args[1:])
        a = args[0]
        if isinstance(a, Symbolic.Range):
            v = a.coeff
        else:
            v = a
        expr, coeffs = [], []
        for t in self.astuple()[1:]:
            if v in t.free_symbols():
                expr.append(t)
            else:
                coeffs.append(t)
        if coeffs:
            return Mul(*coeffs) * Mul(*expr).integrate(v)
        if isinstance(a, Symbolic.Range):
            op = Symbolic.Integral(a.coeff, a.seq[0], a.seq[1])
        else:
            op = Symbolic.Integral(a) #+ IC(a)
        return Symbolic.Apply(op, self)

#
# End of Mul class
#
################################################################################

Symbolic.Mul = Mul
