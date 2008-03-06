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
>>> %timeit h = e.head
10000000 loops, best of 3: 119 ns per loop
>>> %timeit h,d = e.pair
10000000 loops, best of 3: 139 ns per loop
"""
# Author: Pearu Peterson
# Created: March 2008

__all__ = ['Expr']

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
            if obj is not pair and obj is not NotImplemented:
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
        version = 1
        from sympycore.core import _reconstruct
        if version==1:
            hashvalue = self._hash
            if hashvalue is None:
                hashvalue = -1
            state = (type(self), self.pair, hashvalue)
        else:
            raise NotImplementedError('pickle state version %s' % (version))
        return  _reconstruct, (version, state)

    #XXX: remove when rich-comparison is fully implemented
    def __cmp__(self, other):
        if type(other) is not type(self):
            return NotImplemented
        ah, ad = self.pair
        bh, bd = other.pair
        if ah is bh:
            if ad is bd:
                return 0
            return cmp(ad, bd)
        c = cmp(ah, bh)
        if c:
            return c
        elif ad is bd:
            return 0
        return cmp(ad, bd)

    def as_lowlevel(self):
        """ Return self as low-level object instance or NotImplemented.

        In case of success, the low-level object instance is used
        in comparisons as well as in hash computation.
        """
        head, data = pair = self.pair
        if head is NUMBER or head is SYMBOL:
            return data
        return pair

    def __nonzero__(self):
        return not not self.data

    def __eq__(self, other):
        if type(other) is not type(self):
            obj = self.as_lowlevel()
            if obj is NotImplemented:
                return False
            return obj == other
        return self.pair==other.pair

    def __ne__(self, other):
        return not (self==other)

    #XXX: it is not really necessary that Expr will implement the following
    #XXX: similarly implement __gt__, __le__, __ge__
    def __lt2__(self, other):
        if type(other) is not type(self):
            obj = self.as_lowlevel()
            if obj is NotImplemented:
                return NotImplemented
                #return type(self) < type(other)
            return obj < other
        ah, ad = self.pair
        bh, bd = other.pair
        if ah is bh:
            if ad is bd:
                return False
            return ad < bd
        elif ah == bh:
            if ad is bd:
                return False
            return ad < bd
        return ah < bh

from .utils import NUMBER, SYMBOL
