from .algebra import Calculus, one, newinstance
from ..utils import NUMBER, SYMBOL, TERMS, FACTORS

Symbol = Calculus.Symbol

def unknown(expr):
    raise NotImplementedError("don't know how to integrate %s" % expr)

def integrate_indefinite(expr, x):
    head = expr.head
    if head is NUMBER or x not in expr._get_symbols_data():
        return expr*x
    elif head is SYMBOL and expr.data == x:
        return expr**2 / 2
    elif expr.head is FACTORS:
        product = one
        have_x = False
        cls = type(expr)
        for base, e in expr.data.iteritems():
            # We don't know how to do exponentials yet
            if type(e) is cls and x in expr._get_symbols_data():
                unknown(expr)
            if base.head is SYMBOL and base.data == x:
                if have_x:
                    unknown(expr)
                e1 = e+1
                product *= base**e1 / e1
                have_x = True
            # Cases like (x+y)*x could still be handled by expanding,
            # but this may cause infinite recursion if implemented
            # directly here
            elif x in base._get_symbols_data():
                unknown(expr)
            else:
                product *= base**e
        return product
    elif expr.head is TERMS:
        return expr.Add(*(coef*integrate_indefinite(term, x) \
            for term, coef in expr.data.iteritems()))
    unknown(expr)

def integrate_definite(expr, x, a, b):
    head = expr.head
    if head is NUMBER or x not in expr._get_symbols_data():
        return expr*(b-a)
    elif head is SYMBOL and expr.data == x:
        return (b**2 - a**2) / 2
    elif head is FACTORS:
        product = one
        have_x = False
        cls = type(expr)
        for base, e in expr.data.iteritems():
            # We don't know how to do exponentials yet
            if type(e) is cls and x in expr._get_symbols_data():
                unknown(expr)
            if base.head is SYMBOL and base.data == x:
                if have_x:
                    unknown(expr)
                e1 = e+1
                product *= (b**e1 - a**e1) / e1
                have_x = True
            # Cases like (x+y)*x could still be handled by expanding,
            # but this may cause infinite recursion if implemented
            # directly here
            elif x in base._get_symbols_data():
                unknown(expr)
            else:
                product *= newinstance(cls, FACTORS, {base:e})
        return product
    elif head is TERMS:
        return expr.Add(*(coef*integrate_definite(term, x, a, b) \
                          for term, coef in expr.data.iteritems()))
    unknown(expr)

def integrate(expr, x):
    type_ = type
    Calculus_ = Calculus
    type_x = type_(x)
    if type_(expr) is not Calculus_:
        expr = Calculus_(expr)
    if type_x is tuple:
        v, a, b = x
        if type_(v) is not Calculus_: v = Symbol(v)
        if type_(a) is not Calculus_: a = Calculus_(a)
        if type_(b) is not Calculus_: b = Calculus_(b)
        return integrate_definite(expr, v.data, a, b)
    else:
        if type_x is not Calculus_:
            x = Symbol(x)
        return integrate_indefinite(expr, x.data)
