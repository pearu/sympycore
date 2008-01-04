
from ..core import Basic, Atom, BasicType, BasicWild, classes, objects
from ..core import (BasicFunctionType, BasicFunction,
                    FunctionSignature, BasicLambda,
                    instancemethod
                    )
from .methods import ArithmeticMethods
from .basic import BasicArithmetic

from ..core import sexpr
from .sexpr import s_toBasic, s_expand

__all__ = ['FunctionType', 'Function', 'Lambda', 'FunctionSymbol',
           'WildFunctionType', 'ArithmeticFunction']


class FunctionType(BasicArithmetic, BasicFunctionType):
    """ Metaclass for Function class.
    """
    pass


class Function(BasicArithmetic, BasicFunction):
    """ Base class for functions that can be used in arithmetic operations
    as operants (both in evaluated and unevaluated form).
    """

    __metaclass__ = FunctionType

    try_power = instancemethod(BasicArithmetic.try_power)(BasicArithmetic.try_power)

    def try_derivative(self, s):
        i = 0
        l = []
        r = objects.zero
        args = self.args
        for a in args:
            i += 1
            da = a.diff(s)
            if da.is_zero:
                continue
            df = self.func.fdiff(i)
            l.append(df(*args) * da)
        return classes.Add(*l)

    @classmethod
    def fdiff(obj, index=1):
        nargs = obj.signature.nof_arguments
        if nargs is not None and not (1<=index<=nargs):
            raise TypeError('fdiff: invalid index=%r, %s takes %s arguments'\
                            % (index, obj.__name__, nargs))
        mth = getattr(obj, 'fdiff%s' % (index), None)
        if mth is not None:
            return mth()
        return classes.FDerivative(obj, classes.Tuple(index, 1), is_canonical=True)

    @instancemethod(fdiff)
    def fdiff(obj, index=1):
        return obj._fdiff(index)

    def _fdiff(self, index=1):
        # handles: sin(cos).fdiff() -> sin'(cos) * cos' -> cos(cos) * sin
        i = 0
        l = []
        for a in self.args:
            i += 1
            df = self.func.fdiff(i)(*self.args)
            da = a.fdiff(index)
            l.append(df * da)
        return classes.Add(*l)


class Lambda(BasicArithmetic, BasicLambda):

    pass

class WildFunctionType(BasicWild, FunctionType):
    # Todo: derive WildFunctionType from DummyFunctionType.
    def __new__(typ, name=None, bases=(), attrdict={}, is_global=None, predicate=None):
        if name is None:
            name = 'WF'
        attrdict['matches'] = instancemethod(BasicWild.matches)(BasicFunction.__dict__['matches'])
        func = FunctionType.__new__(typ, name, bases, attrdict, is_global)
        if predicate is not None:
            func.predicate = staticmethod(predicate)
        return func

class ArithmeticFunction(Function):
    ordered_arguments = False

    @instancemethod(Function.count_ops)
    def count_ops(self, symbolic=True):
        n = len(self.args)
        if symbolic:
            counter = (n-1) * self.func
        else:
            counter = n-1
        for a in self.args:
            counter += a.count_ops(symbolic=symbolic)
        return counter    

    #XXX: __hash__, __iter__, as_sexpr, etc.

    @instancemethod(Function.__eq__)
    def __eq__(self, other):
        if self.__class__ is other.__class__:
            return self.as_sexpr()[:2]==other.as_sexpr()[:2]
        if isinstance(other, Basic):
            return False
        if isinstance(other, str):
            return self==sympify(other)
        return False

    def expand(self, **hints):
        if hints.get('basic', True):
            return s_toBasic(s_expand(self.as_sexpr()))
        return self

class _old_ArithmeticFunction(Function):
    """ Base class for Add and Mul classes.
    
    Important notes:
    - Add and Mul implement their own __new__ methods.
    - Add and Mul do not implement canonize() method but are
      subclasses of Function. Canonization is carried out
      by the TermCoeffDict and BaseExpDict classes, respectively.
    - Instances of Add and Mul are created in .as_Basic()
      methods of TermCoeffDict and BaseExpDict, respectively.
    - One should not subclass from Add and Mul classes (does this still holds?).
    - Add and Mul instances have the following attributes:
       * ._dict_content - holds TermCoeffDict or BaseExpDict instance
       * .args - equals to _dict_content.args_flattened
       * .args_sorted - use .get_args_sorted() for initializing
       * .args_frozenset - use .get_args_frozenset() for initializing
       * BaseExpDict instances have additional attribute .coeff such
         that <BaseExpDict instance>[coeff] == 1
         and isinstance(coeff, classes.Number) == True
    """

    ordered_arguments = False
    
    signature = FunctionSignature([BasicArithmetic],(BasicArithmetic,))

    @instancemethod(Function.__eq__)
    def __eq__(self, other):
        if self.__class__ is other.__class__:
            return dict.__eq__(self._dict_content, other._dict_content)
        if isinstance(other, Basic):
            return False
        if isinstance(other, str):
            return self==sympify(other)
        return False

    @instancemethod(Function.count_ops)
    def count_ops(self, symbolic=True):
        n = len(self.args)
        if symbolic:
            counter = (n-1) * self.func
        else:
            counter = n-1
        for a in self.args:
            counter += a.count_ops(symbolic=symbolic)
        return counter
