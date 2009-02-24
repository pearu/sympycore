"""Provides Basic class and classes object.
"""

__docformat__ = 'restructuredtext'
__all__ = ['classes', 'Expr', 'defined_functions', 'DefinedFunction',
           'objects', 'Pair', 'IntegerList']

import sys
import types
import inspect

using_C_Expr = False
try:
    from . import expr_ext as expr_module
    using_C_Expr = True
except ImportError, msg:
    msg = str(msg)
    if msg!='No module named expr_ext' and msg!='cannot import name expr_ext':
        print msg
    from . import expr as expr_module

Expr = expr_module.Expr
Pair = expr_module.Pair

# Pickling support:
def _reconstruct(version, state):
    # Returned by <Expr instance>.__reduce__
    if version==1:
        cls, (head, data), hashvalue = state
        head = get_head(head)
        obj = cls(head, data)
        obj._sethash(hashvalue)
        return obj
    elif version==2:
        from .utils import get_head
        cls, (head, data), hashvalue = state
        if type(cls) is tuple:
            cls = cls[0](*cls[1])
        head = get_head(head)
        obj = cls(head, data)
        obj._sethash(hashvalue)
        return obj
    elif version==3:
        cls, (head, data), hashvalue = state
        if type(cls) is tuple:
            cls = cls[0](*cls[1])
        head = getattr(head, 'as_unique_head', lambda head=head: head)()
        obj = cls(head, data)
        obj._sethash(hashvalue)
        return obj
    raise NotImplementedError('pickle _reconstruct version=%r' % (version))

if using_C_Expr:
    # To add support pickling pure Expr instances, uncomment the
    # following line (but it is hackish):
    #
    #__builtins__['Expr'] = Expr
    #
    # Pickling Python classes derived from Expr should work fine
    # without this hack.
    pass

class Holder:
    """ Holds pairs ``(name, value)`` as instance attributes.
    
    The set of Holder pairs is extendable by

    ::
    
      <Holder instance>.<name> = <value>

    and the values are accessible as

    ::

      value = <Holder instance>.<name>
    """
    def __init__(self, descr):
        self._descr = descr
        self._counter = 0

    def __str__(self):
        return self._descr % (self.__dict__)

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, str(self))
    
    def __setattr__(self, name, obj):
        if not self.__dict__.has_key(name) and self.__dict__.has_key('_counter'):
            self._counter += 1
        self.__dict__[name] = obj

    def iterNameValue(self):
        for k,v in self.__dict__.iteritems():
            if k.startswith('_'):
                continue
            yield k,v

classes = Holder('SympyCore classes holder (%(_counter)s classes)')
objects = Holder('SympyCore objects holder (%(_counter)s classes)')
heads = Holder('SympyCore expression heads holder (%(_counter)s heads)')
heads_precedence = Holder('SympyCore heads precedence holder (%(_counter)s items).')
defined_functions = Holder('SympyCore defined functions holder (%(_counter)s classes)')

class FunctionType(type):
    """ Metaclass to Function class.

    FunctionType implements the following features:

    1. If a class derived from ``Function`` has a name containing
       substring ``Function`` then the class will be saved as an
       attribute to ``classes`` holder. Such classes are assumed to
       be base classes to defined functions.

    2. Otherwise, ``Function`` subclasses are saved as attributes to
       ``defined_functions`` holder.

    """

    def __new__(typ, name, bases, attrdict):
        cls = type.__new__(typ, name, bases, attrdict)
        if 'Function' in name:
            setattr(classes, name, cls)
        else:
            setattr(defined_functions, name, cls)
        return cls

class DefinedFunction(object):
    """ Base class to symbolic functions.
    """
    __metaclass__ = FunctionType

    @classmethod
    def derivative(cls, arg):
        """ Return derivative function of cls at arg.
        """
        raise NotImplementedError(`cls, arg`)

    @classmethod
    def get_argument_algebras(cls):
        raise NotImplementedError(`cls`)

def get_nargs(obj):
    assert callable(obj),`obj`
    if isinstance(obj, classes.FunctionRing):
        return obj.nargs
    if inspect.isclass(obj):
        return len(inspect.getargspec(obj.__new__)[0])-1
    if inspect.isfunction(obj):
        return len(inspect.getargspec(obj)[0])
    if inspect.ismethod(obj):
        return len(inspect.getargspec(obj)[0]) - 1
    raise NotImplementedError(`obj`)        

classes.Expr = Expr
classes.Pair = Pair

class SymbolicEquality:
    """ Contex for logical operations.

    In the ``SymbolicEquality(<Algebra class>)`` context relational
    operations return ``Logic`` instances instead of computing
    lexicographic value of relational operations.

    For example,

    >>> x = Calculus('x')
    >>> with SymbolicEquality(Calculus):
    >>>     print x==x
    ...     
    ...     
    x==x
    >>> print x==x
    True

    Add ``from __future__ import with_statement`` to the header of
    python file when using Python version 2.5.
    
    """

    def __init__(self, *classes):
        self.classes = classes

    def __enter__(self):
        for cls in self.classes:
            cls.enable_symbolic_comparison()

    def __exit__(self, type, value, tb):
        for cls in self.classes:
            cls.disable_symbolic_comparison()
        return tb is None

class InitModule:
    
    """ Holds a list of functions (or callable objects), composed by
    that are called exactly once by the execute methods. Functions are
    assumed to take one argument holding a module object. InitModule
    instance can be used as a decorator or functions can be added to
    the list using the register method.
    """

    def __init__(self):
        self.func_list = []
        
    def register(self, init_module_func):
        """ Register a function for execution.
        """
        if callable(init_module_func):
            self.func_list.append(init_module_func)

    def execute(self):
        """ Execute registered functions and discard them.
        """
        while self.func_list:
            func = self.func_list.pop(0)
            module_name = func.__module__
            module = sys.modules[module_name]
            #print 'Executing %s(%s):' % (func.__name__, module.__name__)
            func(module)

    def __call__(self, func):
        """ Register function via decorating it.
        """
        self.register(func)

    def import_heads(self):
        """Registers a function that adds heads symbols to a calling
        module.
        """
        frame = sys._getframe(1)
        module_name = frame.f_locals['__name__']

        def _import_heads(module):
            from sympycore.core import heads
            for n,h in heads.iterNameValue():
                setattr(module, n, h)

        _import_heads.__module__ = module_name

        self.register(_import_heads)

    def import_lowlevel_operations(self):
        """Registers a function that adds lowlevel operation functions
        like dict_get_item, dict_add_item, etc to a calling module.
        """
        frame = sys._getframe(1)
        module_name = frame.f_locals['__name__']
        
        def _import_lowlevel_operations(module):
            for n in dir(expr_module):
                if 'dict' in n or 'new' in n and not n.startswith('_'):
                    setattr(module, n, getattr(expr_module, n))
            module.IntegerList = IntegerList
            
        _import_lowlevel_operations.__module__ = module_name

        self.register(_import_lowlevel_operations)

    def import_numbers(self):
        """Registers a function that adds numbers and number types
        collections to a calling module.
        """
        frame = sys._getframe(1)
        module_name = frame.f_locals['__name__']
        
        def _import_numbers(module):
            from sympycore.arithmetic import numbers
            module.numbertypes = numbers.numbertypes
            module.numbertypes_set = numbers.numbertypes_set
            module.inttypes = numbers.inttypes
            module.rationaltypes = numbers.rationaltypes
            module.realtypes = numbers.realtypes
            module.complextypes = numbers.complextypes
            module.Infinity = numbers.Infinity
            module.number_div = numbers.number_div
            
        _import_numbers.__module__ = module_name

        self.register(_import_numbers)

init_module = InitModule()
init_module.register(expr_module.init_module)

init_module.import_heads()

class IntegerList(Expr):
    """ IntegerList holds a list of integers and supports element-wise
    arithmetic operations.
    """

    @classmethod
    def convert(cls, arg, typeerror=True):
        t = type(arg)
        if t is int or t is long:
            return cls(INTEGER_LIST, [arg])
        if t is list:
            return cls(INTEGER_LIST, arg)
        if t is tuple:
            return cls(INTEGER_LIST, list(arg))
        if t is IntegerList:
            return arg
        if typeerror:
            raise TypeError('failed to convert %r to IntegerList' % (arg))
        return NotImplemented

    def __repr__(self):
        return '%s(%s)' % (type(self).__name__, self.data)

    def __len__(self): return len(self.data)

    def __getitem__(self, index):
        return self.data[index]

    def __setitem__(self, index, value):
        if self.is_writable:
            self.data[index] = value
        else:
            raise TypeError('this IntegerList instance is not writable')
        
    def __pos__(self):
        return self

    def __neg__(self):
        return IntegerList(INTEGER_LIST, [-i for i in self.data])

    def __add__(self, other):
        lhead, ldata = self.pair
        t = type(other)
        if t is int or t is long:
            if other==0:
                return self
            return IntegerList(INTEGER_LIST, [i + other for i in ldata])
        if t is IntegerList:
            rdata = other.data
        elif t is list or t is tuple:
            rdata = other
        else:
            return NotImplemented
        if len(ldata)!=len(rdata):
            raise TypeError('IntegerList.__add__ operands must have the same size')
        return IntegerList(INTEGER_LIST, [i + j for i,j in zip(ldata, rdata)])

    __radd__ = __add__

    def __sub__(self, other):
        t = type(other)
        if t is int or t is long:
            if other==0:
                return self
            return IntegerList(INTEGER_LIST, [i - other for i in self.data])
        ldata = self.data
        if t is IntegerList:
            rdata = other.data
        elif t is list or t is tuple:
            rdata = other
        else:
            return NotImplemented
        if len(ldata)!=len(rdata):
            raise TypeError('IntegerList.__sub__ operands must have the same size')
        return IntegerList(INTEGER_LIST, [i - j for i,j in zip(ldata, rdata)])

    def __rsub__(self, other):
        return (-self) + other

    def __mul__(self, other):
        t = type(other)
        if t is int or t is long:
            if other==1:
                return self
            return IntegerList(INTEGER_LIST, [i * other for i in self.data])
        ldata = self.data
        if t is IntegerList:
            rdata = other.data
        elif t is list or t is tuple:
            rdata = other
        else:
            return NotImplemented
        if len(ldata)!=len(rdata):
            raise TypeError('IntegerList.__mul__ operands must have the same size')
        return IntegerList(INTEGER_LIST, [i * j for i,j in zip(ldata, rdata)])

    __rmul__ = __mul__

    
