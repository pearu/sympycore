
import types
#from utils import dualmethod, dualproperty, FDiffMethod, Decorator
from utils import DualMethod, DualProperty, FDiffMethod
from basic import Atom, Composite, Basic, BasicType, sympify
from methods import ArithMeths

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
                raise TypeError('%s: wrong number of arguments, expected %s, got %s'\
                                % (funcname, self.nof_arguments, len(args)))
            for a,cls in zip(args, self.argument_classes):
                if not isinstance(a, cls):
                    raise TypeError('%s: wrong argument type %r, expected %s' % (funcname, a, cls))
        elif cls is not None:
            for a in args:
                if not isinstance(a, cls):
                    raise TypeError('%s: wrong argument type %r, expected %s' % (funcname, a, cls))

    def __repr__(self):
        return '%s(%r, %r)' % (self.__class__.__name__,
                               self.argument_classes,
                               self.value_classes)

Basic.FunctionSignature = FunctionSignature

class FunctionClass(ArithMeths, Atom, BasicType):
    """
    Base class for function classes. FunctionClass is a subclass of type.

    Use Function('<function name>' [ , signature ]) to create
    undefined function classes.

    """

    def __new__(typ, *args, **kws):
        if isinstance(args[0], type):
            # create a class of undefined function
            if len(args)==2:
                ftype, name = args
                attrdict = ftype.__dict__.copy()
            else:
                ftype, name, signature = args
                attrdict = ftype.__dict__.copy()
                attrdict['signature'] = signature
            assert ftype is UndefinedFunction,`ftype`
            bases = (ftype,)
            #typ.set_methods_as_dual(name, attrdict)
            func = type.__new__(typ, name, bases, attrdict)
        else:
            # defined functions
            name, bases, attrdict = args

            attrdict['is_'+name] = DualProperty(lambda self:True)
            setattr(Basic, 'is_' + name,
                    property(lambda self:False,
                             lambda cls:isinstance(cls, getattr(Basic, name))))
            
            func = type.__new__(typ, name, bases, attrdict)

            typ._fix_methods(func, attrdict)

            # predefined objest is used by parser
            Basic.predefined_objects[name] = func

            # set Basic.Class attributes:
            setattr(Basic, func.__name__, func)
            
        return func

    @classmethod
    def _fix_methods(cls, func, attrdict):
        """ Apply DualMethod and FDiffMethod to func methods.
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
                if n=='fdiff':
                    #print 'applying FDiffMethod to %s.%s' % (name, n)
                    setattr(func, n, FDiffMethod(mth, name))
                else:
                    #print 'applying DualMethod to %s.%s (using %s.%s)' % (name, n, c.__name__, n)
                    setattr(func, n, DualMethod(mth, name))
        return

    def torepr(cls):
        if issubclass(cls, UndefinedFunction):
            for b in cls.__bases__:
                if b.__name__.endswith('Function'):
                    return "%s('%s')" % (b.__name__, cls.__name__)
            return "Function('%s')" % (cls.__name__)
        return type.__repr__(cls)

    def tostr(cls, level=0):
        return cls.__name__

    @property
    def precedence(cls):
        return Basic.Atom_precedence

    def try_power(cls, exponent):
        return

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
            if other.is_FunctionClass:
                return cmp(self.__name__, other.__name__)
        c = cmp(self.__class__, other.__class__)
        if c: return c
        raise NotImplementedError(`self, other`)

    def __eq__(self, other):
        if isinstance(other, Basic):
            if other.is_FunctionClass:
                return self.__name__==other.__name__
            return False
        if isinstance(other, bool):
            return False
        if isinstance(other, type):
            if isinstance(self, type):
                return self.__name__ == other.__name__
            return False
        return sympify(other)==self

class Function(ArithMeths, Composite, tuple):
    """
    Base class for applied functions.
    Constructor of undefined classes.

    If Function class (or its derivative) defines a method that FunctionClass
    also has then this method will be DualMethod, i.e. the method can be
    called as class method as well as an instance method.
    """

    __metaclass__ = FunctionClass
    
    signature = FunctionSignature(None, None)
    return_canonize_types = (Basic,)

    def __new__(cls, *args, **options):
        if cls.__name__.endswith('Function'):
            if cls is Function and len(args)==1:
                # Default function signature is of SingleValuedFunction
                # that provides basic arithmetic methods.
                cls = UndefinedFunction
            return FunctionClass(cls, *args)
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

    def __hash__(self):
        try:
            return self.__dict__['_cached_hash']
        except KeyError:
            h = hash((self.__class__.__name__, tuple(self)))
            self._cached_hash = h
        return h

    def __eq__(self, other):
        if isinstance(other, Basic):
            if not other.is_Function: return False
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
        
    @classmethod
    def canonize(cls, args, **options):
        return

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

    @DualProperty
    def precedence(cls):
        return Basic.Apply_precedence

    def subs(self, old, new):
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
            new_a = a.subs(old, new)
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

    def atoms(self, type=None):
        return Basic.atoms(self, type).union(self.__class__.atoms(type))

    def __call__(self, *args):
        """
        (f(g))(x) -> f(g(x))
        (f(g1,g2))(x) -> f(g1(x), g2(x))
        """
        return self.__class__(*[a(*args) for a in self.args])

    def try_derivative(self, s):
        i = 0
        l = []
        r = Basic.zero
        args = self.args
        for a in args:
            i += 1
            da = a.diff(s)
            if da.is_zero:
                continue
            df = self.func.fdiff(i)
            l.append(df(*args) * da)
        return Basic.Add(*l)

    # See utils.FDiffMethod docs for how fdiff and instance_fdiff methods are called.
    def fdiff(cls, index=1):
        raise NotImplementedError('%s.fdiff(cls, index=1)' % (cls.__name__))

    def instance_fdiff(self, index=1):
        # handles: sin(cos).fdiff() -> sin'(cos) * cos' -> cos(cos) * sin
        i = 0
        l = []
        for a in self.args:
            i += 1
            df = self.func.fdiff(i)(*self.args)
            da = a.fdiff(index)
            l.append(df * da)
        return Basic.Add(*l)

class UndefinedFunction(Function):

    signature = FunctionSignature(None, (Basic,))

    def fdiff(cls, index=1):
        return UndefinedFunction('%s_%s' % (cls.__name__, index), cls.signature)

class SingleValuedFunction(Function):
    """
    Single-valued functions.
    """
    signature = FunctionSignature(None, (Basic,))

class Lambda(FunctionClass):
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
        if expr.is_Function and tuple(arguments)==expr.args:
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
            expr = expr.subs(a, d)
            args.append(d)
        args = tuple(args)
        name = 'Lambda(%s, %s)' % (args, expr)
        bases = (LambdaFunction,)
        attrdict = LambdaFunction.__dict__.copy()
        attrdict['_args'] = args
        attrdict['_expr'] = expr
        attrdict['nofargs'] = len(args)
        func = type.__new__(cls, name, bases, attrdict)        
        return func

    def __init__(cls,*args):
        pass

class LambdaFunction(Function):
    """ Defines Lambda function properties.
    
    LambdaFunction instance will never be created.
    """

    def __new__(cls, *args):
        n = cls.nofargs
        if n!=len(args):
            raise TypeError('%s takes exactly %s arguments (got %s)'\
                            % (cls, n, len(args)))
        expr = cls._expr
        for d,a in zip(cls._args, args):
            expr = expr.subs(d,sympify(a))
        return expr
