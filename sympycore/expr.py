# -*- coding: latin-1 -*-
"""
  This module implements extension type Expr that holds two Python
  objects, head and data, in a pair attribute.

  When adding new features to Expr class, make sure that these are
  added also to extension type Expr in src/expr_ext.c.

C Expr:

>>> from sympycore.expr_ext import *
>>> %timeit Expr(1,2)
10000000 loops, best of 3: 179 ns per loop
>>> e=Expr(1,2)
>>> %timeit h = e.head
10000000 loops, best of 3: 113 ns per loop
>>> %timeit h,d = e.pair
10000000 loops, best of 3: 141 ns per loop

Python Expr:

>>> from sympycore.expr import *
>>> %timeit Expr(1,2)
1000000 loops, best of 3: 988 ns per loop
>>> e=Expr(1,2)
>>> %timeit h = e.head    if head1 not in _add_swap_args_set1 or (head1, head2)==(NUMBER, TERMS):
        head1, head2, data1, data2, self, other = head2, head1, data2, data1, other, self

10000000 loops, best of 3: 119 ns per loop
>>> %timeit h,d = e.pair
10000000 loops, best of 3: 139 ns per loop
"""
# Author: Pearu Peterson
# Created: March 2008

__all__ = ['Expr']

rc_switch = []

class Expr(object):
    """Represents an symbolic expression in a pair form: (head, data)	
                									
The pair (head, data) is saved in an attribute ``pair``. The parts of
a pair, head and data, can be also accessed via ``head`` and ``data``
attributes, respectively. All three attributes are read-only.
  									
The head part is assumed to be an immutable object.  The data part can
be either an immutable object or Python dictionary.  In the former
case, the hash value of Expr instance is defined as::
  									
    hash((<Expr>.head, <Expr>.

Otherwise, if ``data`` contains a Python dictionary, then the hash
value is defined as::
  									
    hash((<Expr>.head, frozenset(<Expr>.data.items())

WARNING: the hash value of an Expr instance is computed (and cached)
when it is used as a key to Python dictionary. This means that the
instance content MUST NOT be changed after the hash is computed.  To
check if it is safe to change the ``data`` dictionary, use
``is_writable`` attribute that returns True when the hash value has
not been computed::
  									
    <Expr>.is_writable -> True or False				
  									
There are two ways to access the parts of a Expr instance from	
Python::								
  									
    a = Expr(<head>, <data>)					
    head, data = a.head, a.data     - for backward compatibility	
    head, data = a.pair             - fastest way			

When Expr constructor is called with one argument, say ``x``, then
``<Expr subclass>.convert(x)`` will be returned.

This is Python version of Expr type.
"""

    __slots__ = ['head', 'data', 'pair', '_hash']

    def __init__(self, head, data=None):
        if data is None:
            obj = self.convert(head)
            self.pair = obj.pair
            self._hash = obj._hash
        else:
            #print (head, data)
            self.pair = (head, data)
            self._hash = None

    def __repr__(self):
        return '%s%r' % (type(self).__name__, self.pair)

    def __hash__(self):
        """ Compute hash value.
        
        Different from expr_ext.Expr, an exception is raised when data
        dictionary values contain dictionaries.
        """
        h = self._hash
        if not h:
            pair = self.pair
            obj = self.as_lowlevel()
            if obj is not pair:
                h = hash(obj)
            else:
                head, data = pair = self.pair
                if type(data) is dict:
                    h = hash((head, frozenset(data.iteritems())))
                else:
                    h = hash(pair)
            self._hash = h
        return h

    @property
    def is_writable(self):
        return not self._hash

    @property
    def head(self):
        return self.pair[0]

    @property
    def data(self):
        return self.pair[1]

    # Pickle support:
    def _sethash(self, hashvalue):
        """ Set hash value for the object.

        If hashvalue==-1, then the hash value will be reset.

        Used by pickle support in sympycore.core._reconstruct. DO NOT
        use this method directly.
        """
        if hashvalue==-1:
            self._hash = None
        else:
            self._hash = hashvalue

    def __reduce__(self):
        # see also _reconstruct function in sympycore/core.py
        version = 3
        from sympycore.core import _reconstruct
        if version==1:
            hashvalue = self._hash
            if hashvalue is None:
                hashvalue = -1
            state = (type(self), self.pair, hashvalue)
        elif version==2 or version==3:
            hashvalue = self._hash
            if hashvalue is None:
                hashvalue = -1
            cls = type(self)
            typ = type(cls)
            try:
                args = typ.__getinitargs__(cls)
            except AttributeError:
                args = None
            if args is None:
                # either metaclass does not define __getinitargs__ method
                # or cls has no metaclass
                state = (cls, self.pair, hashvalue)
            else:
                state = ((typ, args), self.pair, hashvalue)
        else:
            raise NotImplementedError('pickle state version %s' % (version))
        return  _reconstruct, (version, state)


    def as_lowlevel(self):
        """ Return self as low-level object instance that will be
        used in comparison and in hash computation.

        By default. as_lowlevel returns ``data`` part if the ``head``
        part is ``SYMBOL`` or ``NUMBER``. Otherwise it returns
        ``pair`` tuple. Note that returning a copy of the tuple will
        disable using ``frozenset`` hash algorithm for dictionaries.
        """
        head, data = pair = self.pair
        if head is NUMBER or head is SYMBOL:
            return data
        return pair

    def __nonzero__(self):
        return not not self.data

    def __eq__(self, other):
        pair = self.pair
        tother = type(other)
        if tother is not type(self):
            obj = self.as_lowlevel()
            if obj is not pair or type(obj) is tother:
                return obj == other
            return False # because types are different
        return pair==other.pair

    def __ne__(self, other):
        return not (self==other)

    def __lt__(self, other):
        pair = self.pair
        tother = type(other)
        if tother is not type(self):
            obj = self.as_lowlevel()
            if obj is not pair or type(obj) is tother:
                return obj < other
            return NotImplemented # because types are different
        return pair < other.pair

    def __le__(self, other):
        pair = self.pair
        tother = type(other)
        if tother is not type(self):
            obj = self.as_lowlevel()
            if obj is not pair or type(obj) is tother:
                return obj <= other
            return NotImplemented # because types are different
        return pair <= other.pair

    def __gt__(self, other):
        pair = self.pair
        tother = type(other)
        if tother is not type(self):
            obj = self.as_lowlevel()
            if obj is not pair or type(obj) is tother:
                return obj > other
            return NotImplemented # because types are different
        return pair > other.pair

    def __ge__(self, other):
        pair = self.pair
        tother = type(other)
        if tother is not type(self):
            obj = self.as_lowlevel()
            if obj is not pair or type(obj) is tother:
                return obj >= other
            return NotImplemented # because types are different
        return pair >= other.pair

    def _add_item(self, key, value):
        # value must be non-zero
        head, data = self.pair
        assert type(data) is dict and value
        c = data.get(key)
        if c is None:
            data[key] = value
        else:
            c = c + value
            if c:
                data[key] = c
            else:
                del data[key]

    def _sub_item(self, key, value):
        # value must be non-zero
        head, data = self.pair
        assert type(data) is dict and value
        c = data.get(key)
        if c is None:
            data[key] = -value
        else:
            c = c - value
            if c:
                data[key] = c
            else:
                del data[key]

    def _add_dict(self, d):
        head, data = self.pair
        assert type(data) is dict
        for key, value in d.iteritems():
            c = data.get(key)
            if c is None:
                data[key] = value
            else:
                c = c + value
                if c:
                    data[key] = c
                else:
                    del data[key]

    def _sub_dict(self, d):
        head, data = self.pair
        assert type(data) is dict
        for key, value in d.iteritems():
            c = data.get(key)
            if c is None:
                data[key] = -value
            else:
                c = c - value
                if c:
                    data[key] = c
                else:
                    del data[key]

    def _add_dict2(self, d, coeff):
        head, data = self.pair
        assert type(data) is dict,`type(data)`
        assert type(d) is dict,`type(d)`
        for key, value in d.iteritems():
            c = data.get(key)
            if c is None:
                data[key] = value * coeff
            else:
                c = c + value * coeff
                if c:
                    data[key] = c
                else:
                    del data[key]

    def _add_dict3(self, d):
        head, data = self.pair
        assert type(data) is dict
        assert type(d) is dict
        cls = type(self)
        result = None
        for key, value in d.iteritems():
            c = data.get(key)
            if c is None:
                data[key] = value
            else:
                c = c + value
                if type(c) is cls and c.head is NUMBER:
                    c = c.data
                if c:
                    if key.head is NUMBER:
                        result = self.handle_numeric_item(result, key, c)
                    else:
                        data[key] = c
                else:
                    del data[key]
        return result

    def handle_numeric_item(self, result, key, value):
        """ Internal method.

        The method is called from the <Expr instance>._add_dict3(d) method
        when::
        
          <Expr instance>.data[key] = value

        needs to be executed but is left to the call::

          <Expr instance>.handle_numeric_method(result, key, value)

        to handle when key.head is NUMBER and value is non-zero
        low-level number. Note that handle_numeric_method is responsible
        for calling::
        
          del <Expr instance>.data[key]

        if it does not reset ``<Expr instance>.data[key]``.

        The handle_numeric_item() method may change the value of ``result``
        (that is returned by the _add_dict3() method) by returning new
        value. Initially ``result`` is ``None``.
        """
        self.data[key] = value
        return result

    def canonize_FACTORS(self):
        data = self.data
        l = len(data)
        if l==0:
            return self.one
        if l==1:
            t, c = data.items()[0]
            if c==1:
                return t
            if t==self.one:
                return t
        return self

    def canonize_TERMS(self):
        data = self.data
        l = len(data)
        if l==0:
            return self.zero
        if l==1:
            t, c = data.items()[0]
            if c==1:
                return t
            if t==self.one:
                return type(self)(NUMBER, c)
        return self

from .utils import NUMBER, SYMBOL
