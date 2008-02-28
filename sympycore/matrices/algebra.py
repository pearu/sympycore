#
# Author: Pearu Peterson
# Created: February 2008
#
""" Provides MatrixRing, SquareMatrix, PermutationMatrix classes.
"""
__docformat__ = "restructuredtext"
__all__ = ['MatrixRing', 'SquareMatrix', 'PermutationMatrix']

import random

from ..core import BasicType, classes
from ..utils import SYMBOL, NUMBER, ADD, MUL, POW
from ..basealgebra.ring import CommutativeRing
from ..basealgebra import PrimitiveAlgebra
from ..arithmetic.numbers import div

class MatrixRingFactory(BasicType):

    def __new__(typ, name, bases, attrdict):
        if not attrdict.has_key('ring'):
            attrdict['ring'] = classes.Calculus
        if not attrdict.has_key('shape'):
            attrdict['shape'] = None
        cls = type.__new__(typ, name, bases, attrdict)
        cls.zero = cls.Number(0)
        cls.one = cls.Number(1)
        return cls

    def __eq__(self, other):
        if isinstance(other, MatrixRingFactory):
            return self.ring==other.ring and self.shape==other.shape
        return False

    def __ne__(self, other):
        return not self==other

    def __getitem__(self, ring_info, cache={}):
        """ Return a new matrix ring class.

        Examples::

          MatrixRing[<shape>, <coefficient ring>]
          MatrixRing[<shape>] is MatrixRing[<shape>, Calculus]
          MatrixRing[<coefficient ring>] is MatrixRing[None, <coefficient ring>]

        When ``<shape>`` is ``None`` then the shape is determined by
        the smallest and largest index.
        """
        if isinstance(ring_info, (int, long)):
            if self.is_square:
                shape = (ring_info,)*2
            else:
                shape = (ring_info, 1)
            ring = classes.Calculus
        elif isinstance(ring_info, type):
            shape = None
            ring = ring_info
        elif isinstance(ring_info, tuple) and isinstance(ring_info[-1], type):
            if len(ring_info)==2:
                shape_info, ring = ring_info
                if isinstance(shape_info, (int, type)):
                    if self.is_square:
                        shape = (shape_info,)*2
                    else:
                        shape = (shape_info, 1)
                elif isinstance(shape_info, (tuple,list)):
                    shape = tuple(shape_info)
                elif shape_info is None:
                    shape = None
                else:
                    raise TypeError(`shape_info, ring_info`)
            else:
                shape = ring_info[:-1]
                ring = ring_info[-1]
        elif isinstance(ring_info, (tuple, list)):
            shape = tuple(ring_info)
            ring = classes.Calculus
        elif ring_info is None:
            shape = None
            ring = classes.Calculus
        else:
            raise TypeError(`ring_info`)

        name = '%s[%s, %s]' % (self.__name__, shape, ring.__name__)
        r = MatrixRingFactory(name,
                              (self,),
                              dict(shape=shape, ring = ring))
        return r

def newinstance(cls, data):
    obj = object.__new__(cls)
    obj.data = data
    return obj


class MatrixRing(CommutativeRing):
    """ Base class to matrix rings that hold matrix element information
    pairs ``(<indices>: <element>)`` stored in Python dictionary.

    Represents rectangular matrix.
    """

    __slots__ = ['data']

    __metaclass__ = MatrixRingFactory

    is_square = None

    def __new__(cls, data={}):
        if isinstance(data, list):
            if data and isinstance(data[0], list):
                d = {}
                for i,row in enumerate(data):
                    for j,element in enumerate(row):
                        if element:
                            d[i,j] = element
                data = d
            else:
                data = dict(data)
        elif not isinstance(data, dict):
            return cls.convert(data)
        return newinstance(cls, data)

    @classmethod
    def random(cls, interval=(-10,10)):
        n,m = cls.shape
        d = {}
        r = newinstance(cls, d)
        for i in range(n):
            for j in range(m):
                num = random.randint(*interval)
                if num:
                    d[i,j] = num
        return r
    
    def copy(self):
        return newinstance(self.__class__, dict(self.data))

    def __eq__(self, other):
        return other.__class__ == self.__class__ and self.data == other.data

    def __array__(self):
        import numpy
        r = numpy.zeros(self.shape,dtype=object)
        for (i,j),e in self.data.iteritems():
            r[i][j] = e
        return r

    @classmethod
    def Number(cls, obj):
        if cls.shape is None:
            return newinstance(cls, {():obj})
        if cls.shape[0]==1:
            return newinstance(cls, dict([((1,i),obj) for i in range(cls.shape[0])]))
        if cls.shape[1]==1:
            return newinstance(cls, dict([((i,1),obj) for i in range(cls.shape[0])]))
        m = min(cls.shape)
        return newinstance(cls, dict([((i,i),obj) for i in range(m)]))

    def __str__(self):
        if self.shape is not None:
            columns = []
            for j in xrange(self.shape[1]):
                col = []
                for i in xrange(self.shape[0]):
                    s = str(self[i,j])
                    col.append(s)
                width = max(map(len,col))
                fmt = ' %'+str(width)+'s '
                col = [fmt % (s) for s in col]
                columns.append(col)
            return '\n'.join([''.join(row).rstrip() for row in zip(*columns)])
        return '['+', '.join(['(%s, %s)' % (i,e) for i,e in self.data.iteritems()])+']'

    def __setitem__(self, key, value):
        if 0 and self.shape:
            m,n = self.shape
            i,j = key
            assert 0<=i<m,`self.shape,key,value`
            assert 0<=j<n,`self.shape,key,value`
        if value:
            self.data[key] = value
        else:
            try:
                del self.data[key]
            except KeyError:
                pass

    def __getitem__(self, key):
        return self.data.get(key, 0)

    def __neg__(self):
        return newinstance(self.__class__, dict([(index,-element) for index, element in self.data.iteritems()]))

    def __mul__(self, other):
        if isinstance(other, MatrixRing):
            cls1 = self.__class__
            cls2 = other.__class__
            if cls1.ring==cls2.ring:
                if cls1.shape and cls2.shape:
                    if cls1.shape[-1]==cls2.shape[0]:
                        cls = MatrixRing[(cls1.shape[0], cls2.shape[-1]), cls1.ring]
                        return mul_MATRIX_MATRIX(self, other, cls)
                else:
                    return mul_MATRIX_MATRIX(self, other, MatrixRing[cls1.ring])
        elif isinstance(other, (self.ring, int, long)):
            return mul_MATRIX_SCALAR(self, other, self.__class__)
        return NotImplemented

    def __add__(self, other):
        if isinstance(other, (self.ring, int, long)):
            other = self.Number(other)
        if isinstance(other, MatrixRing):
            cls1 = self.__class__
            cls2 = other.__class__
            if cls1.ring==cls2.ring:
                if cls1==cls2:
                    return add_MATRIX_MATRIX(self, other, cls1)
                else:
                    return add_MATRIX_MATRIX(self, other, MatrixRing[cls1.ring])
        return NotImplemented

    def __sub__(self, other):
        return self + (-other)

    def __div__(self, other):
        if isinstance(other, (self.ring, int, long)):
            return div_MATRIX_SCALAR(self, other, self.__class__)
        return NotImplemented

    def row_indices(self, column=None):
        if column is None:
            return [i for (i,j) in self.data]
        return [i for (i,j) in self.data if j==column]

    def column_indices(self, row=None):
        if row is None:
            return [j for (i,j) in self.data]
        return [j for (i,j) in self.data if i==row]

    def swap_rows(self, i, j):
        """ Swap i-th and j-th rows inplace.
        """
        if i==j:
            return
        data = self.data
        row_i = []
        row_j = []
        for index, element in data.items():
            i0 = index[0]
            if i0==i:
                row_i.append((index, element))
                del data[index]
            elif i0==j:
                row_j.append((index, element))
                del data[index]
        for index,element in row_i:
            data[j, index[1]] = element
        for index,element in row_j:
            data[i, index[1]] = element
        return

    def swap_columns(self, i, j):
        """ Swap i-th and j-th columns inplace.
        """
        if i==j:
            return
        data = self.data
        column_i = []
        column_j = []
        for index, element in data.items():
            i0 = index[1]
            if i0==i:
                column_i.append((index, element))
                del data[index]
            elif i0==j:
                column_j.append((index, element))
                del data[index]
        for index,element in column_i:
            data[index[0], j] = element
        for index,element in column_j:
            data[index[0], i] = element
        return

    def crop(self):
        """ Remove elements that are out of dimensions.
        """
        m, n = self.shape
        for (i,j) in self.data.keys():
            if 0<=i<m and 0<=j<n:
                continue
            del self.data[i,j]

    @property
    def T(self):
        """ Return a transposed copy of the matrix.
        """
        if self.shape is None:
            cls = MatrixRing[None, self.ring]
        else:
            cls = MatrixRing[(self.shape[-1],self.shape[0]), self.ring]
        d = {}
        r = cls(d)
        for (i,j), element in self.data.iteritems():
            d[j, i] = element
        return r

    def lu(self):
        """ Perform LU factorization of a m x n matrix A.

        Outputs::
        
          P, L, U - LU decomposition matrices of A.

        Definitions::
        
          P - m x m permuation matrix
          L - m x k lower triangular or trapezoidal matrix with unit-diagonal
          U - k x n upper triangular or trapezoidal matrix
          k = min(m,n)
          
          A = P * L * U
        """
        M,N = self.shape
        K = min(M, N)
        L = MatrixRing[(M,K), self.ring]({})
        U = MatrixRing[(K,N), self.ring](dict(self.data))
        if M>N:
            for i in xrange(N,M):
                U.data[(i,i)] = 1
        pivot_table = range(M)
        for n in xrange(M-1):
            a_nn = U.data.get((n,n))
            if a_nn is None:
                for k in xrange(n+1, M):
                    a_nn = U.data.get((k,n))
                    if a_nn is not None:
                        break
                if a_nn is None:
                    continue
                pivot_table[n], pivot_table[k] = pivot_table[k], pivot_table[n]
                U.swap_rows(n, k)
                L.swap_rows(n, k)
            for k in xrange(n+1,M):
                u_kn = U.data.get((k,n))
                if u_kn is None:
                    continue
                c = div(u_kn, a_nn)
                for p in xrange(n,N):
                    u_np = U.data.get((n,p))
                    if u_np is None:
                        continue
                    U[k,p] = U[k,p] - u_np*c
                if n<K and k<M:
                    L[k,n] = c
            if n<K:
                L[n,n] = 1
        L[K-1,K-1] = 1
        if M>N:
            U.crop()
        P = PermutationMatrix(pivot_table).T
        return P, L, U

    def inv_l(self):
        """ Return inverse of lower triangular matrix L.
        """
        linv = self.zero.copy()
        M,N = self.shape
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
        p, l, u = self.lu()
        # a = p*l*u
        # a^-1 = u^-1 * l^-1 * p.T
        det = reduce(lambda x,y:x*y,[u[i,i] for i in range(min(u.shape))],1)
        if det:
            linv = l.inv_l()
            uinv = u.T.inv_l().T
            return uinv * linv * p.T
        raise ZeroDivisionError

class SquareMatrix(MatrixRing):
    """ Represents a square matrix."""
    is_square = True

class PermutationMatrix(SquareMatrix):
    """ Represents a square permutation matrix."""
    
    def __new__(cls, data):
        if isinstance(data, (list,tuple)):
            if cls is PermutationMatrix:
                cls = PermutationMatrix[(len(data),)*2]
            one = cls.ring.one
            d = {}
            for i,index in enumerate(data):
                d[i, index] = one
            data = d
        elif not isinstance(data, dict):
            return cls.convert(data)
        return newinstance(cls, data)        


def mul_MATRIX_MATRIX(lhs, rhs, cls):
    d = {}
    r = newinstance(cls, d)
    indices = set([])
    lhs_row_indices = set([])
    rhs_column_indices = set([])
    for (i,j) in lhs.data:
        lhs_row_indices.add(i)
        indices.add(j)
    for (i,j) in rhs.data:
        rhs_column_indices.add(j)
        indices.add(i)
    lget = lhs.data.get
    rget = rhs.data.get
    for i in lhs_row_indices:
        for j in rhs_column_indices:
            c_ij = 0
            for k in indices:
                a_ik = lget((i,k))
                if a_ik is None:
                    continue
                b_kj = rget((k,j))
                if b_kj is None:
                    continue
                c_ij += a_ik * b_kj
            if c_ij:
                d[i,j] = c_ij
    return r

def add_MATRIX_MATRIX(lhs, rhs, cls):
    d = dict(lhs.data)
    r = newinstance(cls, d)
    for index, element in rhs.data.iteritems():
        b = d.get(index)
        if b is None:
            d[index] = element
        else:
            b = b + element
            if b:
                d[index] = b
            else:
                del d[index]
    return r

def sub_MATRIX_MATRIX(lhs, rhs, cls):
    d = dict(lhs.data)
    r = newinstance(cls, d)
    for index, element in rhs.data.iteritems():
        b = d.get(index)
        if b is None:
            d[index] = -element
        else:
            b = b - element
            if b:
                d[index] = b
            else:
                del d[index]
    return r

def mul_MATRIX_SCALAR(lhs, rhs, cls):
    d = {}
    r = newinstance(cls, d)
    for index, element in lhs.data.iteritems():
        d[index] = element * rhs
    return r

def div_MATRIX_SCALAR(lhs, rhs, cls):
    d = {}
    r = newinstance(cls, d)
    for index, element in lhs.data.iteritems():
        d[index] = div(element, rhs)
    return r
