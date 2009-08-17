
__all__ = ['EXP_COEFF_DICT']

from .base import ArithmeticHead

from ..core import init_module, Pair, Expr
init_module.import_heads()
init_module.import_numbers()
init_module.import_lowlevel_operations()

@init_module
def _init(module):
    from ..arithmetic.number_theory import multinomial_coefficients
    module.multinomial_coefficients = multinomial_coefficients

class ExpCoeffDict(ArithmeticHead):
    """
    """

    def is_data_ok(self, cls, data):
        if type(data) is not Pair:
            return 'data must be Pair instance but got %r' % (type(data).__name__)
        variables, exps_coeff_dict = data.pair
        if type(variables) is not tuple:
            return 'data[0] must be tuple but got %r' % (type(variables).__name__)
        if type(exps_coeff_dict) is not dict:
            return 'data[1] must be dict but got %r' % (type(exps_coeff_dict).__name__)
        for exps, coeff in exps_coeff_dict.items():
            if type(exps) is not IntegerList:
                del exps_coeff_dict[exps]
                exps = IntegerList(exps)
                exps_coeff_dict[exps] = coeff
                #return 'data[1] keys must be IntegerList instances but got %r' % (type(exps).__name__)
        
    def _reevaluate(self, cls, (variables, exp_coeff_dict)):
        r = cls(self, Pair(variables, d))

    def __repr__(self): return 'EXP_COEFF_DICT'

    def data_to_str_and_precedence(self, cls, data):
        variables, exp_coeff_dict = data
        terms = []
        for exps in sorted(exp_coeff_dict, reverse=True):
            coeff = exp_coeff_dict[exps]
            if type(exps) is not IntegerList:
                # temporary hook for SPARSE_POLY head, remove if block when SPARSE_POLY is gone
                exps = IntegerList(exps)
            factors = []
            for var,exp in zip(variables, exps):
                if not isinstance(var, cls):
                    var = cls(SYMBOL, var)
                factors.append(cls(POW,(var, exp)))
            terms.append(cls(TERM_COEFF, (cls(MUL,factors), coeff)))
        return ADD.data_to_str_and_precedence(cls, terms)

    def to_lowlevel(self, cls, data, pair):
        variables, exp_coeff_dict = data.pair
        n = len(exp_coeff_dict)
        if n==0:
            return 0
        if n==1:
            exps, coeff = dict_get_item(exp_coeff_dict)
            if type(exps) is not IntegerList:
                # temporary hook for SPARSE_POLY head, remove if block when SPARSE_POLY is gone
                exps = IntegerList(exps)
            factors = []
            for var, exp in zip(variables, exps.data):
                if exp==0:
                    continue
                if not isinstance(var, cls):
                    var = cls(SYMBOL, var)
                if exp==1:
                    factors.append(var)
                else:
                    factors.append(cls(POW, (var, exp)))
            if not factors:
                return coeff
            term = MUL.new(cls, factors)
            return term_coeff_new(cls, (term, coeff))
        return pair

    def combine_variables(self, *seq):
        variables = set([])
        seq = list(seq)
        while seq:
            s = seq.pop(0)
            if isinstance(s, Expr):
                if s.head is SYMBOL:
                    variables.add(s.data)
                else:
                    variables.add(s)
            elif isinstance(s, str):
                variables.add(s)
            elif isinstance(s, (tuple, list)):
                seq.extend(s)
            elif s is None:
                pass
            else:
                raise TypeError('expected an expression or a sequence of expressions but got %n' % (type(s)))
        return tuple(sorted(variables))

    def make_exponent(self, expr, variables):
        i = list(variables).index(expr)
        exp = [0] * (i) + [1] + [0] * (len(variables)-i-1)
        return IntegerList(exp)

    def to_EXP_COEFF_DICT(self, cls, data, expr, variables = None):
        if variables is None:
            return expr
        evars, edata = data.pair
        if evars==variables:
            return expr
        variables = self.combine_variables(evars, variables)
        levars = list(evars)
        l = []
        for v in variables:
            try:
                i = levars.index(v)
            except ValueError:
                i = None
            l.append(i)
        d = {}
        for exps, coeff in edata.iteritems():
            new_exps = IntegerList([(exps[i] if i is not None else 0) for i in l])
            d[new_exps] = coeff
        return cls(self, Pair(variables, d))
    
    def add(self, cls, lhs, rhs):
        lvars, ldict = lhs.data.pair
        rhead, rdata = rhs.pair
        if rhead is not EXP_COEFF_DICT:
            rhs = rhead.to_EXP_COEFF_DICT(cls, rdata, rhs, lvars)
            rhead, rdata = rhs.pair
        rvars, rdict = rdata.pair
        if lvars == rvars:
            d = ldict.copy()
            dict_add_dict(cls, d, rdict)
            return cls(self, Pair(lvars, d))
        variables = tuple(sorted(set(lvars + rvars)))
        lhs = self.to_EXP_COEFF_DICT(cls, lhs.data, lhs, variables)
        rhs = self.to_EXP_COEFF_DICT(cls, rhs.data, rhs, variables)
        d = lhs.data.data.copy()
        dict_add_dict(cls, d, rhs.data.data)
        return cls(self, Pair(variables, d))

    def commutative_mul(self, cls, lhs, rhs):
        rhead, rdata = rhs.pair
        if rhead is NUMBER:
            return self.commutative_mul_number(cls, lhs, rdata)
        lvars, ldict = lhs.data.pair
        if rhead is EXP_COEFF_DICT:
            rvars, rdict = rdata.pair
            if lvars == rvars:
                d = {}
                exp_coeff_dict_mul_dict(cls, d, ldict, rdict)
                return cls(self, Pair(lvars, d))
        raise NotImplementedError(`self, rhs.head`)

    def commutative_mul_number(self, cls, lhs, rhs):
        lvars, ldict = lhs.data.pair
        if rhs==0:
            return cls(self, Pair(lvars, {}))
        if rhs==1:
            return lhs
        d = {}
        for exps, coeff in ldict.iteritems():
            d[exps] = coeff * rhs
        return cls(self, Pair(lvars, d))
    
    def pow(self, cls, base, exp):
        variables, exp_coeff_dict = base.data.pair
        if isinstance(exp, Expr) and exp.head is NUMBER and isinstance(exp.data, inttypes):
            exp = exp.data
        if isinstance(exp, inttypes):
            return self.pow_number(cls, base, exp)
        expr = cls(POW, (base, exp))
        variables = self.combine_variables(variables, expr)
        exps = self.make_exponent(expr, variables)
        return cls(self, Pair(variables, {exps:1}))

    def pow_number(self, cls, base, exp):
        variables, exp_coeff_dict = base.data.pair
        if isinstance(exp, inttypes):
            if exp==0:
                return cls(self, Pair(variables, {(0,)*len(variables):1}))
            if exp==1:
                return base
            if exp>1:
                exps_coeff_list = base.data.data.items()
                m = len(variables)
                mdata = multinomial_coefficients(len(exps_coeff_list), exp)
                d = {}
                for e,c in mdata.iteritems():
                    new_exps = IntegerList([0]*m)
                    new_coeff = c
                    for e_i, (exps,coeff) in zip(e, exps_coeff_list):
                        new_exps += exps * e_i
                        new_coeff *= coeff ** e_i
                    dict_add_item(cls, d, new_exps, new_coeff)
                return cls(self, Pair(variables, d))
        expr = cls(POW, (base, exp))
        variables = self.combine_variables(variables, expr)
        exps = self.make_exponent(expr, variables)
        return cls(self, Pair(variables, {exps:1}))

EXP_COEFF_DICT = ExpCoeffDict()
