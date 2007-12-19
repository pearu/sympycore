
import os
import sys

__all__ = ['UniversalMethod','DualMethod','DualProperty',
           'singleton','memoizer_immutable_args','clear_cache',
           'get_object_by_name', 'get_class_statement'
           ]

all_caches = {}

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

class UniversalMethod(Decorator):
    ''' universalmethod decorator

class AType(type):
    pass

class A(object):    
    __metaclass__ = AType
    @UniversalMethod
    def foo(self_or_cls):
        return 'A.foo(%r)' % (self_or_cls)

A.foo() -> "A.foo(<class \'__main__.A\'>)"
A().foo() -> "A.foo(<__main__.A object at 0xfdb3d0>)"
    '''


    def __new__(cls, func):
        obj = object.__new__(cls)        
        obj.func = func
        obj.method_name = func.__name__
        obj.class_wrapper_name = '%s(%s) class method wrapper' \
                                 % (cls.__name__, func.__name__)
        obj.instance_wrapper_name = '%s(%s) instance method wrapper' \
                                        % (cls.__name__, func.__name__)
        return obj
        
    def __get__(self, obj, typ=None):
        if obj is None:
            def class_wrapper(*args, **kw):
                return self.func(typ, *args, **kw)
            class_wrapper.__name__ = self.class_wrapper_name
            class_wrapper._universalmethod = self
            return class_wrapper
        else:
            def instance_wrapper(*args, **kw):
                return self.func(obj, *args, **kw)
            instance_wrapper.__name__ = self.instance_wrapper_name
            instance_wrapper._universalmethod = self
            return instance_wrapper    


class DualMethod(Decorator):
    """dualmethod decorator.
    
    Enable calling a method as a class method or as an instance method
    provided that both metaclass and class define methods with the
    same name.

    Consider the following example:

    class AType(type):
        def foo(cls):
            print 'In AType.foo()'

    class A(object):
        __metaclass__ = AType
        def foo(self):
            print 'In A.foo()'

    The objective is to be able to call foo method both as
    `A.foo()` and `A().foo()`. Using the example above,
    a TypeError is raised when calling `A.foo()`:

    >>> A().foo()
    In A.foo()
    >>> A.foo()
    ...
    <type 'exceptions.TypeError'>: unbound method foo() must be called with A instance as first argument (got nothing instead)

    This issue can be overcome by adding DualMethod decorator to
    A.foo method definition:

    class A(object):
        __metaclass__ = AType
        @DualMethod
        def foo(self):
            print 'In A.foo()'

    And now the example works as expected:

    >>> A().foo()
    In A.foo()
    >>> A.foo()
    In AType.foo()

    """
    # got the idea from http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/523033
    
    def __new__(cls, func, clsname=None, funcname=None):
        if isinstance(func, cls):
            return func
        obj = object.__new__(cls)
        obj.func = func
        if funcname is None:
            funcname = func.__name__
        obj.funcname = funcname
        if clsname is None:
            obj.class_wrapper_name = '%s(%s) class method wrapper' \
                                     % (cls.__name__, funcname)
            obj.instance_wrapper_name = '%s(%s) instance method wrapper' \
                                        % (cls.__name__, funcname)
        else:
            obj.class_wrapper_name = '%s(%s.%s) class method wrapper' \
                                     % (cls.__name__, clsname, funcname)
            obj.instance_wrapper_name = '%s(%s.%s) instance method wrapper' \
                                        % (cls.__name__, clsname, funcname)
        return obj
        
    def __get__(self, obj, typ=None):
        if obj is None:
            funcname = self.funcname
            def class_wrapper(*args, **kw):
                if hasattr(self.func, 'im_self') and self.func.im_self is not None:
                    return self.func(*args, **kw)
                mth = getattr(typ.__class__, self.funcname)
                return mth(typ, *args, **kw)
            class_wrapper.__name__ = self.class_wrapper_name
            return class_wrapper
        else:
            def instance_wrapper(*args, **kw):
                return self.func(obj, *args, **kw)
            instance_wrapper.__name__ = self.instance_wrapper_name
            return instance_wrapper

class DualProperty(Decorator):
    """ dualproperty decorator.

class AType(type):
    @property
    def foo(cls):
        return 'AType.foo'
    # or foo = 'AType.foo'

class A(object):
    __metaclass__ = AType
    @DualProperty
    def foo(self):
        return 'A.foo'

A.foo -> 'AType.foo'
A().foo -> 'A.foo'

See also DualMethod.
    """
    def __new__(cls, func, type_callback=None):
        obj = object.__new__(cls)
        obj.func = func
        obj.attr_name = func.__name__
        obj.type_callback = type_callback
        return obj
        
    def __get__(self, obj, typ=None):
        if obj is None:
            # called when metaclass or type object does not have the property
            # but attribute.
            if self.type_callback is not None:
                return self.type_callback(typ)
            return getattr(typ.__class__, self.attr_name)
        else:
            return self.func(obj)

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
