
__all__ = ['EXP_COEFF_DICT']

from .base import ArithmeticHead

def init_module(m):
    from .base import heads
    for n,h in heads.iterNameValue(): setattr(m, n, h)

class ExpCoeffDict(ArithmeticHead):
    """
    """

    def __repr__(self): return 'EXP_COEFF_DICT'

    def data_to_str_and_precedence(self, cls, (variables, exp_coeff_dict)):
        terms = []
        for exps in sorted(exp_coeff_dict, reverse=True):
            coeff = exp_coeff_dict[exps]
            if not isinstance(exps, tuple):
                # temporary hook for SPARSE_POLY head, remove if block when SPARSE_POLY is gone
                exps = (exps,)
            factors = []
            for var,exp in zip(variables, exps):
                if not isinstance(var, cls):
                    var = cls(SYMBOL, var)
                factors.append(cls(POW,(var, exp)))
            terms.append(cls(TERM_COEFF, (cls(MUL,factors), coeff)))
        return ADD.data_to_str_and_precedence(cls, terms)

EXP_COEFF_DICT = ExpCoeffDict()
