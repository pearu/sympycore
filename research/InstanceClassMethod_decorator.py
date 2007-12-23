import new
import types

class InstanceClassMethod(object):
    """ Decorator that allows to use the same name for class
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

class InstanceClassProperty(object):
    """ Decorator similar to InstanceClassMethod but
    applies to property methods and attributes.
    """
    
    def __new__(cls, method, clsname):
        assert isinstance(method, property), type(method)
        obj = object.__new__(cls)
        obj.method = method
        obj.name = method.fget.__name__
        obj.clsname = clsname
        return obj

    def __get__(self, obj, owner):
        name = self.name
        if obj is None:
            return getattr(type(owner), name, self.method)
        else:
            return self.method.__get__(obj, owner)

    def __repr__(self):
        return '%s(%r, %r)' % (self.__class__.__name__,
                               self.method, self.clsname)

special_methods = ('__new__', '__init__')

def apply_InstanceClassMethod_to_Class_methods(cls, d = None, Class=object):
    if d is None:
        d = {}
    if not issubclass(cls, Class):
        return d
    if issubclass(cls, type):
        mro = cls.__mro__
    else:
        for k, v in cls.__dict__.iteritems():
            if k in special_methods:
                continue
            if k in d:
                v1 = d[k]
                if isinstance(v, classmethod):
                    if isinstance(v1, InstanceClassMethod) and v1.clsmethod is None:
                        d[k] = InstanceClassMethod(v1.method, v, v1.clsname + ',' + cls.__name__)
                elif isinstance(v, InstanceClassMethod):
                    if isinstance(v1, classmethod):# and v.clsmethod is None:
                        d[k] = InstanceClassMethod(v.method, v1)#, cls.__name__ + ',' + v.clsname)
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
        if k in special_methods:
            d[k] = v
            continue
        if isinstance(v, types.FunctionType):
            d[k] = InstanceClassMethod(v, clsname = name)
        elif isinstance(v, property):
            d[k] = InstanceClassProperty(v, clsname = name)
        else:
            d[k] = v

    for c in bases:
        apply_InstanceClassMethod_to_Class_methods(c, d, Basic)

    t = type.__new__(basetype, name, bases, d)

    return t

#################################
##### Unittests
#################################

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

    @property
    def prop7(self):
        return 2

    prop8 = 2

class BasicFunctionType(Basic, BasicType):

    __new__ = new_type # applies InstanceClassMethod to Basic methods

    def __str__(self):
        return self.__name__

    def __repr__(self):
        return type.__repr__(self)

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

    @property
    def prop1(self):
        return 3

    prop2 =3

    @property
    def prop3(self):
        return 3

    prop4 = 3

    @property
    def prop5(self):
        return 3

class BasicFunction(Basic):

    __metaclass__ = BasicFunctionType

    def __new__(cls, *args):
        obj = cls.canonize(args)
        if obj is not None:
            return obj
        obj = object.__new__(cls)
        obj.args = args
        obj.func = cls
        return obj

    @classmethod
    def canonize(cls, args):
        return

    def __str__(self):
        return '%s(%s)' % (self.func, ', '.join(map(str, self.args)))

    def __repr__(self):
        return '%s(%s)' % (self.func, ', '.join(map(repr, self.args)))

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

    @property
    def prop1(self):
        return 4

    @property
    def prop2(self):
        return 4

    prop3 = 4

    prop4 = 4

    @property
    def prop6(self):
        return 4

def instancemethod(clsmth):
    def wrap(func):
        return InstanceClassMethod(func, clsmth)
    return wrap

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
            name = '%s(%s)' % (cls.__name__, ', '.join(map(str, args)))
            obj = new_type(type(cls), name, bases = (cls, ),
                         attrdict=dict(args=args,
                                       is_operator = False,
                                       is_function = True))
            return obj
        obj = object.__new__(cls)
        obj.is_function = False
        obj.args = args
        obj.func = cls
        return obj

    @classmethod
    def canonize(cls, args):
        print cls.is_operator, cls.is_function, getattr(cls, 'args', None), args
        return

    @instancemethod(canonize)
    def canonize(self, args):
        print self.is_operator, self.is_function, self.args, args
        return

    def __str__(self):
        return '%s(%s)' % (self.func, ', '.join(map(str, self.args)))

    def __repr__(self):
        return '%s(%s)' % (self.__class__, ', '.join(map(repr, self.args)))

class BasicParametricFunction(BasicFunction):

    is_metafunction = True
    is_function = False

    def __new__(cls, *args):
        obj = cls.canonize(args)
        if obj is not None:
            return obj

        if cls.is_metafunction:
            name = '%s(%s)' % (cls.__name__, ', '.join(map(str, args)))
            obj = new_type(cls.__metaclass__, name, bases = (cls, ),
                           attrdict=dict(args=args,
                                         is_metafunction = False,
                                         is_function = True))
            return obj
        obj = object.__new__(cls)
        obj.is_function = False
        obj.args = args
        obj.func = cls
        return obj

    def __str__(self):
        return self.__name__

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, ', '.join(map(repr, self.args)))

    @classmethod
    def canonize(cls, args):
        print cls.is_function, cls.args, args
        return

    @instancemethod(canonize)
    def canonize(self, args):
        print cls.is_function, cls.args, args
        return

######### User defined classes


class Hermite(BasicParametricFunction):

    @classmethod
    def canonize(cls, args):
        return

class D(BasicOperator):

    pass

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

    @property
    def prop7(self):
        return 5

    @property
    def prop8(self):
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

# prop1 is a property defined in BasicFunctionType and BasicFunction

assert BasicFunction.prop1==3
assert BasicFunction().prop1==4
assert MyFunction.prop1==3
assert MyFunction().prop1==4

# prop2 is defined in BasicFunction as property and in BasicFunctionType as attribute
assert BasicFunction.prop2==3
assert BasicFunction().prop2==4
assert MyFunction.prop2==3
assert MyFunction().prop2==4

# prop3 is defined in BasicFunctionType as property and in BasicFunction as attribute
assert BasicFunction.prop3==3
assert BasicFunction().prop3==4
assert MyFunction.prop3==3
assert MyFunction().prop3==4

# prop4 is defined in BasicFunctionType and in BasicFunction as attribute
assert BasicFunction.prop4==4
assert BasicFunction().prop4==4
assert MyFunction.prop4==4
assert MyFunction().prop4==4

# prop5 is defined in BasicFunctionType as property
assert BasicFunction.prop5==3
assert MyFunction.prop5==3

# prop6 is defined in BasicFunction as property
assert BasicFunction().prop6==4
assert MyFunction().prop6==4
assert isinstance(BasicFunction.prop6, property)==True
assert isinstance(MyFunction.prop6, property)==True

# prop7 is defined in Basic, redefined in MyFunction
assert Basic().prop7==2
assert BasicFunction.prop7==2
assert isinstance(BasicFunctionType.prop7, property)==True
assert BasicFunction().prop7==2
assert MyFunction().prop7==5

# prop8 is defined in Basic as attribute, redefined in MyFunction as property
assert Basic().prop8==2
assert BasicFunction.prop8==2
assert BasicFunction().prop8==2
assert MyFunction().prop8==5
