**This page is obsolete**

# Decorators #

The `sympy.core.utils` module defines decorators for
caching the results of functions/methods as well as
for dealing with the issues of calling `BasicFunction` methods
both as class methods and as instance methods.

## `singleton` decorator ##

If a class should have one and only one instance then
apply the `singleton` declarator for the `__new__` method
of the corresponding class.
```
>>> class A(Basic):
...     @singleton
...     def __new__(cls):
...         return Basic.__new__(cls)
...     
>>> A() is A()
True
```

## `memoizer_immutable_args` decorator ##

To memorize the results of methods/functions that take
only immutable arguments, apply the `memoizer_immutable_args('<function/method name>')`
decorator to the corresponding function/method.

## `UniversalMethod` decorator ##

To define a method that can be used as an instance and class method
at the same time, apply `UniversalMethod` to the corresponding method.
The method itself should take care of processing correctly the first argument,
that can be either a class object or an instance of this class.
```
>>> class A:                                    
    @UniversalMethod
    def foo(obj):
        if isinstance(obj, type(A)):
            return 'obj is class'
        return 'obj is class instance'
...     
...     
>>> A.foo()
'obj is class'
>>> A().foo()
'obj is class instance'
```

## `DualMethod` decorator ##

If the metaclass of a class defines a method for a class with the same
name as the class for an instance method, then apply `DualMethod` decorator
to class method so that the metaclass method can be used as a class method
(otherwise one gets a TypeError on calling unbound method).
```
>>> class AType(type):
...     def foo(cls):
...         return 'metaclass method foo'
...     
...     
>>> class A:
...     __metaclass__ = AType
...     @DualMethod
...     def foo(self):
...         return 'instance method foo'
...     
...     
>>> A.foo()
'metaclass method foo'
>>> A().foo()
'instance method foo'
```

## `DualProperty` method ##

If the metaclass of a class defines a property method for a class with
the same name as the class for an instance property method, then apply
`DualProperty` decorator to class property method.
```
>>> class AType(type):
...     @property
...     def foo(cls):
...         return 'metaclass property foo'
...     
...     
>>> class A:
...     __metaclass__ = AType
...     @DualProperty
...     def foo(self):
...         return 'instance property foo'
...     
...     
>>> A.foo
'metaclass property foo'
>>> A().foo
'instance property foo'
```