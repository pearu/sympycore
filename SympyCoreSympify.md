**This page is obsolete**

## The `sympify(..)` function ##

The `sympy.core.sympify` module implements a function `sympify`
that can be used to create symbolic expressions from Python
objects like strings, numbers, etc. This function can also
be used to map the arguments of functions to ensure that
arguments are symbolic objects.

The signature of the `sympify` function is the following:
```
sympify(obj, sympify_lists=False, globals=None, locals=None)
```
and it returns either a `Basic` instance or Python `bool` iff the
first argument is a boolean value. If `obj` is  already a `Basic`
instance then it is returned immidiately.

If `sympify_lists` is `True` then `obj` can be a sequence (tuple or list)
of objects to be sympified.

If `obj` is a Python string then
arguments `globals` and `locals` are used to retrive existing
symbolic symbols from these dictionaries that are used in the
string `obj`. By default, `globals` is a dictionary of `sympy`
symbols and `locals` is `{}`.

When using `sympify(strobj,locals=locals())` then all undefined
symbols will be created to the callers namespace:
```
>>> sympify('x+y')
y + x
>>> x
...
<type 'exceptions.NameError'>: name 'x' is not defined
>>> sympify('x+y',locals=locals())
y + x
>>> x
x
>>> sympify('x',locals=locals()) is x
True
>>> sympify('x') is x
False
```