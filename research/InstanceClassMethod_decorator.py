import new
import types

class InstanceClassMethod(object):
    """ Decorator that maps a metaclass method and a classmethod of a base class
    to a classmethod of a given class when the given class defines an instance
    method.

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

    # metaclass method will be used as class method
    @InstanceClassMethod
    def foo(self):
        return self
    
    @classmethod
    def bar(cls):
        return cls

    def fun(self):
        return self

class B(A):

    # classmethod is defined in a parent class
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

    """

    def __new__(cls, method, clsmethod=None, clsname=None):
        # XXX: clsname is functionally unnecessary
        if clsmethod is None:
            clsmethod = getattr(method, '_classmethod', None)
        assert isinstance(method, types.FunctionType),`type(method)`
        assert isinstance(clsmethod, (classmethod, types.NoneType)),`type(clsmethod)`
        obj = object.__new__(cls)
        obj.method = method
        obj.clsmethod = clsmethod
        obj.name = method.__name__
        obj.clsname = clsname
        return obj

    def __get__(self, obj, owner):
        name = self.name
        if obj is None:
            clsmethod = self.clsmethod
            if clsmethod is not None:
                return clsmethod.__get__(obj, owner)
            cn = '_cache_%s_methods' % (owner.__name__)
            cache = owner.__dict__.get(cn)
            if cache is None:
                cache = {}
                setattr(owner, cn, cache)
            t = type(owner)
            method = getattr(t, name, None)
            if method is None:
                # the result will be an unbound method
                method = self.method
            else:
                # the result will be a bound method of classmethod
                obj = owner
                owner = t
        else:
            # the method will be bound method
            cn = '_cache_instance_methods'
            method = self.method
            cache = obj.__dict__.get(cn)
            if cache is None:
                cache = {}
                setattr(obj, cn, cache)
        
        mth = cache.get(name)
        if mth is None:
            cache[name] = mth = new.instancemethod(method, obj, owner)
        return mth

    def __repr__(self):
        return '%s(%r, %r, %r)' % (self.__class__.__name__,
                               self.method, self.clsmethod, self.clsname)

def apply_InstanceClassMethod_to_Class_methods(cls, d = None, Class=object):
    if d is None:
        d = {}
    if not issubclass(cls, Class):
        return d
    if issubclass(cls, type):
        mro = cls.__mro__
    else:
        for k, v in cls.__dict__.iteritems():
            if k in d:
                if isinstance(v, classmethod):
                    v1 = d[k]
                    if isinstance(v1, InstanceClassMethod) and v1.clsmethod is None:
                        d[k] = InstanceClassMethod(v1.method, v, v1.clsname + ',' + cls.__name__)
                elif isinstance(v, InstanceClassMethod):
                    v1 = d[k]
                    if isinstance(v1, classmethod) and v.clsmethod is None:
                        d[k] = InstanceClassMethod(v.method, v1, cls.__name__ + ',' + v.clsname)
                continue
            if isinstance(v, InstanceClassMethod):
                d[k] = v
            elif isinstance(v, types.FunctionType):
                d[k] = InstanceClassMethod(v, clsname = cls.__name__)

        mro = cls.mro()
    for c in mro:
        if c is cls:
            continue
        apply_InstanceClassMethod_to_Class_methods(c, d, Class)
    return d

def new_type(basetype, name, bases=(), attrdict={}):

    d = {}
    for k, v in attrdict.iteritems():
        if isinstance(v, types.FunctionType):
            d[k] = InstanceClassMethod(v, clsname = name)
        else:
            d[k] = v

    for c in bases:
        apply_InstanceClassMethod_to_Class_methods(c, d, Basic)

    t = type.__new__(basetype, name, bases, d)

    return t

class BasicType(type):

    __new__ = type.__new__

    def foo(self):
        # never called because Basic redefines foo
        assert isinstance(self, BasicType)
        return 1

    def fun(self):
        assert isinstance(self, BasicType)
        return 1

    def run(self):
        assert isinstance(self, BasicType)
        return 1

    def gun(self):
        # never called because Basic redefines gun
        assert isinstance(self, BasicType)
        return 1

    def too(self):
        assert isinstance(self, BasicType)
        return 1

class Basic(object):

    __metaclass__ = BasicType # to save Basic classes to `classes`

    def foo(self):
        assert isinstance(self, Basic)
        return 2

    def fun(self):
        assert isinstance(self, Basic)
        return 2

    def run(self):
        assert isinstance(self, Basic)
        return 2

    def gun(self):
        assert isinstance(self, Basic)
        return 2

    def bar(self):
        assert isinstance(self, Basic)
        return 2

class BasicFunctionType(Basic, BasicType):

    __new__ = new_type # applies InstanceClassMethod to Basic methods

    def __eq__(self, other):
        #print 'BasicFunctionType'
        return self is other

    def foo(self):
        assert isinstance(self, Basic)
        assert isinstance(self, BasicType)
        return 3

    def boo(self):
        assert isinstance(self, Basic)
        assert isinstance(self, BasicType)
        return 3

    def run(self):
        assert isinstance(self, Basic)
        assert isinstance(self, BasicType)
        return 3

class BasicFunction(Basic):

    __metaclass__ = BasicFunctionType

    def __eq__(self, other):
        #print 'BasicFunction'
        return self is other

    def foo(self):
        assert isinstance(self, Basic)
        assert not isinstance(self, BasicType)
        return 4

    def fun(self):
        assert isinstance(self, Basic)
        assert not isinstance(self, BasicType)
        return 4

    def sun(self):
        assert isinstance(self, Basic)
        assert not isinstance(self, BasicType)
        return 4

    @classmethod
    def Foo(cls):
        return 4

    def Fun(self):
        return 4

class MyFunction(BasicFunction):

    def fun(self):
        return 5

    def xxx(self):
        return 5

    def Foo(self):
        return 5

    @classmethod
    def _Bar(cls):
        return 5.1

    def Bar(self):
        return 5.2

    Bar._classmethod = _Bar

    @classmethod
    def Fun(cls):
        return 5

# Unittests:

# foo is defined in BasicType, Basic, BasicFunctionType, BasicFunction
assert Basic().foo()==2
assert isinstance(Basic.foo,types.MethodType)
assert BasicFunction.foo()==3
assert BasicFunction().foo()==4
assert BasicFunctionType('a').foo()==3
assert BasicFunctionType('a',bases=(BasicFunction,))().foo()==4

# fun is defined in BasicType, Basic, BasicFunction
assert Basic().fun()==2
assert isinstance(Basic.fun,types.MethodType)
assert BasicFunction.fun()==2
assert BasicFunction().fun()==4
assert BasicFunctionType('a').fun()==2
assert BasicFunctionType('a',bases=(BasicFunction,))().fun()==4

assert MyFunction.fun()==2
assert MyFunction().fun()==5

# run is defined in BasicType, Basic, BasicFunctionType
assert Basic().run()==2
assert isinstance(Basic.run,types.MethodType)
assert BasicFunction.run()==3
assert BasicFunction().run()==2
assert BasicFunctionType('a').run()==3
assert BasicFunctionType('a',bases=(BasicFunction,))().run()==2

# gun is defined in BasicType, Basic
assert Basic().gun()==2
assert isinstance(Basic.gun,types.MethodType)
assert BasicFunction.gun()==2
assert BasicFunction().gun()==2
assert BasicFunctionType('a').gun()==2
assert BasicFunctionType('a',bases=(BasicFunction,))().gun()==2

# bar is defined in Basic
assert Basic().bar()==2
assert isinstance(Basic.bar,types.MethodType)
assert BasicFunction().bar()==2
assert BasicFunction.bar()==2
assert BasicFunctionType('a').bar()==2
assert BasicFunctionType('a',bases=(BasicFunction,))().bar()==2

# too is defined in BasicType
assert hasattr(Basic(),'too')==False
assert Basic.too()==1
assert BasicFunction.too()==1
assert hasattr(BasicFunction(),'too')==False
assert BasicFunctionType('a').too()==1

# boo is defined in BasicFunctionType
assert BasicFunction.boo()==3
assert hasattr(BasicFunction(),'boo')==False
assert BasicFunctionType('a').boo()==3

# sun is defined in BasicFunction
assert isinstance(BasicFunction.sun, types.UnboundMethodType)==True
assert BasicFunction().sun()==4
assert BasicFunctionType('a',bases=(BasicFunction,))().sun()==4

# Foo is defined in BasicFunction as classmethod, in MyFunction as method
assert BasicFunction.Foo()==4
assert BasicFunction().Foo()==4
assert MyFunction().Foo()==5
assert MyFunction.Foo()==4

# Bar is defined in MyFunction as method with an attribute _classmethod
# holding classmethod version of Bar
assert MyFunction().Bar()==5.2
assert MyFunction.Bar()==5.1

# Fun is defined in MyFunction as classmethod but in BasicFunction as instance method
assert MyFunction.Fun()==5
assert MyFunction().Fun()==4
