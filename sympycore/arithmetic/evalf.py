"""Provides low-level evalf function.
"""

__all__ = ['evalf']

from .numbers import Float, Complex

import math
import cmath
import re
import mpmath

int_pattern = re.compile('\d+([.]\d+)?')

def quote_numbers(s, format):
    return int_pattern.sub(lambda m: (format % m.group()), s)

def replace_names(s, names):
    for name, new in names.items():
        s = s.replace(name, new)
    return s

def f_header(symbols):
    if isinstance(symbols, (tuple, list)):
        return "lambda %s: " % ",".join(map(str, symbols))
    if not symbols:
        return "lambda: "
    return "lambda %s: " % symbols

def convert_mpmath(expr):
    s = str(expr)
    s = quote_numbers(s, "mpf(%s)")
    s = replace_names(s, { 'I':'j', 'E':'e', 'oo':'inf','undefined':'nan'})
    return s

def compile_mpmath(symbols, expr):
    s = convert_mpmath(expr)
    f = eval(f_header(symbols) + s, vars(mpmath))
    return f

def mpmath_to_numbers(x, digits):
    prec = int(digits*3.33) + 12
    if isinstance(x, mpmath.mpc):
        return Complex(Float(x.real.val, prec), Float(x.imag.val, prec))
    a = object.__new__(Float)
    a.val = x.val
    a.prec = prec
    return a

def evalf(expr, digits=15):
    s = convert_mpmath(expr)
    mpmath.mpf.dps = digits + 4
    return mpmath_to_numbers(eval(s, vars(mpmath)), digits)
