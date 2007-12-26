
import os
import sys
import types

from .utils import InstanceClassMethod, instancemethod, get_class_statement
from .basic import Atom, Composite, Basic, BasicType, sympify, sympify_types1,\
     BasicWild, classes

from .sorting import sort_sequence
from .signature import FunctionSignature

__all__ = [
           'BasicFunctionType', 'BasicFunction',
           'BasicParametricFunction', 'BasicOperator',
           'BasicWildFunctionType',
           'BasicLambda',
           ]

def new_type(cls, name, bases=(), attrdict={}, is_global=None):
    """ Create a new class object with name.
    
    When is_global is True, then the created type will be set
    as an `classes` instance attribute with `name`.
    """
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

    if isinstance(bases, type):
        bases = (bases,)

    t = getattr(cls, '_instance_type', None)
    if t is not None:
        for b in bases:
            if issubclass(b, t):
                t = None
                break
        if t is not None:
            bases = bases + (t,)

    # create class object:
    obj = type.__new__(cls, name, bases, attrdict)

    if not cls.__dict__.has_key('_instance_type'):
        setattr(cls, '_instance_type', obj)

    if is_global:
        setattr(classes, name, obj)

    return obj

    

class BasicFunctionType(Basic, BasicType):
    """ Metaclass to BasicFunction classes.
    """

    __new__ = new_type

    # Here we create methods that Basic class defines
    # but these methods will call classmethods of classes
    # which have BasicFunctionType as metaclass.
    for _k, _v in Basic.__dict__.iteritems():
        if _k in ('__new__', '__init__'):
            continue
        if isinstance(_v, types.FunctionType):
            exec '''\
def %(name)s(cls, *args, **kwargs):
    mth = cls.%(name)s
    type_mth = type(cls).%(name)s
    if mth.im_func is type_mth.im_func:
        raise NotImplementedError(\'%%s must implement %(name)s method.\' %% (cls))
    return mth(*args, **kwargs)
''' % dict(name=_k)
    del _k, _v

    # Object methods:

    def __ne__(self, other):
        return not (self == other)

    def compare(cls, other):
        return cmp(cls.__name__, other.__name__)

    def __hash__(cls):
        return hash(cls.__name__)

    def __nonzero__(cls):
        return False

    # Output methods:

    precedence = Basic.Atom_precedence

    # Informational methods:
    

def new_function(cls, args, options):
    name = '%s(%s)' % (cls.__name__, ', '.join(map(str, args)))
    attrdict = {}
    attrdict.update(dict(args = args,
                         func = cls,
                         is_operator = False,
                         is_function = True))
    obj = new_type(cls.__metaclass__, name,
                   bases = (cls, ),
                   attrdict=attrdict)
    return obj

def new_function_value(cls, args, options):
    """ Create a BasicFunction instance.
    """
    if not isinstance(args, tuple):
        args = tuple(args)
    obj = object.__new__(cls)
    obj.args = args
    obj.options = options
    obj.func = cls
    obj.args_sorted = None    # use get_args_sorted() to initialize
    obj.args_frozenset = None # use get_args_frozenset() to initialize
    obj._hash_value = None
    obj.is_function = False
    return obj

class BasicFunction(Composite):
    """ Base class for symbolic functions.

    BasicFunction class objects are Basic instances.
    """
    ###########################################################################
    # IMPORTANT!! ON DEFINING METHODS FOR BasicFunction OR FOR ITS SUBCLASSES #
    ###########################################################################
    #
    # Note that BasicFunction class object is an instance of Basic class, and
    # so are BasicFunction instances instances of the Basic class. This means
    # that when defining a method for BasicFunction, one has to specify whether
    # it is a class method or an instance method, so that, for example, the
    # following calls
    #
    #   Sin.tostr()    -> 'Sin'
    #   Sin(x).tostr() -> 'Sin(x)'
    #
    # could work.
    #
    # In order to achive the above, all BasicFunction methods must be decorated
    # with `instancemethod(<classmethod instance>)` decorator. If a method
    # is not decorated with this decorator, then the method is usable only
    # for instances of BasicFunction (if Basic implements an method then
    # an NotImplementedError will be raised when the method is tried to
    # use as a classmethod).
    # Constructor methods __new__, __init__ are exceptions.
    #
    # Here follows some examples how to use instancemethod decorator:
    #
    # 1) (Re)define class and instance method in a BasicFunction (sub)class
    #
    #   @classmethod
    #   def tostr(cls, level=0):
    #       return ...
    #
    #   @instancemethod(tostr)
    #   def tostr(self, level=0):
    #       return ...
    #
    # 2) Redefine classmethod in a BasicFunction (sub)class:
    #
    #   @classmethod
    #   def tostr(cls, level=0):
    #       return ...
    #
    #   2.1)
    #   tostr = instancemethod(tostr)(Basic.tostr)
    #
    #   2.2)
    #   # or if base class is a BasicFunction (sub)class then one
    #   # must use __dict__ directly:
    #
    #   tostr = instancemethod(tostr)(BasicFunction.__dict__['tostr'])
    #
    #   2.3)
    #   # or let instancemethod find the instance method from the
    #   # __dict__ of base classes:
    #
    #   tostr = instancemethod(tostr)(BasicFunction)
    #    
    # 3) Redefine instance method in a BasicFunction (sub)class:
    #
    #   @instancemethod(BasicFunction.tostr)
    #   def tostr(self, level=0):
    #       return ...
    #
    #   # note that using `BasicFunction.tostr` above is correct
    #   # as the returned `BasicFunction.tostr` refers to a classmethod.
    #
    ############################################################################

    __metaclass__ = BasicFunctionType

    # When ordered_arguments is True then it is assumed
    # that the order of arguments is significant and
    # this will be taken into account when comparing
    # function instances. Otherwise arguments are compared
    # as frozenset's. Commutative operations should
    # set ordered_arguments = False.

    ordered_arguments = True

    # Constructor methods:

    def __new__(cls, *args, **options):
        # options can only be used to control the canonize
        # method. options should not contain additional data
        # as the content of options are not used for comparing
        # instances nor for computing the hash value of an
        # instance. However, options can be used to save
        # temporary data when constructing an instance that
        # could be useful in certain operations.

        if options.get('is_canonical', False):
            return new_function_value(cls, args, options)

        args = map(sympify, args)

        if cls.canonize.func_code.co_argcount==2:
            if options:
                raise NotImplementedError('%s.canonize method does not take'\
                                          ' options, got %r'\
                                          % (cls.__name__, options))
            obj = cls.canonize(args)
        else:
            obj = cls.canonize(args, options)

        if obj is not None:
            return obj

        return new_function_value(cls, args, options)

    @classmethod
    def canonize(cls, args):
        return

    

    # Iterator methods:

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

    # Object methods:

    def __hash__(self):
        if self._hash_value is None:
            cls = self.func
            if cls.ordered_arguments:
                self._hash_value = hash((cls.__name__, self.args))
            else:
                self._hash_value = hash((cls.__name__, self.get_args_frozenset()))
        return self._hash_value

    @classmethod
    def __eq__(cls, other):
        if isinstance(other, sympify_types1):
            other = sympify(other)
        if isinstance(other, Basic):
            if isinstance(other, classes.BasicFunctionType):
                return cls.__name__==other.__name__
        return False

    @instancemethod(__eq__)
    def __eq__(self, other):
        if isinstance(other, sympify_types1):
            other = sympify(other)
        if isinstance(other, Basic):
            if not isinstance(other, BasicFunction):
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

    # Output methods:

    @property
    def precedence(self):
        return Basic.Apply_precedence

    @classmethod
    def torepr(cls):
        return type.__repr__(cls)

    @instancemethod(torepr)
    def torepr(self):
        return '%s(%s)' % (self.func.tostr(),
                           ', '.join([a.torepr() for a in self.args]))

    @classmethod
    def tostr(cls, level=0):
        return cls.__name__

    @instancemethod(tostr)
    def tostr(self, level=0):
        p = self.precedence
        r = '%s(%s)' % (self.func.tostr(),
                        ', '.join([a.tostr() for a in self.args]))
        if p<=level:
            return '(%s)' % (r)
        return r

    __str__ = instancemethod(Basic.__str__)(Basic.__str__)
    __repr__ = instancemethod(Basic.__repr__)(Basic.__repr__)

    # Informational methods:

    @classmethod
    def count_ops(self, symbolic=True):
        return 0

    @instancemethod(count_ops)
    def count_ops(self, symbolic=True):
        if symbolic:
            counter = self.func
        else:
            counter = 1
        for a in self.args:
            counter += a.count_ops(symbolic=symbolic)
        return counter

    @classmethod
    def atoms(cls, type=None):
        if type is not None and not isinstance(type, (object.__class__, tuple)):
            type = sympify(type).__class__
        if type is None or isinstance(cls, type):
            return set([cls])
        return set()

    @instancemethod(atoms)
    def atoms(self, type=None):
        return Basic.atoms(self, type).union(self.func.atoms(type))


    # Match methods:
    match = instancemethod(Basic.match)(Basic.match)
    
    @classmethod
    def matches(pattern, expr, repl_dict={}, evaluate=False):
        """
        Helper method for match().
        """
        # check if pattern has already a match:
        v = repl_dict.get(pattern, None)
        if v is not None:
            if v==expr:
                return repl_dict
            return
        # match exactly
        if pattern==expr:
            return repl_dict

    @instancemethod(matches)
    def matches(pattern, expr, repl_dict={}, evaluate=False):
        d = Basic.matches(pattern, expr, repl_dict)
        if d is not None:
            return d
        if not isinstance(expr, classes.BasicFunction):
            return
        if len(pattern.args)!=len(expr.args):
            return

        fd = pattern.func.matches(expr.func, repl_dict)
        if fd is None:
            return
        for pa, ea in zip(pattern.args, expr.args):
            fd = pa.replace_dict(fd).matches(ea, fd)
            if fd is None:
                return
        return fd

    # Substitution methods:
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
        return

    def __call__(self, *args):
        """
        (f(g))(x) -> f(g(x))
        (f(g1,g2))(x) -> f(g1(x), g2(x))
        """
        return self.func(*[a(*args) for a in self.args])

class BasicOperator(BasicFunction):

    is_metaoperator = True
    is_operator = False
    is_function = False

    def __new__(cls, *args):
        obj = cls.canonize(args)
        if obj is not None:
            return obj
        if cls.is_metaoperator:
            name = '%s(%s)' % (cls.__name__, ', '.join(map(str, args)))
            obj = new_type(type(cls), name, bases = (cls, ),
                         attrdict=dict(args=args,
                                       is_metaoperator = False,
                                       is_operator = True))
            return obj

        if cls.is_operator:
            return new_function(cls, args, options)
        return new_function_value(cls, args, options)


class BasicParametricFunction(BasicFunction):

    is_operator = True
    is_function = False

    def __new__(cls, *args, **options):
        
        if options.get('is_canonical', False):
            if cls.is_operator:
                return new_function(cls, args, options)
            return new_function_value(cls, args, options)

        args = map(sympify, args)

        if cls.canonize.func_code.co_argcount==2:
            if options:
                raise NotImplementedError('%s.canonize method does not take'\
                                          ' options, got %r'\
                                          % (cls.__name__, options))
            obj = cls.canonize(args)
        else:
            obj = cls.canonize(args, options)

        if obj is not None:
            return obj
        
        if cls.is_operator:
            return new_function(cls, args, options)
        return new_function_value(cls, args, options)


class FunctionTemplate_obsolete(Composite):
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
        # could be useful in certain operations.
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

    #@DualProperty
    def precedence(cls):
        return Basic.Apply_precedence

    def __call__(self, *args):
        """
        (f(g))(x) -> f(g(x))
        (f(g1,g2))(x) -> f(g1(x), g2(x))
        """
        return self.__class__(*[a(*args) for a in self.args])

    
class BasicWildFunctionType(BasicWild, BasicFunctionType):
    # Todo: derive BasicWildFunctionType from BasicDummyFunctionType.

    def __new__(typ, name=None, bases=(), attrdict={}, is_global=None, predicate=None):
        if name is None:
            name = 'WF'
        attrdict['matches'] = instancemethod(BasicWild.matches)(BasicFunction.__dict__['matches'])
        func = BasicFunctionType.__new__(typ, name, bases, attrdict, is_global)
        if predicate is None:
            predicate = lambda expr: isinstance(expr, classes.BasicFunctionType)
        func.predicate = staticmethod(predicate)
        return func



class BasicLambda(BasicParametricFunction):
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
    @classmethod
    def canonize(cls, args):
        if cls.is_operator:
            arguments, expr = args
            if not isinstance(arguments, classes.Tuple):
                arguments = classes.Tuple(arguments)
            if isinstance(expr, classes.BasicFunction) and tuple(arguments)==expr.args:
                return expr.__class__
            new_arguments = []
            # The bound variables must be changed to dummy symbols; otherwise
            # wrong results will be obtained if the Lambda is called with some of
            # the symbols that were used to define it. For example, without dummy
            # variables, Lambda((x, y), x*y)(y, x) will evaluate to x**2 or y**2
            # (depending on the order of substitution) instead of x*y because the
            # bound x or y gets mixed up with the unbound x or y.
            for a in arguments:
                d = a.as_dummy()
                expr = expr.replace(a, d)
                new_arguments.append(d)
            new_arguments = classes.Tuple(*new_arguments)
            obj = cls(new_arguments, expr, is_canonical=True)
            obj._args = new_arguments
            obj._expr = expr
            obj._nofargs = len(new_arguments)
            obj._symbol_cls = cls._symbol_cls
            return obj
        
        assert cls.is_function, `cls.is_function`
        n = cls._nofargs
        if n!=len(args):
            raise TypeError('%s takes exactly %s arguments (got %s)' % (cls, n, len(args)))
        expr = cls._expr
        for d,a in zip(cls._args, args):
            expr = expr.replace(d, a)
        return expr        

    @classmethod
    def __eq__(self, other):
        if isinstance(other, sympify_types1):
            other = sympify(other)
        if isinstance(other, type(self)) and issubclass(other, BasicLambda):
            if self._nofargs==other._nofargs:
                return self._expr == other(*self._args)
        return False

    __eq__ = instancemethod(__eq__)(BasicParametricFunction)

class BasicLambda2(Composite, BasicFunctionType):

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
        if isinstance(other, Basic) and isinstance(other, classes.BasicFunctionType) and func.__name__==other.__name__:
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

