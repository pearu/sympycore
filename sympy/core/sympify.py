
from __future__ import absolute_import

import re
import sys
from compiler.transformer import Transformer
from compiler.pycodegen import ExpressionCodeGenerator
from compiler import ast
import symbol
import compiler

from .basic import Basic

__all__ = ['sympify']

def sympify(a, sympify_lists=False, globals=None, locals=None):
    """Converts an arbitrary expression to a type that can be used
       inside sympy. For example, it will convert python int's into
       instance of sympy.Integer, floats into intances of sympy.Float,
       etc. It is also able to coerce symbolic expressions which does
       inherit after Basic. This can be useful in cooperation with SAGE.
       
       It currently accepts as arguments:
         - any object defined in sympy (except maybe matrices [TODO])
         - standard numeric python types: int, long, float, Decimal
         - strings (like "0.09" or "2e-19")

       If sympify_lists is set to True then sympify will also accept
       lists, tuples and sets. It will return the same type but with
       all of the entries sympified.

       If the argument is already a type that sympy understands, it will do
       nothing but return that value. This can be used at the begining of a
       function to ensure you are working with the correct type.

       >>> from sympy import *

       >>> sympify(2).is_Integer
       True
       >>> sympify(2).is_Real
       True

       >>> sympify(2.0).is_Real
       True
       >>> sympify("2.0").is_Real
       True
       >>> sympify("2e-45").is_Real
       True
       
       """
    if isinstance(a, (Basic,bool)):
        return a
    if isinstance(a, (int, long)):
        return Basic.Integer(a)
    if isinstance(a, float):
        return Basic.Float(a)
    if isinstance(a, complex):
        # XXX: fix int-s
        real, imag = sympify(a.real), sympify(a.imag)
        ireal, iimag = int(real), int(imag)
        if ireal + iimag*1j == a:
            return ireal + iimag*Basic.I
        return real + Basic.I * imag
    if isinstance(a, str):
        if globals is None or locals is None:
            frame = sys._getframe(1)
            if globals is None:
                globals = frame.f_globals
            if locals is None:
                locals = frame.f_locals
    if isinstance(a, (list,tuple,set)) and sympify_lists:
        return type(a)([Basic.sympify(x, True, globals, locals) for x in a])
    if not isinstance(a, str):
        # At this point we were given an arbitrary expression
        # which does not inherit after Basic. This may be
        # SAGE's expression (or something alike) so take
        # its normal form via str() and try to parse it.
        # XXX: make sure that `a` is actually a SAGE expression
        a = str(a)
    if isinstance(a, str):
        return sympy_eval(a, globals, locals)
    raise ValueError("%s is NOT a valid SymPy expression" % (`a`))

_is_integer = re.compile(r'\A\d+(l|L)?\Z').match

class SympyTransformer(Transformer):
    """
    The following transformations are carried out:
    
      integer_literal -> Integer(integer_literal)
      float_literal -> Float(float_literal)
      string_literal -> (globals(), locals()).get(string_literal, Symbol(string_literal))
      lambda x,y,..: expr -> .. Lambda((x,y,..), expr)

    Todo:
      a and b -> And(a, b)
      a or b -> Or(a, b)
      not a -> Not a
      a < b -> Less(a, b)
      etc
    """
    def __init__(self, globals, locals):
        Transformer.__init__(self)
        self.globals = globals
        self.locals = locals

    def atom_name(self, nodelist):
        name, lineno = nodelist[0][1:]
        if self.locals.has_key(name) or self.globals.has_key(name):
            return ast.Name(name, lineno=lineno)
        return ast.CallFunc(ast.Name('Symbol'),[ast.Const(name, lineno=lineno)])

    def atom_number(self, nodelist):
        n = Transformer.atom_number(self, nodelist)
        number, lineno = nodelist[0][1:]
        if _is_integer(number):
            n = ast.Const(long(number), lineno)
            return ast.CallFunc(ast.Name('Integer'), [n])
        n = ast.Const(number, lineno)
        return ast.CallFunc(ast.Name('Float'), [n])

    def lambdef(self, nodelist):
        # lambdef: 'lambda' [varargslist] ':' test
        if nodelist[2][0] == symbol.varargslist:
            names, defaults, flags = self.com_arglist(nodelist[2][1:])
        else:
            names = defaults = ()
            flags = 0
        lineno = nodelist[1][2]
        code = self.com_node(nodelist[-1])
        assert not defaults,`defaults` # sympy.Lambda does not support optional arguments
        arguments = []
        for name in names:
            arguments.append(ast.CallFunc(ast.Name('Symbol'),[ast.Const(name, lineno=lineno)]))
        return ast.CallFunc(ast.Name('Lambda'),[ast.Tuple(arguments,lineno=lineno), code])


def sympy_eval(a, globals, locals):
    exec 'from sympy import Integer, Float, Symbol, Lambda' in globals, locals
    tree = SympyTransformer(globals, locals).parseexpr(a)
    compiler.misc.set_filename('<sympify>', tree)
    code = ExpressionCodeGenerator(tree).getCode()
    return eval(code, globals, locals)

