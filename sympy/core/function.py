
import os
import sys
import types

from .utils import DualMethod, DualProperty, get_class_statement
from .basic import Atom, Composite, Basic, BasicType, sympify, sympify_types1,\
     BasicWild, classes

from .sorting import sort_sequence
from .signature import FunctionSignature

__all__ = [
           'BasicFunctionType', 'BasicFunction',
           'BasicWildFunctionType',
           'BasicLambda', 'Callable']


def new_function_value(cls, args, options):
    if not isinstance(args, tuple):
        args = tuple(args)
    obj = object.__new__(cls)
    obj.args = args
    obj.options = options
    obj.func = cls
    obj.args_sorted = None    # use get_args_sorted() to initialize
    obj.args_frozenset = None # use get_args_frozenset() to initialize
    obj._hash_value = None
    return obj

class FunctionTemplate(Composite):
    """ Base class for function values.
    """
    # Not deriving FunctionTemplate from tuple because
    # we don't want to create an unnecessary copy of the
    # arguments tuple.

    signature = FunctionSignature(None, None)

    # When ordered_arguments is True then it is assumed
    # that the order of arguments is significant and
    # this will be taken into account when comparing
    # function instances. Otherwise arguments are compared
    # as frozenset's.
    ordered_arguments = True

    def __new__(cls, *args, **options):
        if options.get('is_canonical', False):
            r = None
            return new_function_value(cls, args, options)
        args = map(sympify, args)
        # options can only be used to control the canonize
        # method. options should not contain additional data
        # as the content of options are not used for comparing
        # instances nor for computing the hash value of an
        # instance. However, options can be used to save
        # temporary data when constructing an instance that
        # could be useful in certain operations. See
        # Addition and Multiplication operations as for
        # examples.
        errmsg = cls.signature.validate(cls.__name__, args)
        if errmsg is not None:
            raise TypeError(errmsg) #pragma NO COVER
        # since args is a list, canonize may change it in-place,
        # e.g. sort it.
        if cls.canonize.func_code.co_argcount==2:
            if options:
                raise NotImplementedError('%s.canonize method does not take'\
                                          ' options, got %r'\
                                          % (cls.__name__, options))
            r = cls.canonize(args)
        else:
            r = cls.canonize(args, options)
        if r is not None:
            errmsg = cls.signature.validate_return(cls.__name__, (r,))
            if errmsg is not None:
                raise TypeError(errmsg) #pragma NO COVER
            return r
        #options['is_canonical'] = True
        return new_function_value(cls, args, options)

    @classmethod
    def canonize(cls, args, options):
        return

    def __hash__(self):
        if self._hash_value is None:
            cls = self.__class__
            if cls.ordered_arguments:
                self._hash_value = hash((cls.__name__, self.args))
            else:
                self._hash_value = hash((cls.__name__, self.get_args_frozenset()))
        return self._hash_value

    def count_ops(self, symbolic=True):
        if symbolic:
            counter = self.func
        else:
            counter = 1
        for a in self.args:
            counter += a.count_ops(symbolic=symbolic)
        return counter

    def __iter__(self):
        return iter(self.args)

    def get_args_frozenset(self):
        if self.args_frozenset is None:
            self.args_frozenset = frozenset(self.args)
        return self.args_frozenset

    def get_args_sorted(self):
        if self.args_sorted is None:
            self.args_sorted = tuple(sort_sequence(self.args))
        return self.args_sorted

    def iterSorted(self):
        return iter(self.get_args_sorted())

    def __len__(self):
        return len(self.args)

    def __getitem__(self, key):
        return self.args[key]

    def __eq__(self, other):
        if isinstance(other, sympify_types1):
            other = sympify(other)
        if isinstance(other, Basic):
            if not isinstance(other, classes.BasicFunction):
                return False
            if self.func==other.func:
                if self.func.ordered_arguments:
                    return self.args==other.args
                else:
                    return self.get_args_frozenset()==other.get_args_frozenset()
            return False
        if isinstance(other, str):
            return self==sympify(other)
        return False

    @DualProperty
    def precedence(cls):
        return Basic.Apply_precedence

    def torepr(self):
        return '%s(%s)' % (self.__class__.torepr(),
                           ', '.join([a.torepr() for a in self.args]))

    def tostr(self, level=0):
        p = self.precedence
        r = '%s(%s)' % (self.__class__.tostr(),
                        ', '.join([a.tostr() for a in self.args]))
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
        return Basic.atoms(self, type).union(self.func.atoms(type))

    def matches(pattern, expr, repl_dict={}, evaluate=False):
        d = Basic.matches(pattern, expr, repl_dict)
        if d is not None: return d
        if not isinstance(expr, classes.FunctionTemplate): return
        if len(pattern.args)!=len(expr.args): return

        fd = pattern.func.matches(expr.func, repl_dict)
        if fd is None: return
        for pa, ea in zip(pattern.args, expr.args):
            fd = pa.replace_dict(fd).matches(ea, fd)
            if fd is None: return
        return fd


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
            for n,mth in c.__dict__.iteritems():
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

        # set Basic.Class attribute:
        setattr(classes, name, func)

    def torepr(cls):
        return type.__repr__(cls)

    def tostr(cls, level=0):
        return cls.__name__

    @property
    def precedence(cls):
        return Basic.Atom_precedence

    def atoms(cls, type=None):
        if type is not None and not isinstance(type, (object.__class__, tuple)):
            type = sympify(type).__class__
        if type is None or isinstance(cls, type):
            return set([cls])
        return set()

    def __eq__(cls, other):
        if isinstance(other, sympify_types1):
            other = sympify(other)
        if isinstance(other, Basic):
            if isinstance(other, classes.Callable):
                return cls.__name__==other.__name__
        return False

    def compare(cls, other):
        return cmp(cls.__name__, other.__name__)

    def __hash__(cls):
        return hash(cls.__name__)

    def __nonzero__(cls):
        return False


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
                line = get_class_statement()
                if line is not None:
                    if line.replace(' ','').startswith('class'+name+'('):
                        is_global = True
                    else:
                        print >> sys.stderr, 'Unexpected class definition line'\
                              ' %r when defining class %r' % (line, name) #pragma NO COVER
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


class BasicWildFunctionType(BasicWild, BasicFunctionType):
    # Todo: derive BasicWildFunctionType from BasicDummyFunctionType.
    def __new__(typ, name=None, bases=None, attrdict=None, is_global=None, predicate=None):
        if name is None:
            name = 'WF'
        func = BasicFunctionType.__new__(typ, name, bases, attrdict, is_global)
        if predicate is None:
            predicate = lambda expr: isinstance(expr, classes.BasicFunctionType)
        func.predicate = staticmethod(predicate)
        return func

    
class BasicFunction(FunctionTemplate):
    """
    Base class for applied functions.
    Constructor of undefined classes.

    If Function class (or its derivative) defines a method that FunctionType
    also has then this method will be DualMethod, i.e. the method can be
    called as class method as well as an instance method.
    """
    __metaclass__ = BasicFunctionType

    def try_replace(self, old, new):
        func = self.func
        flag = False
        if isinstance(old, classes.BasicFunctionType) and isinstance(new, classes.BasicFunctionType) and old==func:
            func = new
        if func is not self.func:
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
        #return self


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
        if isinstance(expr, classes.BasicFunction) and tuple(arguments)==expr.args:
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
        attrdict['_hashvalue'] = None
        attrdict['_symbol_cls'] = cls._symbol_cls
        func = type.__new__(cls, name, bases, attrdict)
        func.signature = FunctionSignature((Basic,)*len(args), Basic)
        return func

    def __eq__(func, other):
        if isinstance(other, sympify_types1):
            other = sympify(other)
        if isinstance(other, Basic) and isinstance(other, classes.Callable) and func.__name__==other.__name__:
            # other is also a lambda function.
            if func.nofargs==other.nofargs:
                return func._expr == other(*func._args)
        return False

    def compare(func, other):
        c = cmp(func.nofargs, other.nofargs)
        if c:
            return c
        c = cmp(func._expr.count_ops(symbolic=False),
                other._expr.count_ops(symbolic=False))
        if c:
            return c
        return cmp(__func.name__, other.__name__)

    def __hash__(func):
        if func._hashvalue is None:
            args = [func._symbol_cls('__%i_lambda_hash_symbol__') for i in range(func.nofargs)]
            func._hashvalue = hash(func(*args))
        return func._hashvalue

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


