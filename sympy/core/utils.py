
import os
import sys
import new
import types

__all__ = ['instancemethod', 'InstanceClassMethod',
           'singleton','memoizer_immutable_args','clear_cache',
           'get_object_by_name', 'get_class_statement',
           'get_class_attributes',
           'get_class_methods',
           'get_class_properties',
           ]

all_caches = {}

def get_class_attributes(cls):
    d = {}
    if issubclass(cls, type):
        mro = cls.__mro__
    else:
        mro = cls.mro()
    for c in mro:
        if c.__module__ == '__builtin__':
            continue
        for k,v in c.__dict__.items():
            if k in d:
                continue
            d[k] = v
    return d

def get_class_methods(cls):
    d = {}
    if issubclass(cls, type):
        mro = cls.__mro__
    else:
        mro = cls.mro()
    for c in mro:
        if c.__module__ == '__builtin__':
            continue
        for k,v in c.__dict__.items():
            if k in d:
                continue
            if isinstance(v, types.FunctionType):
                d[k] = v
    return d

def get_class_properties(cls):
    d = {}
    if issubclass(cls, type):
        mro = cls.__mro__
    else:
        mro = cls.mro()
    for c in mro:
        if c.__module__ == '__builtin__':
            continue
        for k,v in c.__dict__.items():
            if k in d:
                continue
            if isinstance(v, property):
                d[k] = v
    return d

def get_object_by_name(name, default=None):
    """ Return object that is a value of a variable with name
    in the local or parent namespaces. If variable is found
    in parent namespaces then it is added to children
    namespaces.
    When no variable with name is found then return default
    and add a variable only to the callers locals namespace. 
    """
    frame = sys._getframe(1)
    frames = [frame]
    while frame is not None:
        obj = frame.f_locals.get(name, None)
        if obj is not None:
            for frame in frames:
                frame.f_locals[name] = obj
            return obj
        if default is not None:
            try:
                _name = frame.f_locals['__name__']
            except KeyError:
                _name = None
            if _name is not None and _name=='__main__':
                obj = frames[0].f_locals[name] = default
                return obj
        frames.append(frame)
        frame = frame.f_back
    return default

def get_class_statement(frame = None):
    """ Return a Python class definition line or None at frame lineno.
    This function must be called inside a __new__ method.
    """
    if frame is None:
        frame = sys._getframe(2)
    d = frame.f_locals
    if d.has_key('__file__'):
        fn = d['__file__']
    else:
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
            return get_class_statement(frame.f_back)
    else:
        print >> sys.stderr,'Warning: cannot locate file:',fn #pragma NO COVER


class Decorator(object):
    pass

def instancemethod(clsmth):
    """ Apply InstanceClassMethod decorator to instance method.
    instancemethod takes an argument that must be a classmethod.

    Usage examples:

      class MyFunc(BasicFunction):

          # MyFunc defines foo both as class and instance method
          @classmethod
          def foo(cls):
              ...

          @instancemethod(foo)
          def foo(self):
              ...

          # MyFunc redefines instance method bar that is initially defined in BasicFunction:
          @instancemethod(BasicFunction.bar)
          def bar(self):
              ...

          # MyFunc redefines class method fun that is initially defined in BasicFunction:
          @classmethod
          def fun(self):
              ...
          fun = instancemethod(fun)(BasicFunction.fun)

    As a result, MyFunc.foo() will call the method `foo` defined first
    and MyFunc().foo() will call the method `foo` defined second.
    """
    if isinstance(clsmth, types.FunctionType):
        clsmth = classmethod(clsmth)
    elif isinstance(clsmth, types.MethodType):
        return instancemethod(clsmth.im_func)
    assert isinstance(clsmth, classmethod),`type(clsmth)`
    def wrap(func):
        if isinstance(func, types.MethodType):
            return wrap(func.im_func)
        elif isinstance(func, InstanceClassMethod):
            return wrap(func.method)
        elif isinstance(func, type):
            n = clsmth.__get__(None, func).im_func.__name__
            for cls in func.mro():
                if n in cls.__dict__:
                    func = cls.__dict__[n]
                    return wrap(func)
        assert isinstance(func, types.FunctionType),`type(func)`
        return InstanceClassMethod(func, clsmth)
    return wrap


# method names that will ignored in applying InstanceClassMethod decorator:
special_methods = ('__new__', '__init__', '__hash__')


class InstanceClassMethod(object):
    """ Decorator that allows to use the same method name for class
    and instance methods.
    
    When calling a method via class object then metaclass method
    or the classmethod of a base class with the same name will be used.

    Example
    -------

      The example below demonstrates four different ways of providing
      a method as a classmethod when called using class object or
      as an instance method when called using class instance:
      
      * foo  - metaclass method will be used as a classmethod
      * bar  - classmethod is defined in a parent class, instance method
               in a given class
      * car  - classmethod is defined in the same class with instance method
      * fun  - classmethod is defined in a given class and instance
               method in a parent class

class AType(type):
    def foo(cls):
        return cls

class A(object):
    __metaclass__ = AType

    # metaclass method will be used as class method:
    @InstanceClassMethod
    def foo(self):
        return self
    
    @classmethod
    def bar(cls):
        return cls

    def fun(self):
        return self

class B(A):

    # classmethod is defined in a parent class:
    def bar(self):
        return self
    bar = InstanceClassMethod(bar, A.__dict__['bar'])

    # classmethod and instance methods are defined in the same class:
    @classmethod
    def _car(cls):
        return cls
    
    def car(self):
        return self

    # option 1:
    car = InstanceClassMethod(car, _car)
    # option 2:
    car._classmethod = _car
    car = InstanceClassMethod(car)

    # instance method is defined in a parent class:
    @classmethod
    def fun(cls):
        return cls
    fun = InstanceClassMethod(A.__dict__['fun'], fun)

>>> A.foo()
<class '__main__.A'>
>>> A().foo()
<__main__.A object at 0xdc3a50>
>>> B.foo()
<class '__main__.B'>
>>> B().foo()
<__main__.B object at 0xede310>

    See also:
      InstanceClassProperty decorator
    """

    def __new__(cls, method, clsmethod):
        assert isinstance(method, types.FunctionType),`type(method)`
        assert isinstance(clsmethod, classmethod),`type(clsmethod)`
        obj = object.__new__(cls)
        obj.method = method
        obj.clsmethod = clsmethod
        obj.name = method.__name__
        return obj

    def __get__(self, obj, owner):
        if obj is None:
            return self.clsmethod.__get__(obj, owner)
        return new.instancemethod(self.method, obj, owner)

    def __repr__(self):
        return '%s(%r, %r)' % (self.__class__.__name__,
                               self.method, self.clsmethod)


def memoizer_immutable_args(name):
    def make_memoized(func):
        func._cache_it_cache = func_cache_it_cache = {}
        def wrapper(*args):
            try:
                r = func_cache_it_cache.get(args, None)
            except TypeError, msg:
                if 'dict objects are unhashable'==str(msg):
                    return func(*args)
                raise
            if r is None:
                func_cache_it_cache[args] = r = func(*args)
            return r
        all_caches[name] = func_cache_it_cache
        wrapper.__name__ = 'wrapper.%s' % (name)
        return wrapper
    return make_memoized

def memoizer_Fraction(func):
    func._memoizer_cache = cache = {}
    def wrapper_Fraction(cls, *args):
        r = cache.get(args, None)
        if r is None:
            cache[args] = r = func(cls,*args)
        return r
    return wrapper_Fraction

def memoizer_Integer(func):
    func._memoizer_cache = cache = {}
    def wrapper_Integer(cls, p):
        if not(-1000<p<1000):
            return func(cls,p)
        r = cache.get(p, None)
        if r is None:
            cache[p] = r = func(cls,p)
        return r
    return wrapper_Integer

def clear_cache():
    """Clear all cached objects."""
    for cache in all_caches.values():
        cache.clear()


def singleton(func):
    """ Decorator for singletons.
    """
    func._cache_it_cache = func_cache_it_cache = {}
    def wrapper(arg):
        r = func_cache_it_cache.get(arg, None)
        if r is None:
            func_cache_it_cache[arg] = r = func(arg)
        return r
    return wrapper
