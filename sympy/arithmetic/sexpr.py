"""
This module defines arithmetic operations and expand
function for s-expressions. The following functions are defined:

  s_add(lhs, rhs)
  s_mul(lhs, rhs)
  s_power(base, intexp)
  s_expand(expr)
  s_tostr(expr)
  s_add_sequence(seq)
  s_mul_sequence(seq)

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

This code is based on the research of Fredrik Johansson
(see research/directadd5.py) and is implemented by Pearu Peterson.
"""

__all__ = ['s_add', 's_mul', 's_power', 's_expand', 's_tostr',
           's_add_terms_coeffs','s_mul_bases_exps',
           's_add_sequence', 's_mul_sequence', 's_toBasic']

from ..core import classes, objects, sympify
from ..core.sexpr import NUMBER, SYMBOLIC, TERMS, FACTORS, IMAGUNIT, NANINF

one = objects.one
zero = objects.zero
two = one+one
s_zero = (NUMBER, objects.zero)
s_one = (NUMBER, objects.one)

s_nan = (NANINF, objects.nan)
s_oo = (NANINF, objects.oo)
s_moo = (NANINF, objects.moo)
s_zoo = (NANINF, objects.zoo)

assert one is classes.Integer(1)
assert zero is classes.Integer(0)

# connection to Basic classes:
def s_toBasic_generator(expr):
    Number = classes.Number
    s = expr[0]
    seq = expr[1]
    if s is TERMS:
        Mul = classes.Mul
        for t,c in seq:
            b = s_toBasic(t)
            if c is one:
                yield b
            elif isinstance(b, Number):
                yield b*c
            else:
                if t[0] is FACTORS:
                    t1 = (FACTORS, t[1].union([((NUMBER,c), one)]), c)
                    yield Mul(s_toBasic_generator(t1), sexpr=t1)
                else:
                    yield Mul((b,c), sexpr = (TERMS,frozenset([(t,c)]), zero))
    elif s is FACTORS:
        Pow = classes.Pow
        for t,c in seq:
            b = s_toBasic(t)
            if c is one:
                yield b
            else:
                yield Pow(b, c, sexpr = (FACTORS,frozenset([(t,c)]), one))
    else:
        yield seq

def s_toBasic(expr):
    """ Convert s-expr to Basic instance.
    """
    s = expr[0]
    seq = expr[1]
    if s is NUMBER:
        return seq
    elif s is TERMS:
        if len(seq)==1:
            t, c = list(seq)[0]
            coeff = (NUMBER, c)
            if t[0] is FACTORS:
                t = (FACTORS, t[1].union([(coeff, one)]), coeff)
            else:
                t = (FACTORS, frozenset([(t, one), (coeff, one)]), coeff)
            return classes.Mul(s_toBasic_generator(t), sexpr=expr)
        return classes.Add(s_toBasic_generator(expr), sexpr=expr)
    elif s is FACTORS:
        if len(seq)==1:
            t, c = list(seq)[0]
            if c is zero:
                return one
            b = s_toBasic(t)
            if c is one:
                return b
            return classes.Pow(b, c, sexpr=expr)
        return classes.Mul(s_toBasic_generator(expr), sexpr=expr)
    return seq

# output functions:

def s_tostr(expr, apply_parenthesis = False):
    """ Return s-expr as a readable string. The output is not
    minimal in terms of operations but it reflects the content
    of an s-expr precisely.
    Terms and factors are sorted lexicographically to ensure
    unique output.
    """
    s = expr[0]
    if s is TERMS:
        l = ['%s*%s' % (c, s_tostr(t)) for t,c in expr[1]]
        l.sort()
        r = ' + '.join(l)
    elif s is FACTORS:
        l = ['%s**%s' % (s_tostr(t, t[0] is TERMS), c) for t,c in expr[1]]
        l.sort()
        r = ' * '.join(l)
    else:
        r = str(expr[1])
    if apply_parenthesis:
        r = '(%s)' % (r)
    return r

# arithmetic functions:

def add_inplace_dict_terms(d, rhs, p):
    for t,c in rhs[1]:
        # in C use the following code idiom:
        #add_inplace_dict_term_coeff(d, t, c * p)
        #continue
        b = d.get(t)
        if b is None:
            d[t] = c * p
        else:
            c = b + c * p
            if c is zero:
                del d[t]
            else:
                d[t] = c
    return

# having special function with p=1 gives 50% speedup.
def add_inplace_dict_terms1(d, rhs):
    for t,c in rhs[1]:
        # in C use the following code idiom:
        #add_inplace_dict_term_coeff(d, t, c)
        #continue
        b = d.get(t)
        if b is None:
            d[t] = c
        else:
            c = b + c
            if c is zero:
                del d[t]
            else:
                d[t] = c 
    return

def add_inplace_dict_term_coeff(d, term, coeff):
    b = d.get(term)
    if b is None:
        d[term] = coeff
    else:
        c = b + coeff
        if c is zero:
            del d[term]
        else:
            d[term] = c
    return

def mul_inplace_dict_factors(d, rhs, p):
    for t,c in rhs[1]:
        # in C use the following code idiom:
        # mul_inplace_dict_base_exp(d, t, c * p)
        # continue
        b = d.get(t)
        if b is None:
            d[t] = c * p
        else:
            c = b + c * p
            if c is zero:
                del d[t]
            else:
                d[t] = c
    return

def mul_inplace_dict_factors1(d, rhs):
    for t,c in rhs[1]:
        # in C use the following code idiom:
        # mul_inplace_dict_base_exp(d, t, c)
        # continue
        b = d.get(t)
        if b is None:
            d[t] = c
        else:
            c = b + c
            if c is zero:
                del d[t]
            else:
                d[t] = c
    return

def mul_inplace_dict_base_exp(d, base, exp):
    b = d.get(base)
    if b is None:
        d[base] = exp
    else:
        c = b + exp
        if c is zero:
            del d[base]
        else:
            d[base] = c

def terms_dict_to_expr(d):
    if not d:
        return s_zero
    if len(d)==1:
        t, c = d.items()[0]
        if c is one:
            return t
        elif t[0] is NUMBER and t[1] is one:
            return (NUMBER, c)
    return (TERMS, frozenset(d.iteritems()), d.get(s_one, zero))

def factors_dict_to_expr(d):
    if not d:
        return s_one
    if len(d)==1:
        t, c = d.items()[0]
        if c is one:
            return t
    assert d.get(s_one) is None, `d`
    return (FACTORS, frozenset(d.iteritems()), one)

def add_terms_terms(lhs, rhs):
    d = dict(lhs[1])
    add_inplace_dict_terms1(d, rhs)
    return terms_dict_to_expr(d)

def add_terms_term_coeff(lhs, term, coeff):
    d = dict(lhs[1])
    b = d.get(term)
    if b is None:
        d[term] = coeff
    else:
        c = b + coeff
        if c is zero:
            del d[term]
        else:
            d[term] = c
    return terms_dict_to_expr(d)

def add_nonterms_nonterms(lhs, rhs):
    t1 = lhs[1]
    t2 = rhs[1]
    if t1==t2:
        return (TERMS, frozenset([(lhs, two)]), zero)
    return (TERMS, frozenset([(lhs, one), (rhs, one)]), zero)

def s_add(lhs, rhs):
    """ Add two s-expressions.
    """
    s1, s2 = lhs[0], rhs[0]
    if s1 is NUMBER:
        n = lhs[1]
        if s1 is s2:
            return (NUMBER, n + rhs[1])
        if n is zero:
            return rhs
        if s2 is TERMS:
            return add_terms_term_coeff(rhs, s_one, lhs[1])
        return (TERMS, frozenset([(rhs, one), (s_one, lhs[1])]), lhs[1])
    if s2 is NUMBER:
        n = rhs[1]
        if n is zero:
            return lhs
        if s1 is TERMS:
            return add_terms_term_coeff(lhs, s_one, n)
        return (TERMS, frozenset([(lhs, one), (s_one, n)]), n)
    if s1 is TERMS:
        if s1 is s2:
            return add_terms_terms(lhs, rhs)
        return add_terms_term_coeff(lhs, rhs, one)
    if s2 is TERMS:
        return add_terms_term_coeff(rhs, lhs, one)
    return add_nonterms_nonterms(lhs, rhs)

def add_inplace_dict(d, rhs, p):
    """ Add s-expression multiplied with p to dictionary d.
    """
    s = rhs[0]
    if s is TERMS:
        add_inplace_dict_terms(d, rhs, p)
    elif s is NUMBER:
        add_inplace_dict_term_coeff(d, s_one, rhs[1] * p)
    else:
        add_inplace_dict_term_coeff(d, rhs, p)
    return

def add_inplace_dict1(d, rhs):
    """ Add s-expression multiplied with p to dictionary d.
    """
    s = rhs[0]
    if s is TERMS:
        add_inplace_dict_terms1(d, rhs)
    elif s is NUMBER:
        add_inplace_dict_term_coeff(d, s_one, rhs[1])
    else:
        add_inplace_dict_term_coeff(d, rhs, one)
    return

def mul_factors_factors(lhs, rhs):
    d = dict(lhs[1])
    mul_inplace_dict_factors1(d, rhs)
    return factors_dict_to_expr(d)

def mul_factors_base_exp(lhs, base, exp):
    d = dict(lhs[1])
    mul_inplace_dict_base_exp(d, base, exp)
    return factors_dict_to_expr(d)

def mul_nonfactors_nonfactors(lhs, rhs):
    t1 = lhs[1]
    t2 = rhs[1]
    if t1==t2:
        return (FACTORS, frozenset([(lhs, 2)]), one)
    return (FACTORS, frozenset([(lhs, one), (rhs, one)]), one)

def mul_terms_terms(lhs, rhs):
    if len(lhs[1])==1 and len(rhs[1])==1:
        t1,c1 = list(lhs[1])[0]
        t2,c2 = list(rhs[1])[0]
        return s_mul(s_mul(t1, t2),(NUMBER, c1*c2))
    return mul_nonfactors_nonfactors(lhs, rhs)

def mul_terms_number(lhs, rhs):
    d = dict()
    add_inplace_dict_terms(d, lhs, rhs[1])
    return terms_dict_to_expr(d)

def mul_terms_factors(lhs, rhs):
    if not (len(lhs[1])==1):
        return mul_factors_base_exp(rhs, lhs, one)
    t,c = list(lhs[1])[0]
    return s_mul(s_mul(t,rhs), (NUMBER, c))

def mul_terms_nonfactors(lhs, rhs):
    if not (len(lhs[1])==1):
        return mul_nonfactors_nonfactors(rhs, lhs)
    t,c = list(lhs[1])[0]
    return s_mul(s_mul(t,rhs), (NUMBER, c))

def mul_number_other(lhs, rhs):
    n = lhs[1]
    s = rhs[0]
    if n is one:
        return rhs
    if s is NUMBER:
        return (NUMBER, n * rhs[1])
    if n is zero:
        return lhs
    if s is TERMS:
        return mul_terms_number(rhs, lhs)
    return (TERMS, frozenset([(rhs, n)]), zero)

def s_mul(lhs, rhs):
    """ Multiply two s-expressions.
    """
    s1, s2 = lhs[0], rhs[0]
    if s1 is FACTORS:
        if s2 is FACTORS:
            return mul_factors_factors(lhs, rhs)
        elif s2 is TERMS:
            return mul_terms_factors(rhs, lhs)
        elif s2 is NUMBER:
            return mul_number_other(rhs, lhs)
        return mul_factors_base_exp(lhs, rhs, one)
    elif s1 is TERMS:
        if s2 is FACTORS:
            return mul_terms_factors(lhs, rhs)
        elif s2 is TERMS:
            return mul_terms_terms(lhs, rhs)
        elif s2 is NUMBER:
            return mul_number_other(rhs, lhs)
        return mul_terms_nonfactors(lhs, rhs)
    elif s1 is NUMBER:
        return mul_number_other(lhs, rhs)
    else:
        if s2 is FACTORS:
            return mul_factors_base_exp(rhs, lhs, one)
        elif s2 is TERMS:
            return mul_terms_nonfactors(rhs, lhs)
        elif s2 is NUMBER:
            return mul_number_other(rhs, lhs)
    return mul_nonfactors_nonfactors(lhs, rhs)

def s_neg(expr):
    """ Negative of an s-expression.
    """
    s = expr[0]
    if s is NUMBER:
        return (NUMBER, -expr[1])
    if s is TERMS:
        return mul_terms_number(expr, (NUMBER, -one))
    return (TERMS, frozenset([(expr, -one)]), zero)

def s_power(base, exp):
    """ Find a power of an s-expression over integer exponent.
    """
    assert isinstance(exp, (int,long)),`type(exp)`
    if exp is one:
        return base
    elif exp is zero:
        return s_one
    s = base[0]
    if s is NUMBER:
        return (NUMBER, base[1] ** exp)
    elif s is TERMS:
        if len(base[1])==1 and not(exp is one):
            t,c = list(base[1])[0]
            cc = c**exp
            if cc is one:
                return s_power(t, exp)
            return s_mul(s_power(t, exp), (NUMBER, cc))
    elif s is FACTORS:
        d = dict()
        mul_inplace_dict_factors(d, base, exp)
        return factors_dict_to_expr(d)
    elif s is IMAGUNIT:
        e = exp % 4
        if e==0:
            return s_one
        if e==1:
            return base
        if e==2:
            return s_neg(s_one)
        return s_neg(base)
    return (FACTORS, frozenset([(base, exp)]), one)

def expand_mul_terms_terms(lhs, rhs):
    d = dict()
    for t1,c1 in lhs[1]:
        for t2,c2 in rhs[1]:
            add_inplace_dict(d, s_mul(t1,t2), c1*c2)
    return terms_dict_to_expr(d)

def expand_mul_terms_nonterms(lhs, rhs):
    d = dict()
    for t,c in lhs[1]:
        add_inplace_dict(d, s_mul(t, rhs), c)
    return terms_dict_to_expr(d)

def expand_mul(lhs, rhs):
    """ Multiply s-expressions with expand.
    """
    s1, s2 = lhs[0], rhs[0]
    if s1 is TERMS:
        if s1 is s2:
            return expand_mul_terms_terms(lhs, rhs)
        return expand_mul_terms_nonterms(lhs, rhs)
    if s2 is TERMS:
        return expand_mul_terms_nonterms(rhs, lhs)
    return s_mul(lhs, rhs)

def expand_terms(expr):
    d = dict()
    for t,c in expr[1]:
        add_inplace_dict(d, s_expand(t), c)
    return terms_dict_to_expr(d)

def expand_factors(expr):
    r = None
    for t,c in expr[1]:
        e = expand_power(s_expand(t), c)
        if r is None:
            r = e
        else:
            r = expand_mul(r, e)
    return r

def expand_power(expr, p):
    if p is one:
        return expr
    elif p<zero or expr[0]!=TERMS:
        return s_power(expr, p)
    ## Consider polynomial
    ##   P(x) = sum_{i=0}^n p_i x^k
    ## and its m-th exponent
    ##   P(x)^m = sum_{k=0}^{m n} a(m,k) x^k
    ## The coefficients a(m,k) can be computed using the
    ## J.C.P. Miller Pure Recurrence [see D.E.Knuth,
    ## Seminumerical Algorithms, The art of Computer
    ## Programming v.2, Addison Wesley, Reading, 1981;]:
    ##  a(m,k) = 1/(k p_0) sum_{i=1}^n p_i ((m+1)i-k) a(m,k-i),
    ## where a(m,0) = p_0^m.
    Fraction = classes.Fraction
    m = int(p)
    tc = list(expr[1])
    n = len(tc)-1
    t0,c0 = tc[0]
    p0 = [s_mul(s_mul(t, s_power(t0,-one)),(NUMBER, c/c0)) for t,c in tc]
    r = dict()
    add_inplace_dict(r, s_power(t0,m), c0**m)
    l = [terms_dict_to_expr(r)]
    for k in xrange(1, m * n + 1):
        r1 = dict()
        for i in xrange(1, min(n+1,k+1)):
            nn = (m+1)*i-k
            if nn:
                add_inplace_dict(r1, expand_mul(l[k-i], p0[i]), Fraction(nn, k))
        f = terms_dict_to_expr(r1)
        add_inplace_dict1(r, f)
        l.append(f)
    return terms_dict_to_expr(r)

def s_expand(expr):
    """ Expand s-expression.
    """
    s = expr[0]
    if s is TERMS:
        return expand_terms(expr)
    elif s is FACTORS:
        return expand_factors(expr)
    return expr

def s_add_sequence(seq):
    """ Add a sequence of s-expressions.
    """
    d = dict()
    for expr in seq:
        if expr[0] is NUMBER and expr[1] is zero:
            continue
        add_inplace_dict1(d, expr)
    return terms_dict_to_expr(d)

def s_add_terms_coeffs(seq):
    """ Add a sequence of (s-expression, coeff).
    """
    d = dict()
    for expr, coeff in seq:
        if (expr[0] is NUMBER and expr[1] is zero) or coeff is zero:
            continue
        add_inplace_dict(d, expr, coeff)
    return terms_dict_to_expr(d)

def s_mul_sequence(seq):
    """ Multiply a sequence of s-expressions.
    """
    d = dict()
    coeff = one
    for expr in seq:
        s = expr[0]
        if s is FACTORS:
            mul_inplace_dict_factors1(d, expr)
        elif s is NUMBER:
            coeff = coeff * expr[1]
        elif s is TERMS:
            if len(expr[1])==1:
                t,c = list(expr[1])[0]
                coeff = coeff * c
                if t[0] is FACTORS:
                    mul_inplace_dict_factors1(d, t)
                else:
                    mul_inplace_dict_base_exp(d, t, one)
            else:
                mul_inplace_dict_base_exp(d, expr, one)
        else:
            mul_inplace_dict_base_exp(d, expr, one)
    if coeff is one:
        return factors_dict_to_expr(d)
    return s_mul(factors_dict_to_expr(d), (NUMBER, coeff))

def s_mul_bases_exps(seq):
    """ Multiply a sequence of s-expressions.
    """
    d = dict()
    coeff = one
    for (expr,p) in seq:
        s = expr[0]
        if s is FACTORS:
            mul_inplace_dict_factors(d, expr, p)
        elif s is NUMBER:
            coeff = coeff * (expr[1] ** p)
        elif s is TERMS:
            if len(expr[1])==1:
                t,c = list(expr[1])[0]
                coeff = coeff * (c ** p)
                if t[0] is FACTORS:
                    mul_inplace_dict_factors(d, t, p)
                else:
                    mul_inplace_dict_base_exp(d, t, p)
            else:
                mul_inplace_dict_base_exp(d, expr, p)
        else:
            mul_inplace_dict_base_exp(d, expr, p)
    if coeff is one:
        return factors_dict_to_expr(d)
    return s_mul(factors_dict_to_expr(d), (NUMBER, coeff))

