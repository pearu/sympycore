#
# Author: Pearu Peterson
# Created: February 2008
#
""" Provides Matrix support.
"""
from __future__ import division

__docformat__ = "restructuredtext"
__all__ = ['Matrix', 'MatrixBase', 'MatrixDict']

import random

from ..core import classes
from ..utils import SYMBOL, NUMBER, ADD, MUL, POW, MATRIX, MATRIX_DICT
from ..basealgebra import Algebra
from ..basealgebra.verbatim import Verbatim
from ..arithmetic.numbers import div, mpq

def is_sequence(obj):
    t = type(obj)
    if t is list or t is tuple:
        return True
    elif t is mpq:
        return False
    try:
        len(obj)
        return True
    except TypeError:
        return False

def Matrix(*args, **kws):
    """ Construct a matrix instance.

    The following signatures are supported:

      Matrix(n)           - n x n matrix of zeros
      Matrix(n, random=True) - n x n matrix of random values belonging to [-10,10]
      Matrix(n, random=[l, u]) - n x n matrix of random values belonging to [l,u]
      Matrix(m, n)        - m x n matrix of zeros
      Matrix(n, m, random=True) - m x n matrix of random values belonging to [-10,10]
      Matrix(n, m, random=[l, u]) - m x n matrix of random values belonging to [l,u]
      Matrix(seq)         - n x 1 column matrix where n = len(seq)
      Matrix(seq, diagonal=True)    - n x n diagonal matrix where n = len(seq)
      Matrix(seq, permutation=True) - n x n permutation matrix where n = len(seq)
      Matrix(array)       - m x n matrix where m=len(array), n=max(len(array[:]))
      Matrix(m, n, dict)  - m x n matrix with nonzero elements defined by dict,
                            dict keys must be 2-tuples of integers.
      Matrix(m, n, seq)   - m x n matrix with elements in seq row-wise.
    """
    if len(args)==1:
        a = args[0]
        if isinstance(a, MatrixBase):
            return a
        elif isinstance(a, int):
            m, n = a, a
            data = {}
            interval = kws.get('random')
            if interval is not None:
                if interval==True:
                    interval = (-10, 10)
                for i in range(m):
                    for j in range(n):
                        num = random.randint(*interval)
                        if num:
                            data[i,j] = num                
        elif is_sequence(a):
            m = len(a)
            data = {}
            if True in map(is_sequence, a):
                n = 0
                for i,row in enumerate(a):
                    if is_sequence(row):
                        l = len(row)
                        n = max(n, l)
                        for j, x in enumerate(row):
                            if x:
                                data[i,j] = x
                    else:
                        n = max(n, 1)
                        if row:
                            data[i,0] = row
            else:
                n = m
                if kws.get('diagonal'):
                    for i, x in enumerate(a):
                        if x:
                            data[i, i] = x
                elif kws.get('permutation'):
                    for i,x in enumerate(a):
                        assert 0<=x<m,`x,m`
                        data[i, x] = 1
                else: # single column matrix
                    n = 1
                    for i,x in enumerate(a):
                        if x:
                            data[i, 0] = x
        else:
            raise TypeError('Matrix call with 1 argument: argument must be integer or a sequence, got %r' % (type(a)))
    elif len(args)==2:
        m, n = args
        data = {}
        if not (isinstance(m, int) and isinstance(n, int)):
            raise TypeError('Matrix call with 2 arguments: arguments must be integers, got %r, %r' % (type(m), type(n)))
        interval = kws.get('random')
        if interval is not None:
            if interval==True:
                interval = (-10, 10)
            for i in range(m):
                for j in range(n):
                    num = random.randint(*interval)
                    if num:
                        data[i,j] = num                
    elif len(args)==3:
        m, n, data = args
        flag = True
        if isinstance(data, dict):
            pass
        elif is_sequence(data):
            k = 0
            d = {}
            for i in range(m):
                for j in xrange(n):
                    x = data[k]
                    if x:
                        d[i,j] = x
                    k += 1
            data = d
        else:
            flag = False
        if not (isinstance(m, int) and isinstance(n, int) and flag):
            raise TypeError('Matrix call with 3 arguments: arguments must be integers and a dictionary|sequence, got %r, %r, %r'\
                            % (type(m), type(n), type(data)))
        
        
    else:
        raise TypeError('Matrix takes 1, 2, or 3 arguments, got %r' % (len(args)))

    return MatrixDict(MATRIX(m, n, MATRIX_DICT), data)


class MatrixBase(Algebra):
    """ Base class to matrix classes.

    Currently the following matrix classes are implemented:

      MatrixDict - matrix content is saved in a dictonary
    """

    @classmethod
    def convert(cls, data, typeerror=True):
        if isinstance(data, list):
            return Matrix(data)
        return super(CommutativeRing, cls).convert(data, typeerror=typeerror)

    @classmethod
    def random(cls, n, m, interval=(-10,10)):
        return Matrix(n, m, random=interval)

    def __str__(self):
        rows, cols = self.rows, self.cols
        columns = []
        for j in xrange(cols):
            col = []
            for i in xrange(rows):
                s = str(self[i,j])
                col.append(s)
            width = max(map(len,col))
            fmt = ' %'+str(width)+'s '
            col = [fmt % (s) for s in col]
            columns.append(col)
        return '\n'.join([''.join(row).rstrip() for row in zip(*columns)])

    def __iadd__(self, other):
        raise NotImplementedError('%s must implement __iadd__' % (type(self)))

    def __imul__(self, other):
        raise NotImplementedError('%s must implement __imul__' % (type(self)))

    def __pos__(self):
        return self

    def __add__(self, other):
        ret = self.copy()
        ret += other
        return ret

    def __radd__(self, other):
        t = type(other)
        if t is list or t is tuple:
            return Matrix(other) + self
        # other is scalar
        ret = self.copy()
        ret += other
        return ret

    def __isub__(self, other):
        self += -other
        return self

    def __sub__(self, other):
        ret = self.copy()
        ret -= other
        return ret

    def __rsub__(self, other):
        return other + (-self)

    def __mul__(self, other):
        ret = self.copy()
        ret *= other
        return ret

    def __rmul__(self, other):
        t = type(other)
        if t is list or t is tuple:
            return Matrix(other) * self
        # other is scalar
        ret = self.copy()
        ret *= other
        return ret

    def __idiv__(self, other):
        self *= div(1, other)
        return self

    def __div__(self, other):
        iother = div(1, other)
        return self * iother


class MatrixDict(MatrixBase):
    """ Implementation of matrix where elements are stored in a dictionary.
    """

    rows = property(lambda self: self.head.rows)
    cols = property(lambda self: self.head.cols)
    shape = property(lambda self: self.head.shape)
    is_square = property(lambda self: self.head.rows==self.head.cols)

    @property
    def is_lower(self):
        head, data = self.pair
        if head.is_transpose:
            return all(i<=j for i, j in data)
        return all(i>=j for i, j in data)

    @property
    def is_upper(self):
        head, data = self.pair
        if head.is_transpose:
            return all(i>=j for i, j in data)
        return all(i<=j for i, j in data)

    @property
    def is_orthogonal(self):
        if not self.is_square:
            return False
        return (self*self.T).is_identity

    @property
    def is_identity(self):
        head, data = self.pair
        m, n = head.shape
        if m!=n or len(data)!=n:
            return False
        return all(i==j and x==1 for (i,j),x in data.iteritems())

    @property
    def T(self):
        """ Return transposed view of a matrix.
        """
        head, data = self.pair
        return type(self)(head.T, data)

    @property
    def A(self):
        """ Return array view of a matrix.
        """
        head, data = self.pair
        if head.is_array:
            return self
        newhead = head.A
        if newhead is head:
            return self
        return type(self)(newhead, data)

    @property
    def M(self):
        """ Return matrix view of a matrix.
        """
        head, data = self.pair
        if not head.is_array:
            return self
        newhead = head.M
        if newhead is head:
            return self
        return type(self)(newhead, data)

    @property
    def I(self):
        """ Return inverse matrix.
        """
        return self.inv()

    def resize(self, m, n):
        """ Return resized view of a matrix.

        Notes:

         - Use crop() to remove elements out-of-matrix bounds.
         - If matrix is not writable then matrix data is copied.
        """
        head, data = self.pair
        p, q = head.shape
        if p==m and q==n:
            return self
        newhead = MATRIX(m, n, head.storage)
        if not self.is_writable:
            data = dict(data)
        return type(self)(newhead, data)

    def tolist(self):
        """Convert matrix to a list of lists."""
        rows, cols = self.head.shape
        return [[self[i,j] for j in xrange(cols)] for i in xrange(rows)]

    def __getitem__(self, key):
        tkey = type(key)
        head, data = self.pair
        if tkey is tuple:
            i, j = key
            ti, tj = type(i), type(j)
            if ti is int and tj is int:
                if head.is_transpose:
                    key = j, i
                return data.get(key, 0)
            if ti is slice and tj is int:
                row_indices = dict([(i0,k) for k,i0 in enumerate(xrange(*i.indices(head.rows)))])
                col_indices = {j:0}
            elif ti is int and tj is slice:
                row_indices = {i:0}
                col_indices = dict([(j0,k) for k,j0 in enumerate(xrange(*j.indices(head.cols)))])
            elif ti is slice and tj is slice:
                row_indices = dict([(i0,k) for k,i0 in enumerate(xrange(*i.indices(head.rows)))])
                col_indices = dict([(j0,k) for k,j0 in enumerate(xrange(*j.indices(head.cols)))])
            else:
                raise NotImplementedError(`key`)
            newdata = {}
            if head.is_transpose:
                for (j,i), x in data.items():
                    ki = row_indices.get(i)
                    if ki is not None:
                        kj = col_indices.get(j)
                        if kj is not None:
                            newdata[ki, kj] = x
            else:
                for (i,j), x in data.items():
                    ki = row_indices.get(i)
                    if ki is not None:
                        kj = col_indices.get(j)
                        if kj is not None:
                            newdata[ki, kj] = x
            return Matrix(len(row_indices), len(col_indices), newdata)
        elif tkey is int or tkey is slice:
            return self[key, :]
        raise NotImplementedError(`key`)

    def __setitem__(self, key, value):
        if not self.is_writable:
            raise TypeError('Matrix content is read-only')
        if isinstance(value, list):
            self[key] = Matrix(value)
            return
        head, data = self.pair
        tkey = type(key)
        if tkey is int or tkey is slice:
            self[key, :] = value
            return
        i, j = key
        ti, tj = type(i), type(j)
        if ti is int and tj is int:
            if head.is_transpose:
                key = j,i
            if value:
                data[key] = value
            else:
                try:
                    del data[key]
                except KeyError:
                    pass
            return
        if ti is slice and tj is int:
            row_indices = [(i0,k) for k,i0 in enumerate(xrange(*i.indices(head.rows)))]
            col_indices = [(j,0)]
        elif ti is int and tj is slice:
            row_indices = [(i,0)]
            col_indices = [(j0,k) for k,j0 in enumerate(xrange(*j.indices(head.cols)))]
        elif ti is slice and tj is slice:
            row_indices = [(i0,k) for k,i0 in enumerate(xrange(*i.indices(head.rows)))]
            col_indices = [(j0,k) for k,j0 in enumerate(xrange(*j.indices(head.cols)))]
        else:
            raise NotImplementedError(`key`)
        if isinstance(value, MatrixBase):
            m, n = value.head.shape
            assert len(row_indices)==m,`len(row_indices),m`
            assert len(col_indices)==n,`len(col_indices),n`
            if head.is_transpose:
                for i,ki in row_indices:
                    for j,kj in col_indices:
                        v = value[ki, kj]
                        if v:
                            data[j, i] = v
                        else:
                            try:
                                del data[j, i]
                            except KeyError:
                                pass
            else:
                for i,ki in row_indices:
                    for j,kj in col_indices:
                        v = value[ki, kj]
                        if v:
                            data[i, j] = v
                        else:
                            try:
                                del data[i, j]
                            except KeyError:
                                pass
        else:
            if value:
                if head.is_transpose:
                    for i,ki in row_indices:
                        for j,kj in col_indices:
                            data[j, i] = value
                else:
                    for i,ki in row_indices:
                        for j,kj in col_indices:
                            data[i, j] = value
            else:
                if head.is_transpose:
                    for i,ki in row_indices:
                        for j,kj in col_indices:
                            try:
                                del data[j, i]
                            except KeyError:
                                pass
                else:
                    for i,ki in row_indices:
                        for j,kj in col_indices:
                            try:
                                del data[i, j]
                            except KeyError:
                                pass
    
    def copy(self):
        """ Return a copy of a matrix.
        """
        head, data = self.pair
        return MatrixDict(head, dict(data))


    def __array__(self):
        """ Return matrix as numpy array.
        """
        import numpy
        head, data = self.pair
        storage = head.storage
        shape = head.shape
        r = numpy.zeros(shape,dtype=object)
        if head.is_transpose:
            for (j, i),e in data.items():
                r[i][j] = e
        else:
            for (i,j),e in data.items():
                r[i][j] = e
        return r

    def __neg__(self):
        head, data = self.pair
        return MatrixDict(head, dict([(index,-element) for index, element in data.items()]))

    def inv_l(self):
        """ Return inverse of lower triangular matrix L.
        """

        M,N = self.head.shape
        linv = Matrix(M,N)
        assert M==N,`M,N`
        for j in xrange(N):
            linv[j,j] = div(1, self[j, j])
            for i in xrange(j+1,N):
                r = 0
                for k in range(j,i):
                    r = r - self[i, k] * linv[k, j]
                linv[i, j] = div(r, self[i, i])
        return linv

    def inv(self):
        """ Return inverse of a square matrix.
        """
        head, data = self.pair
        m, n = head.shape
        assert m==n,`m,n`
        if head.is_transpose:
            d = {}
            for (i,j),x in data.items():
                d[j,i] = x
        else:
            d = dict(data)
        for i in range(m):
            d[i,i+m] = 1
        a = MatrixDict(MATRIX(m, 2*m, MATRIX_DICT), d)
        # XXX: catch singular matrices
        b = a.gauss_jordan_elimination(overwrite=True)
        return b[:,m:]

    def solve(self, rhs):
        """ Solve system of linear equations A * x = b.

        Usage:

          A // b -> x
        
        For example::

          Matrix([[1,2], [3,4]]) // [1,2] -> Matrix([[0],[1/2]])
        
        """
        t = type(rhs)
        if t is tuple or t is list:
            rhs = Matrix(rhs)
        head, data = self.pair
        m, n = head.shape
        assert m==n,`m,n`
        if head.is_transpose:
            d = {}
            for (i,j), x in data.items():
                d[j,i] = x
        else:
            d = dict(data)
        rhead, rdata = rhs.pair
        p, q = rhead.shape
        assert p==m,`p,m`
        if rhead.is_transpose:
            for (j,i),x in rdata.items():
                d[i,j+n] = x
        else:
            for (i,j),x in rdata.items():
                d[i,j+n] = x
        a = MatrixDict(MATRIX(m, n+q, MATRIX_DICT), d)
        b = a.gauss_jordan_elimination(overwrite=True)
        return b[:,m:]

    __floordiv__ = solve
    
from .matrix_operations import MATRIX_DICT_iadd, MATRIX_DICT_imul
from .linalg import (MATRIX_DICT_swap_rows, MATRIX_DICT_swap_cols,
                     MATRIX_DICT_lu, MATRIX_DICT_crop,
                     MATRIX_DICT_gauss_jordan_elimination,
                     MATRIX_DICT_trace)
from .linalg_determinant import MATRIX_DICT_determinant

MatrixDict.__iadd__ = MATRIX_DICT_iadd
MatrixDict.__imul__ = MATRIX_DICT_imul
MatrixDict.swap_rows = MATRIX_DICT_swap_rows
MatrixDict.swap_cols = MATRIX_DICT_swap_cols
MatrixDict.crop = MATRIX_DICT_crop
MatrixDict.lu = MATRIX_DICT_lu
MatrixDict.gauss_jordan_elimination = MATRIX_DICT_gauss_jordan_elimination
MatrixDict.det = MATRIX_DICT_determinant
MatrixDict.trace = MATRIX_DICT_trace
