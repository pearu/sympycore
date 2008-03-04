# -*- coding: latin-1 -*-
"""This module implements a pure python Pair class.

In python code, usage of the following idioms are recommended:

  head, data = <Pair instance>[:]

Some benchmarks follow below.

1) Pair is a pure Python new-style class:

>>> %timeit Pair(1,2)
1000000 loops, best of 3: 818 ns per loop

>>> a=Pair(1,2)
>>> %timeit head, data = a.head, a.data
1000000 loops, best of 3: 213 ns per loop
>>> %timeit head, data = a[:]
1000000 loops, best of 3: 704 ns per loop
>>> %timeit head, data = a
100000 loops, best of 3: 2.3 µs per loop
>>> %timeit head, data = a[0], a[1]
1000000 loops, best of 3: 1.03 µs per loop

2) Pair is object type implemented in extension module:

>>> %timeit Pair(1,2)
1000000 loops, best of 3: 191 ns per loop

>>> a=Pair(1,2)
>>> %timeit head, data = a.head, a.data
1000000 loops, best of 3: 187 ns per loop
>>> %timeit head, data = a[:]
10000000 loops, best of 3: 132 ns per loop
>>> %timeit head, data = a
1000000 loops, best of 3: 716 ns per loop
>>> %timeit head, data = a[0], a[1]
10000000 loops, best of 3: 173 ns per loop

3) Pair is derived from tuple (cannot use this approach as it breaks
numpy array support):

>>> a=Pair(1,2)
>>> %timeit Pair(1,2)
1000000 loops, best of 3: 1.18 µs per loop

>>> a=Pair(1,2)
>>> %timeit head, data = a.head, a.data
1000000 loops, best of 3: 346 ns per loop
>>> %timeit head, data = a[0], a[1]
10000000 loops, best of 3: 174 ns per loop
>>> %timeit head, data = a[:]
10000000 loops, best of 3: 135 ns per loop
>>> %timeit head, data = a
10000000 loops, best of 3: 159 ns per loop

"""
#  Author: Pearu Peterson
#  Created: March 2008

class Pair(object):
    """ Holds a pair of Python objects: head and data.

    This is pure Python version of the Pair type. For C version, see
    the extension module pair_ext. For a detailed documentation, see
    the header of src/pair_ext.c file.

    When adding new features to Pair class, make sure that these are
    added to the extension type Pair in src/pair_ext.c as well.
    """

    __slots__ = ['head', 'data', '_hash']

    #XXX: replace __new__ with __init__
    def __new__(cls, head, data, new = object.__new__):
        obj = new(cls)
        obj.head = head
        obj.data = data
        obj.pair = (head, data)
        obj._hash = None
        return obj

    def __repr__(self):
        return '%s(%r, %r)' % (type(self).__name__, self.head, self.data)

    def __getslice__(self, start, end):
        return (self.head, self.data)[start:end]

    def __getitem__(self, index):
        if index is 0: return self.head
        if index is 1: return self.data
        raise IndexError

    def __hash__(self):
        """ Compute hash value.
        
        Different from pair_ext.Pair, an exception is raised when data
        dictionary values contain dictionaries.
        """
        h = self._hash
        if not h:
            data = self.data
            if type(data) is dict:
                h = hash((self.head, frozenset(data.iteritems())))
            else:
                h = hash((self.head, data))
            self._hash = h
        return h

    @property
    def is_writable(self):
        return not self._hash
