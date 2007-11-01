
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
            if hasattr(Basic, name):
                return issubclass(getattr(Basic, name), Basic.BasicArithmetic)
        elif isinstance(node.node, ast.CallFunc):
            return _is_arithmetic(node.node)
    elif isinstance(node, ast.Const):
        value = node.value
        if isinstance(value, Basic):
            return value.is_BasicArithmetic
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
            arguments.append(ast.CallFunc(ast.Name('BasicSymbol'),[ast.Const(name, lineno=lineno)]))
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
                elif op=='is not':
                    ops.append(ast.CallFunc(ast.Name('IsNot'),[lhs, rhs]))
                else:
                    raise NotImplementedError('%r %r %r' % (lhs, op, rhs))
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
        n = ast.Const(number, lineno)
        return ast.CallFunc(ast.Name('Float'), [n])

    # decode_literal, atom_string
    def atom_name(self, nodelist):
        name, lineno = nodelist[0][1:]
        if self.locals.has_key(name) or self.globals.has_key(name):
            obj = eval(name, self.globals, self.locals)
            #print
            #print 'HEY:',obj
            #print
            return ast.Const(obj, lineno=lineno)
            return ast.Name(name, lineno=lineno)
        return ast.CallFunc(ast.Name(self.symbol_class),[ast.Const(name, lineno=lineno)])

    
def sympy_eval(a, globals, locals):
    globals = globals.copy()
    globals['Is'] = lambda x,y: x is y or x == y
    globals['IsNot'] = lambda x,y: not(x is y or x == y)
    exec 'from sympy import *' in globals
    tree = SympyTransformer(globals, locals).parseexpr(a)
    compiler.misc.set_filename('<sympify>', tree)
    code = ExpressionCodeGenerator(tree).getCode()
    return eval(code, globals, locals)

