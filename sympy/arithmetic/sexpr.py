"""
This module defines arithmetic operations and expand
function for s-expressions. The following functions are defined:
  add(lhs, rhs)
  mul(lhs, rhs)
  power(base, intexp)
  expand(expr)
  tostr(expr)
with s-expression arguments (except intexp that must be Python integer)
and return values. The following s-expressions are supported:
  (SYMBOLIC, <object>)
  (NUMBER, <number object>)
  (TERMS, frozenset([(<term1>, <coeff1>), ...])) where <coeffs> are numbers
  (FACTORS, frozenset([(<base1>, <exp1>), ...])) where <exps> are integers
where <object> must be an immutable object that supports __eq__ with other
similar objects, <number object> must support arithmetic operations with
Python integers, <terms> and <bases> must be s-expressions.

Efficency and easy translation to C code has been kept in mind while writting
the code below.
"""

__all__ = ['add', 'mul', 'pow', 'expand', 'tostr']

from ..core.sexpr import NUMBER, SYMBOLIC, TERMS, FACTORS

# output functions:
def parenthesis_in_mul(t):
    if t[0]==TERMS:
        return True
    if t[0]==NUMBER:
        return t[1] < 0 or t[1].__class__.__name__ == 'Fraction'
    return False

def tostr(expr, apply_parenthesis = False):
    s = expr[0]
    if s==TERMS:
        r = ' + '.join(['%s*%s' % (c, tostr(t)) for t,c in expr[1]])
    elif s==FACTORS:
        r = ' * '.join(['%s**%i' % (tostr(t, parenthesis_in_mul(t)), c) for t,c in expr[1]])
    else:
        r = str(expr[1])
    if apply_parenthesis:
        r = '(%s)' % (r)
    return r

# arithmetic functions:

zero = (NUMBER, 0)
one = (NUMBER, 1)

def add_inplace_dict_terms(d, rhs, p):
    for t,c in rhs[1]:
        b = d.get(t)
        if b is None:
            d[t] = c * p
        else:
            c = b + c * p
            if c==0:
                # XXX: check that t does not contain oo or nan
                del d[t]
            else:
                d[t] = c 
    return

def add_inplace_dict_number(d, rhs, p):
    return add_inplace_dict_terms(d, (TERMS, [(one, rhs[1])]), p)

def add_inplace_dict_nonterms(d, rhs, p):
    return add_inplace_dict_terms(d, (TERMS, [(rhs, 1)]), p)

def mul_inplace_dict_factors(d, rhs, p):
    for t,c in rhs[1]:
        b = d.get(t)
        if b is None:
            d[t] = c * p
        else:
            c = b + c * p
            if c==0:
                # XXX: check that t does not contain nan
                del d[t]
            else:
                d[t] = c
    return

def terms_dict_to_expr(d):
    if not d:
        return zero
    if len(d)==1:
        t, c = d.items()
        if c==1:
            return t
    return (TERMS, frozenset(d.items()))

def factors_dict_to_expr(d):
    if not d:
        return one
    if len(d)==1:
        t, c = d.items()
        if c==1:
            return t
    return (FACTORS, frozenset(d.items()))

def add_terms_terms(lhs, rhs):
    d = dict(lhs[1])
    add_inplace_dict_terms(d, rhs, 1) # XXX: optimize 1
    return terms_dict_to_expr(d)

def add_terms_number(lhs, rhs):
    # XXX: optimize
    return add_terms_terms(lhs, (TERMS, [(one, rhs[1])]))

def add_terms_nonterms(lhs, rhs):
    # XXX: optimize
    return add_terms_terms(lhs, (TERMS, ((rhs, 1),)))

def add_nonterms_nonterms(lhs, rhs):
    t1 = lhs[1]
    t2 = rhs[1]
    if t1==t2:
        return (TERMS, frozenset([(lhs, 2)]))
    return (TERMS, frozenset([(lhs, 1), (rhs, 1)]))

def add_number_number(lhs, rhs):
    return (NUMBER, lhs[1] + rhs[1])

def add_nonterms_number(lhs, rhs):
    return (TERMS, frozenset([(lhs, 1), (one, rhs[1])]))

def add(lhs, rhs):
    """ Add two s-expressions.
    """
    s1, s2 = lhs[0], rhs[0]
    if s1==s2==NUMBER:
        return add_number_number(lhs, rhs)
    if s1==s2==TERMS:
        return add_terms_terms(lhs, rhs)
    if s1==TERMS:
        if s2==NUMBER:
            return add_terms_number(lhs, rhs)
        return add_terms_nonterms(lhs, rhs)
    if s2==TERMS:
        if s1==NUMBER:
            return add_terms_number(rhs, lhs)
        return add_terms_nonterms(rhs, lhs)
    if s1==NUMBER:
        return add_nonterms_number(rhs, lhs)
    if s2==NUMBER:
        return add_nonterms_number(lhs, rhs)
    return add_nonterms_nonterms(lhs, rhs)

def add_inplace_dict(d, rhs, p):
    """ Add s-expression multiplied with p to dictionary d.
    """
    s = rhs[0]
    if s==TERMS:
        add_inplace_dict_terms(d, rhs, p)
    elif s==NUMBER:
        add_inplace_dict_number(d, rhs, p)
    else:
        add_inplace_dict_nonterms(d, rhs, p)
    return

def mul_factors_factors(lhs, rhs):
    d = dict(lhs[1])
    mul_inplace_dict_factors(d, rhs, 1)
    return factors_dict_to_expr(d)

def mul_number_number(lhs, rhs):
    return (NUMBER, lhs[1] * rhs[1])

def mul_factors_number(lhs, rhs):
    return (TERMS, frozenset([(lhs, 1), (one, rhs[1])]))

def mul_factors_nonfactors(lhs, rhs):
    return mul_factors_factors(lhs, (FACTORS, [(rhs, 1)]))

def mul_nonfactors_number(lhs, rhs):
    return (TERMS, frozenset([(lhs, 1), (one, rhs[1])]))

def mul_nonfactors_nonfactors(lhs, rhs):
    t1 = lhs[1]
    t2 = rhs[1]
    if t1==t2:
        return (FACTORS, frozenset([(lhs, 2)]))
    return (FACTORS, frozenset([(lhs, 1), (rhs, 1)]))

def expand_mul_terms_terms(lhs, rhs):
    # lhs, rhs must be expanded
    d = dict()
    for t1,c1 in lhs[1]:
        for t2,c2 in rhs[1]:
            t = mul(t1,t2)
            c = c1 * c2
            add_inplace_dict_terms(d, t, c)
    return terms_dict_to_expr(d)

def expand_mul_terms_nonterms(lhs, rhs):
    # lhs, rhs must be expanded
    d = dict()
    for t,c in lhs[1]:
        add_inplace_dict(d, mul(t, rhs), c)
    return terms_dict_to_expr(d)

def expand_mul(lhs, rhs):
    # lhs, rhs must be expanded
    s1, s2 = lhs[0], rhs[0]
    if s1==s2==TERMS:
        return expand_mul_terms_terms(lhs, rhs)
    if s1==TERMS:
        return expand_mul_terms_nonterms(lhs, rhs)
    if s2==TERMS:
        return expand_mul_terms_nonterms(rhs, lhs)
    return mul(lhs, rhs)

def mul(lhs, rhs):
    """ Multiply two s-expressions.
    """
    s1, s2 = lhs[0], rhs[0]
    if s1==s2==FACTORS:
        return mul_factors_factors(lhs, rhs)
    if s1==s2==NUMBER:
        return mul_number_number(lhs, rhs)
    if s1==FACTORS:
        if s2==NUMBER:
            return mul_factors_number(lhs, rhs)
        return mul_factors_nonfactors(lhs, rhs)
    if s2==FACTORS:
        if s1==NUMBER:
            return mul_factors_number(rhs, lhs)
        return mul_factors_nonfactors(rhs, lhs)
    if s2==NUMBER:
        return mul_nonfactors_number(lhs, rhs)
    if s1==NUMBER:
        return mul_nonfactors_number(rhs, lhs)
    return mul_nonfactors_nonfactors(lhs, rhs)

def power(base, exp):
    """ Find a power of an s-expression over integer exponent.
    """
    assert isinstance(exp, int),`type(exp)`
    s = base[0]
    if s==NUMBER:
        return (NUMBER, base[1] ** exp)
    if s==TERMS:
        if len(base[1])==1:
            t,c = list(base[1])[0]
            return mul(power(t, exp), (NUMBER,c ** exp))
    if s==FACTORS:
        d = dict()
        mul_inplace_dict_factors(d, rhs, exp)
        return factors_dict_to_expr(d)
    return (FACTORS, frozenset([(base, exp)]))

def expand_nonterms(expr):
    return expr

def expand_terms(expr):
    d = dict()
    for t,c in expr[1]:
        add_inplace_dict(d, expand(t), c)
    return terms_dict_to_expr(d)


def expand_factors(expr):
    s = list(expr[1])
    if len(s)==1:
        t, c = s[0]
        t = expand(t)
        if t[0]==TERMS and c>1:
            return expand_add_power(t, c)
        return (FACTORS, frozenset(((t, c),)))
    if len(s)==2:
        return expand_mul(expand(s[0]), expand(s[1]))
    lhs = expand(s[0])
    rhs = expand((FACTORS,frozenset(s[1:])))
    return expand_mul(lhs, rhs)

def expand(expr):
    s = expr[0]
    if s==TERMS:
        return expand_terms(expr)
    if s==FACTORS:
        return expand_factors(expr)
    return expr
