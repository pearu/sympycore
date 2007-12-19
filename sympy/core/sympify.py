
from __future__ import absolute_import

import re
import sys
import symbol
import compiler

from compiler.transformer import Transformer
from compiler.pycodegen import ExpressionCodeGenerator
from compiler import ast

from .basic import Basic, classes, objects

__all__ = ['sympify','sympify_types']

# types that sympify can handle:
sympify_types = (Basic,int,long,float,complex,str) # the first element must be Basic!
int_types = (int, long)
float_types = (float) # XXX: Decimal
complex_types = (complex)
string_types = (str) # XXX: unicode

def sympify(a, globals=None, locals=None, debug=False):
    """Converts an arbitrary expression to a type that can be used
       inside sympy. For example, it will convert python int's into
       instance of sympy.Integer, floats into intances of sympy.Float,
       etc. It is also able to coerce symbolic expressions which does
       inherit after Basic. This can be useful in cooperation with SAGE.
       
       It currently accepts as arguments:
         - any object defined in sympy
         - standard numeric python types: int, long, float, complex
         - strings (like "0.09" or "2e-19")
         - True and False

       If the argument is already a type that sympy understands, it will do
       nothing but return that value. This can be used at the beginning of a
       function to ensure you are working with the correct type.

       >>> from sympy import *

       >>> isinstance(sympify(2), classes.Integer)
       True
       >>> isinstance(sympify(2), classes.Real)
       True

       >>> isinstance(sympify(2.0), classes.Real)
       True
       >>> sympify("2.0"isinstance(), classes.Real)
       True
       >>> sympify("2e-45"isinstance(), classes.Real)
       True
       
    """
    if isinstance(a, (Basic,bool)):
        return a
    if isinstance(a, int_types):
        return classes.Integer(a)
    if isinstance(a, float_types):
        return classes.Float(a)
    if isinstance(a, complex_types):
        real, imag = sympify(a.real), sympify(a.imag)
        ireal, iimag = int(real), int(imag)
        if ireal==real:
            real = ireal
        if imag==iimag:
            imag = iimag
        return real + objects.I * imag
    if isinstance(a, string_types):
        # initialize globals,locals for sympy_eval call
        if globals is None:
            # using from-import instead of __dict__ to
            # have only public sympy symbols in globals.
            globals = {}
            exec 'from sympy import *' in globals
        if locals is None:
            # We cannot use callers locals by default because sympify is
            # frequently called inside methods that define local
            # variables with the same names as in sympify argument. Users
            # must explicitly call `sympify(.., locals=locals())` in
            # order to reuse local variables.
            locals = {}
    if isinstance(a, string_types):
        if debug:
            return sympy_eval(a, globals, locals)
        try:
            return sympy_eval(a, globals, locals)
        except Exception,msg:
            raise ValueError("Failed to evaluate %s: %s" % (`a`,msg))
    if isinstance(a, tuple):
        return classes.Tuple(*map(sympify, a))
    if hasattr(a, '__sympy__'):
        return sympify(a.__sympy__())
    raise TypeError("Invalid type %s for sympy: %s" % (`type(a)`,`a`))


_is_integer = re.compile(r'\A\d+(l|L)?\Z').match
_ast_arith_classes = (ast.Add, ast.Sub, ast.Mul, ast.Div, ast.Mod, ast.FloorDiv,
                      ast.UnaryAdd, ast.UnarySub, ast.Power)

def _mk_mth(mthname, symbol_class):
    # resets symbol_class if needed
    def mth(self, nodelist):
        old_symbol_class = self.symbol_class
        if len(nodelist)>1:
            self.symbol_class = symbol_class
        r = getattr(Transformer, mthname)(self, nodelist)
        self.symbol_class = old_symbol_class
        return r
    return mth

def _is_arithmetic(node):
    if isinstance(node, _ast_arith_classes):
        return True
    elif isinstance(node, ast.CallFunc):
        if isinstance(node.node, ast.Name):
            name = node.node.name
            if hasattr(classes, name):
                return issubclass(getattr(classes, name), classes.BasicArithmetic)
        elif isinstance(node.node, ast.CallFunc):
            return _is_arithmetic(node.node)
    elif isinstance(node, ast.Const):
        value = node.value
        if isinstance(value, Basic):
            return isinstance(value, classes.BasicArithmetic)
        elif isinstance(value, (int, long, float, complex)):
            return True
    
def _mk_mth_op(mthname, symbol_class, function_name):
    # resets symbol_class if needed
    # maps operation to function call
    if function_name == 'Not':
        def mth(self, nodelist):
            old_symbol_class = self.symbol_class
            if len(nodelist)>1:
                self.symbol_class = symbol_class
            r = Transformer.not_test(self, nodelist)
            if isinstance(r, ast.Not):
                if _is_arithmetic(r.expr):
                    # not x+1 -> not Equal(x+1,0)
                    r.expr = ast.CallFunc(ast.Name('Equal'),[r.expr,ast.Const(0)])
                r = ast.CallFunc(ast.Name('Not'), [r.expr])
            self.symbol_class = old_symbol_class
            return r
        return mth
    def mth(self, nodelist):
        old_symbol_class = self.symbol_class
        if len(nodelist)>1:
            self.symbol_class = symbol_class
        r = getattr(Transformer, mthname)(self, nodelist)
        if isinstance(r, getattr(ast, function_name)):
            nodes = []
            for node in r.nodes:
                if _is_arithmetic(node):
                    # .. <logical op> x+1 -> .. <logical op> Equal(x+1,0)
                    node = ast.CallFunc(ast.Name('Equal'),[node,ast.Const(0)])
                nodes.append(node)
            r = ast.CallFunc(ast.Name(function_name), nodes)
        self.symbol_class = old_symbol_class
        return r
    return mth


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
        self.symbol_class = 'Symbol'


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

    # test
    or_test = _mk_mth_op('or_test', 'Boolean', 'Or')
    and_test = _mk_mth_op('and_test', 'Boolean', 'And')
    not_test = _mk_mth_op('not_test', 'Boolean', 'Not')

    comparison = _mk_mth('comparison', 'Symbol')

    def comparison(self, nodelist):
        old_symbol_class = self.symbol_class
        if len(nodelist)>1:
            self.symbol_class = 'Symbol'
        r = Transformer.comparison(self, nodelist)
        if isinstance(r, ast.Compare):
            ops = []
            lhs = r.expr
            for op, rhs in r.ops:
                if op=='==':
                   ops.append(ast.CallFunc(ast.Name('Equal'),[lhs, rhs]))
                elif op=='!=':
                   ops.append(ast.CallFunc(ast.Name('Not'),[ast.CallFunc(ast.Name('Equal'),[lhs, rhs])]))
                elif op=='<':
                    ops.append(ast.CallFunc(ast.Name('Less'),[lhs, rhs]))
                elif op=='>':
                    ops.append(ast.CallFunc(ast.Name('Less'),[rhs, lhs]))
                elif op=='<=':
                    ops.append(ast.CallFunc(ast.Name('Or'),[
                        ast.CallFunc(ast.Name('Equal'),[lhs, rhs]),
                        ast.CallFunc(ast.Name('Less'),[lhs, rhs])]
                                            ))
                elif op=='>=':
                    ops.append(ast.CallFunc(ast.Name('Or'),[
                        ast.CallFunc(ast.Name('Equal'),[lhs, rhs]),
                        ast.CallFunc(ast.Name('Less'),[rhs, lhs])]
                                            ))
                elif op=='in':
                    rhs = ast.CallFunc(ast.Name('AsSet'),[rhs])
                    ops.append(ast.CallFunc(ast.Name('Element'),[lhs, rhs]))
                elif op=='not in':
                    rhs = ast.CallFunc(ast.Name('AsSet'),[rhs])
                    ops.append(ast.CallFunc(ast.Name('Not'),[ast.CallFunc(ast.Name('Element'),[lhs, rhs])]))
                elif op=='is':
                    ops.append(ast.CallFunc(ast.Name('Is'),[lhs, rhs]))
                else:
                    assert op=='is not','%r %r %r' % (lhs, op, rhs)
                    ops.append(ast.CallFunc(ast.Name('IsNot'),[lhs, rhs]))
                lhs = rhs
            if len(ops)==1:
                r = ops[0]
            else:
                r = ast.CallFunc(ast.Name('And'),ops)
        self.symbol_class = old_symbol_class
        return r

    expr = _mk_mth('expr', 'Symbol')
    xor_expr = _mk_mth('xor_expr', 'Symbol')
    and_expr = _mk_mth('and_expr', 'Symbol')
    shift_expr = _mk_mth('shift_expr', 'Symbol')
    arith_expr = _mk_mth('arith_expr', 'Symbol')
    term = _mk_mth('term', 'Symbol')
    factor = _mk_mth('factor', 'Symbol')
    power = _mk_mth('power', 'Symbol')

    def com_call_function(self, primaryNode, nodelist):
        r = Transformer.com_call_function(self, primaryNode, nodelist)
        return r
    
    # atom, atom_lpar, atom_lsqb, atom_lbrace, atom_backquote

    def atom_number(self, nodelist):
        n = Transformer.atom_number(self, nodelist)
        number, lineno = nodelist[0][1:]
        if _is_integer(number):
            n = ast.Const(long(number), lineno)
            return ast.CallFunc(ast.Name('Integer'), [n])
        if number.endswith('j'):
            n = ast.Const(complex(number), lineno)
            return ast.CallFunc(ast.Name('sympify'), [n])
        n = ast.Const(number, lineno)
        return ast.CallFunc(ast.Name('Float'), [n])

    # decode_literal, atom_string
    def atom_name(self, nodelist):
        name, lineno = nodelist[0][1:]
        if self.locals.has_key(name) or self.globals.has_key(name):
            obj = eval(name, self.globals, self.locals)
            return ast.Const(obj, lineno=lineno)
            #return ast.Name(name, lineno=lineno)
        return ast.CallFunc(ast.Name(self.symbol_class),[ast.Const(name, lineno=lineno)])

    
def sympy_eval(a, globals, locals):
    globals['Is'] = lambda x,y: x is y or x == y
    globals['IsNot'] = lambda x,y: not(x is y or x == y)
    tree = SympyTransformer(globals, locals).parseexpr(a)
    compiler.misc.set_filename('<sympify>', tree)
    code = ExpressionCodeGenerator(tree).getCode()
    result = eval(code, globals, locals)
    if isinstance(result, Basic):
        for atom in result.atoms(type=(classes.BasicSymbol, classes.BasicFunctionType)):
            s = str(atom)
            if globals.has_key(s) or locals.has_key(s):
                continue
            locals[s] = atom
    return result
