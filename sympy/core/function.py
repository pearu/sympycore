
import os
import sys
import types

from .utils import DualMethod, DualProperty
from .basic import Atom, Composite, Basic, BasicType, sympify

__all__ = ['FunctionSignature',
           'BasicFunctionType', 'BasicFunction',
           'BasicLambda', 'Callable']

class FunctionSignature:
    """
    Function signature defines valid function arguments
    and its expected return values.

    Examples:

    A function with undefined number of arguments and return values:
    >>> f = Function('f', FunctionSignature(None, None))

    A function with undefined number of arguments and one return value:
    >>> f = Function('f', FunctionSignature(None, (Basic,)))

    A function with 2 arguments and a pair in as a return value,
    the second argument must be Python integer:
    >>> f = Function('f', FunctionSignature((Basic, int), (Basic, Basic)))

    A function with one argument and one return value, the argument
    must be float or int instance:
    >>> f = Function('f', FunctionSignature(((float, int), ), (Basic,)))

    A function with undefined number of Basic type arguments and return values:
    >>> f = Function('f', FunctionSignature([Basic], None))    
    """

    def __init__(self, argument_classes = (Basic,), value_classes = (Basic,)):
        if isinstance(argument_classes, type):
            argument_classes = (argument_classes,)
        if isinstance(value_classes, type):
            value_classes = (value_classes,)
        self.argument_classes = argument_classes
        self.value_classes = value_classes
        self.nof_arguments = None
        if argument_classes is not None:
            if isinstance(argument_classes, tuple):
                self.nof_arguments = len(argument_classes)
            elif isinstance(argument_classes, list):
                self.argument_classes = tuple(self.argument_classes)
        if value_classes is None:
            # unspecified number of arguments
            self.nof_values = None
        else:
            self.nof_values = len(value_classes)

    def validate(self, funcname, args):
        cls = self.argument_classes
        if self.nof_arguments is not None:
            if self.nof_arguments!=len(args):
                raise TypeError('function %s: wrong number of arguments, expected %s, got %s'\
                                % (funcname, self.nof_arguments, len(args)))
            i = 0
            for a,cls in zip(args, self.argument_classes):
                i += 1
                if not isinstance(a, cls):
                    if isinstance(cls, tuple):
                        clsinfo = '|'.join([c.__name__ for c in cls])
                    else:
                        clsinfo = cls.__name__
                    raise TypeError('function %s: wrong argument[%s] type %r, expected %r'\
                                    % (funcname, i, type(a).__name__, clsinfo))
        elif cls is not None:
            i = 0
            for a in args:
                i += 1
                if not isinstance(a, cls):
                    if isinstance(cls, tuple):
                        clsinfo = '|'.join([c.__name__ for c in cls])
                    else:
                        clsinfo = cls.__name__
                    raise TypeError('function %s: wrong argument[%s] type %r, expected %r'\
                                    % (funcname, i, type(a).__name__, clsinfo))

    def __repr__(self):
        return '%s(%r, %r)' % (self.__class__.__name__,
                               self.argument_classes,
                               self.value_classes)

Basic.FunctionSignature = FunctionSignature

class FunctionTemplate(Composite, tuple):

    signature = FunctionSignature(None, None)
    return_canonize_types = (Basic,)
    
    def __new__(cls, *args, **options):
        args = map(sympify, args)
        cls.signature.validate(cls.__name__, args)
        r = cls.canonize(args, **options)
        if isinstance(r, cls.return_canonize_types):
            return r
        elif r is None:
            pass
        elif not isinstance(r, tuple):
            args = (r,)
        # else we have multiple valued function
        return tuple.__new__(cls, args)

    @classmethod
    def canonize(cls, args, **options):
        return

    def __hash__(self):
        try:
            return self.__dict__['_cached_hash']
        except KeyError:
            h = hash((self.__class__.__name__, tuple(self)))
            self._cached_hash = h
        return h

    def __eq__(self, other):
        if isinstance(other, Basic):
            if not other.is_BasicFunction: return False
            if self.func==other.func:
                return tuple.__eq__(self, other)
            return False
        if isinstance(other, bool):
            return False
        return self==sympify(other)

    @property
    def args(self):
        return tuple(self)

    @property
    def func(self):
        return self.__class__

    @DualProperty
    def precedence(cls):
        return Basic.Apply_precedence

    def torepr(self):
        return '%s(%s)' % (self.__class__.torepr(),
                           ', '.join([a.torepr() for a in self[:]]))

    def tostr(self, level=0):
        p = self.precedence
        r = '%s(%s)' % (self.__class__.tostr(),
                        ', '.join([a.tostr() for a in self[:]]))
        if p<=level:
            return '(%s)' % (r)
        return r

    def __call__(self, *args):
        """
        (f(g))(x) -> f(g(x))
        (f(g1,g2))(x) -> f(g1(x), g2(x))
        """
        return self.__class__(*[a(*args) for a in self.args])

    def atoms(self, type=None):
        return Basic.atoms(self, type).union(self.__class__.atoms(type))


class Callable(Basic, BasicType):
    """ Callable is base class for symbolic function classes.
    """

    def __new__(typ, name, bases, attrdict):
        func = type.__new__(typ, name, bases, attrdict)
        func._fix_methods()
        return func

    def _fix_methods(func):
        """ Apply DualMethod to func methods.
        """
        name = func.__name__
        methods = []
        names = []
        mth_names = []
        for c in func.mro():
            if c.__module__=='__builtin__':
                continue
            for n,mth in c.__dict__.items():
                if not isinstance(mth, (types.FunctionType,DualMethod)):
                    continue
                if n in mth_names: continue
                mth_names.append(n)
                # being verbose for a while:
                #print 'applying DualMethod to %s.%s (using %s.%s)' % (name, n, c.__name__, n)
                setattr(func, n, DualMethod(mth, name))
        return

    def _update_Basic(func):
        name = func.__name__
        setattr(func, 'is_'+name, True)
        
        # set Basic.is_Class attribute:
        def is_cls(self): return False
        setattr(Basic, 'is_' + name, property(is_cls))

        # predefined objest is used by parser
        Basic.predefined_objects[name] = func

        # set Basic.Class attribute:
        setattr(Basic, name, func)

    def torepr(cls):
        return type.__repr__(cls)

    def tostr(cls, level=0):
        return cls.__name__

    @property
    def precedence(cls):
        return Basic.Atom_precedence

    def __hash__(cls):
        return hash(cls.__name__)

    def split(cls, op, *args, **kwargs):
        return [cls]

    def atoms(cls, type=None):
        if type is not None and not isinstance(type, (object.__class__, tuple)):
            type = Basic.sympify(type).__class__
        if type is None or isinstance(cls, type):
            return set([cls])
        return set()

    def compare(self, other):
        raise
        if isinstance(other, Basic):
            if other.is_Callable:
                return cmp(self.__name__, other.__name__)
        c = cmp(self.__class__, other.__class__)
        if c: return c
        raise NotImplementedError(`self, other`)

    def __eq__(self, other):
        if isinstance(other, Basic):
            if other.is_Callable:
                return self.__name__==other.__name__
            return False
        if isinstance(other, bool):
            return False
        if isinstance(other, type):
            if isinstance(self, type):
                return self.__name__ == other.__name__
            return False
        return sympify(other)==self

    def __nonzero__(cls):
        return False


def _get_class_statement(frame = None):
    """ Return a Python class definition line or None.
    The function must be called inside a __new__ function.
    """
    if frame is None:
        frame = sys._getframe(2)
    fn = frame.f_code.co_filename
    lno = frame.f_lineno
    if fn.endswith('.pyc') or fn.endswith('.pyo'):
        fn = fn[:-1]
    if os.path.isfile(fn):
        f = open(fn,'r')
        i = lno
        line = None
        while i:
            i -= 1
            line = f.readline()
        f.close()
        if line.lstrip().startswith('class '):
            return line
        if frame.f_back is not None:
            return _get_class_statement(frame.f_back)


class BasicFunctionType(Atom, Callable):
    """ Base class for defined symbolic function.

    Template for defined functions:

      class Func(<BasicFunction or its derivative>):
          signature = ...
          @classmethod
          def canonize(cls, args):
              ...

    Function symbols (also called as undefined functions):
    
      The statements

        Func = BasicFunctionType('Func'),
        Func = BasicFunctionType('Func', BasicFunction)
        Func = BasicFunctionType('Func', (BasicFunction,))
        Func = BasicFunctionType('Func', BasicFunction, {'signature':FunctionSignature(None, None)})

      are equivalent to

        class Func(BasicFunction):
            signature = FunctionSignature(None, None)

      except that no `is_Func` and `Func` attributes are added to Basic class.

    """

    def __new__(typ, name, bases=None, attrdict=None, is_global=None):
        if is_global is None:
            is_global = False
            if isinstance(bases, tuple) and isinstance(attrdict, dict):
                # The following statement reads python module that
                # defines class `name`:
                line = _get_class_statement()
                if line is not None:
                    if line.replace(' ','').startswith('class'+name+'('):
                        is_global = True
                    else:
                        print >> sys.stderr, 'Unexpected class definition line %r when defining class %r' % (line, name)
        if bases is None:
            bases = typ.instance_type
        if isinstance(bases, type):
            bases = (bases,)
        if attrdict is None:
            attrdict = {}

        func = Callable.__new__(typ, name, bases, attrdict)

        if not typ.__dict__.has_key('instance_type'):
            typ.instance_type = func

        if is_global:
            func._update_Basic()
        return func

    def torepr(cls):
        return cls.__name__

class BasicFunction(FunctionTemplate):
    """
    Base class for applied functions.
    Constructor of undefined classes.

    If Function class (or its derivative) defines a method that FunctionType
    also has then this method will be DualMethod, i.e. the method can be
    called as class method as well as an instance method.
    """
    __metaclass__ = BasicFunctionType

    def replace(self, old, new):
        old = sympify(old)
        new = sympify(new)
        if self==old:
            return new
        func = self.__class__
        flag = False
        if func==old:
            func = new
        if func is not self.__class__:
            flag = True
        args = []
        for a in self.args:
            new_a = a.replace(old, new)
            if new_a==a:
                new_a = a
            if new_a is not a:
                flag = True
            args.append(new_a)
        if flag:
            return func(*args)
        return self

    def split(cls, op, *args, **kwargs):
        return [cls]


class BasicLambda(Composite, Callable):
    """
    Lambda(x, expr) represents a lambda function similar to Python's
    'lambda x: expr'. A function of several variables is written
    Lambda((x, y, ...), expr).

    A simple example:
        >>> x = Symbol('x')
        >>> f = Lambda(x, x**2)
        >>> f(4)
        16
    """

    def __new__(cls, arguments, expression):
        if not isinstance(arguments, (tuple,list)):
            arguments = [sympify(arguments)]
        else:
            arguments = map(sympify, arguments)
        expr = sympify(expression)
        if expr.is_BasicFunction and tuple(arguments)==expr.args:
            return expr.__class__
        args = []
        # The bound variables must be changed to dummy symbols; otherwise
        # wrong results will be obtained if the Lambda is called with some of
        # the symbols that were used to define it. For example, without dummy
        # variables, Lambda((x, y), x*y)(y, x) will evaluate to x**2 or y**2
        # (depending on the order of substitution) instead of x*y because the
        # bound x or y gets mixed up with the unbound x or y.
        for a in arguments:
            d = a.as_dummy()
            expr = expr.replace(a, d)
            args.append(d)
        args = tuple(args)
        name = '%s(%s, %s)' % (cls.__name__, args, expr)
        bases = (BasicLambdaFunction,)
        attrdict = BasicLambdaFunction.__dict__.copy()
        attrdict['_args'] = args
        attrdict['_expr'] = expr
        attrdict['nofargs'] = len(args)
        func = type.__new__(cls, name, bases, attrdict)
        func.signature = FunctionSignature((Basic,)*len(args), Basic)
        return func


class BasicLambdaFunction(FunctionTemplate):
    """ Defines Lambda function properties.
    
    BasicLambdaFunction instances will be never created and therefore
    when subclassing BasicLambda subclassing BasicLambdaFunction
    is not needed.
    """
    __metaclass__ = Callable

    def __new__(cls, *args):
        n = cls.nofargs
        if n!=len(args):
            raise TypeError('%s takes exactly %s arguments (got %s)'\
                            % (cls, n, len(args)))
        expr = cls._expr
        for d,a in zip(cls._args, args):
            expr = expr.replace(d,sympify(a))
        return expr
