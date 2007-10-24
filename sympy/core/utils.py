
import sys

all_caches = {}

def get_object_by_name(name, default=None):
    """ Return object that is a value of a variable with name
    in the local or parent namespaces.
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
                obj = frame.f_locals[name] = default
                for frame in frames:
                    frame.f_locals[name] = obj
                return obj
        frames.append(frame)
        frame = frame.f_back
    return default


class Decorator(object):
    pass

class FDiffMethod(Decorator):
    ''' FDiffMethod decorator

    FDiffMethod behaves like a class method but when called
    as instance method, the call is replaced with instance.instance_fdiff
    method call.
    '''

    def __new__(cls, func, clsname=None):
        if isinstance(func, cls):
            return func
        obj = object.__new__(cls)
        obj.func = func
        if clsname is None:
            obj.class_wrapper_name = '%s(%s) class method wrapper' \
                                     % (cls.__name__, func.__name__)
            obj.instance_wrapper_name = '%s(%s) instance method wrapper' \
                                        % (cls.__name__, func.__name__)
        else:
            obj.class_wrapper_name = '%s(%s.%s) class method wrapper' \
                                     % (cls.__name__, clsname, func.__name__)
            obj.instance_wrapper_name = '%s(%s.%s) instance method wrapper' \
                                        % (cls.__name__, clsname, func.__name__)
        return obj
        
    def __get__(self, obj, typ=None):
        if obj is None:
            def class_wrapper(*args, **kw):
                return self.func(typ, *args, **kw)
            class_wrapper.__name__ = self.class_wrapper_name
            return class_wrapper
        else:
            def instance_wrapper(*args, **kw):
                return getattr(obj, 'instance_fdiff')(*args)
            instance_wrapper.__name__ = self.instance_wrapper_name
            return instance_wrapper    

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
        if isinstance(func, cls):
            return func
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
    
    def __new__(cls, func, clsname=None):
        if isinstance(func, cls):
            return func
        obj = object.__new__(cls)
        obj.func = func
        if clsname is None:
            obj.class_wrapper_name = '%s(%s) class method wrapper' \
                                     % (cls.__name__, func.__name__)
            obj.instance_wrapper_name = '%s(%s) instance method wrapper' \
                                        % (cls.__name__, func.__name__)
        else:
            obj.class_wrapper_name = '%s(%s.%s) class method wrapper' \
                                     % (cls.__name__, clsname, func.__name__)
            obj.instance_wrapper_name = '%s(%s.%s) instance method wrapper' \
                                        % (cls.__name__, clsname, func.__name__)
        return obj
        
    def __get__(self, obj, typ=None):
        if obj is None:
            def class_wrapper(*args, **kw):
                return getattr(typ.__class__,
                               self.func.__name__)(typ, *args, **kw)
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
            if self.type_callback is not None:
                return self.type_callback(typ)
            r = getattr(typ.__base__, self.attr_name)
            return r
        else:
            return self.func(obj)

def memoizer_immutable_args(name):
    def make_memoized(func):
        #return func
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

def memoizer_Symbol_new(func):
    func._cache_it_cache = func_cache_it_cache = {}
    def wrapper(cls, name, dummy=False, **options):
        if dummy:
            return func(cls, name, dummy=dummy, **options)
        r = func_cache_it_cache.get(name, None)
        if r is None:
            func_cache_it_cache[name] = r = func(cls, name, dummy=dummy, **options)
        return r
    all_caches['Symbol.__new__'] = func_cache_it_cache
    wrapper.__name__ = 'wrapper.Symbol.__new__'
    return wrapper

def memoizer_Interval_new(func):
    func._cache_it_cache = func_cache_it_cache = {}
    def wrapper(cls, a, b=None, **options):
        if b is None:
            # to ensure that Interval(a) is Interval(a,a)
            args = (a,a)
        else:
            args = (a,b)
        try:
            return func_cache_it_cache[args]
        except KeyError:
            pass
        func_cache_it_cache[args] = r = func(cls, a, b, **options)
        return r
    all_caches['Interval.__new__'] = func_cache_it_cache
    return wrapper

def memoizer_Float_new(func):
    func._cache_it_cache = func_cache_it_cache = {}
    def wrapper(cls, x=0, prec=None, mode=None, **options):
        if prec is None: prec = cls._prec
        if mode is None: mode = cls._mode
        args = (x, prec, mode)
        try:
            return func_cache_it_cache[args]
        except KeyError:
            pass
        func_cache_it_cache[args] = r = func(cls, *args, **options)
        return r
    all_caches['Float.__new__'] = func_cache_it_cache
    return wrapper

def clear_cache():
    """Clear all cached objects."""
    for cache in all_caches.values():
        cache.clear()


def singleton(func):
    """ Decorator for singletons.
    """
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
    #wrapper.__name__ = 'wrapper.%s' % (name)
    return wrapper
