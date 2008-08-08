""" Provides the implementation of integration methods.
"""

__docformat__ = "restructuredtext"
__all__ = ['integrate']

from .algebra import Calculus, one
from ..utils import NUMBER, SYMBOL, TERMS, FACTORS

Symbol = Calculus.Symbol
Convert = Calculus.convert

def unknown(expr, *args):
    raise NotImplementedError("don't know how to integrate %s over [%s]" \
                                  % (expr, ', '.join(map(str, args))))

def integrate_indefinite(expr, x):
    head, data = expr.pair
    cls = type(expr)
    if head is NUMBER or x not in expr._get_symbols_data():
        return expr*cls.Symbol(x)
    elif head is SYMBOL and expr.data == x:
        return expr**2 / 2
    elif head is FACTORS:
        product = one
        have_x = False
        for base, e in data.iteritems():
            # We don't know how to do exponentials yet
            if type(e) is cls and x in expr._get_symbols_data():
                unknown(expr, x)
            if base.head is SYMBOL and base.data == x:
                if have_x:
                    unknown(expr, x)
                e1 = e+1
                product *= base**e1 / e1
                have_x = True
            # Cases like (x+y)*x could still be handled by expanding,
            # but this may cause infinite recursion if implemented
            # directly here
            elif x in base._get_symbols_data():
                unknown(expr, x)
            else:
                product *= base**e
        return product
    elif head is TERMS:
        return expr.Add(*(coef*integrate_indefinite(term, x) \
                          for term, coef in data.iteritems()))
    unknown(expr, x)

def integrate_definite(expr, x, a, b):
    head, data = expr.pair
    if head is NUMBER or x not in expr._get_symbols_data():
        return expr*(b-a)
    elif head is SYMBOL and data == x:
        return (b**2 - a**2) / 2
    elif head is FACTORS:
        product = one
        have_x = False
        cls = type(expr)
        for base, e in data.iteritems():
            # We don't know how to do exponentials yet
            if type(e) is cls and x in expr._get_symbols_data():
                unknown(expr, x, a, b)
            if base.pair == (SYMBOL, x):
                if have_x:
                    unknown(expr, x, a, b)
                e1 = e+1
                product *= (b**e1 - a**e1) / e1
                have_x = True
            # Cases like (x+y)*x could still be handled by expanding,
            # but this may cause infinite recursion if implemented
            # directly here
            elif x in base._get_symbols_data():
                if len(data)==1:
                    db = base.diff(x)
                    if x not in db._get_symbols_data():
                        x1 = Symbol(str(x)+'__')
                        product *= integrate_definite(x1**e, x1, base.subs(x, a), base.subs (x, b))/db
                        break
                else:
                    new_expr = expr.expand()
                    if new_expr != expr:
                        return integrate_definite(new_expr, x, a, b)
                unknown(expr, x, a, b)
            else:
                product *= cls(FACTORS, {base:e})
        return product
    elif head is TERMS:
        return expr.Add(*(coef*integrate_definite(term, x, a, b) \
                          for term, coef in data.iteritems()))
    unknown(expr, x, a, b)

def integrate(expr, x):
    type_ = type
    Calculus_ = Calculus
    type_x = type_(x)
    if type_(expr) is not Calculus_:
        expr = Convert(expr)
    if type_x is tuple:
        v, a, b = x
        if type_(v) is not Calculus_: v = Symbol(v)
        if type_(a) is not Calculus_: a = Convert(a)
        if type_(b) is not Calculus_: b = Convert(b)
        return integrate_definite(expr, v.data, a, b)
    else:
        if type_x is not Calculus_:
            x = Symbol(x)
        return integrate_indefinite(expr, x.data)
