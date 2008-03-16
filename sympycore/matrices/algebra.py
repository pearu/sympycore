#
# Author: Pearu Peterson
# Created: February 2008
#
""" Provides MatrixRing, SquareMatrix, PermutationMatrix classes.
"""
__docformat__ = "restructuredtext"
__all__ = ['Matrix', 'MatrixBase']

import random

from ..core import classes
from ..utils import SYMBOL, NUMBER, ADD, MUL, POW, MATRIX, MATRIX_DICT, MATRIX_DICT_T, MATRIX_DICT_A
from ..basealgebra import Algebra
from ..basealgebra.verbatim import Verbatim
from ..arithmetic.numbers import div

def is_sequence(obj):
    if isinstance(obj, (tuple, list)):
        return True
    try:
        len(obj)
        return True
    except TypeError:
        return False

def Matrix(*args):
    """ Construct a matrix instance.

    The following signatures are supported:

      Matrix(n)           - n x n matrix of zeros
      Matrix(m, n)        - m x n matrix of zeros
      Matrix(diag)        - n x n diagonal matrix where n = len(diag)
      Matrix(array)       - m x n matrix where m=len(array), n=max(len(array[:]))
      Matrix(m, n, dict)  - m x n matrix with nonzero elements defined by dict,
                            dict keys must be 2-tuples of integers.
    """
    if len(args)==1:
        a = args[0]
        if isinstance(a, int):
            m, n = a, a
            data = {}
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
                            data[i,j] = x
                    else:
                        n = max(n, 1)
                        data[i,0] = row
            else:
                n = m
                for i, x in enumerate(a):
                    data[i, i] = x
        else:
            raise TypeError('Matrix call with 1 argument: argument must be integer or a sequence, got %r' % (type(a)))
    elif len(args)==2:
        m, n = args
        data = {}
        if not (isinstance(m, int) and isinstance(n, int)):
            raise TypeError('Matrix call with 2 arguments: arguments must be integers, got %r, %r' % (type(m), type(n)))
    elif len(args)==3:
        m, n, data = args
        if not (isinstance(m, int) and isinstance(n, int) and isinstance(data, dict)):
            raise TypeError('Matrix call with 3 arguments: arguments must be integers and a dictionary, got %r, %r, %r'\
                            % (type(m), type(n), type(data)))
    else:
        raise TypeError('Matrix takes 1, 2, or 3 arguments, got %r' % (len(args)))

    return MatrixDict(MATRIX(m, n, MATRIX_DICT), data)

class MatrixBase(Algebra):
    """ Base class to matrix classes.
    """

    @classmethod
    def convert(cls, data, typeerror=True):
        if isinstance(data, list):
            return Matrix(data)
        return super(CommutativeRing, cls).convert(data, typeerror=typeerror)

    @classmethod
    def random(cls, n, m, interval=(-10,10)):
        d = {}
        for i in range(n):
            for j in range(m):
                num = random.randint(*interval)
                if num:
                    d[i,j] = num
        return Matrix(n, m, d)

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

    def __add__(self, other):
        # generic code
        ret = self.copy()
        ret += other
        return ret

    __radd__ = __add__

    def __isub__(self, other):
        self += -other
        return self

    def __sub__(self, other):
        # generic code
        ret = self.copy()
        ret -= other
        return ret

    def __rsub__(self, other):
        # generic code
        return other + (-self)

    def __mul__(self, other):
        ret = self.copy()
        ret *= other
        return ret

    def __rmul__(self, other):
        t = type(other)
        if t is list:
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

    is_square = property(lambda self: self.rows==self.cols)

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
        newhead = head.A
        if newhead is head:
            return self
        return type(self)(newhead, data)

    @property
    def M(self):
        """ Return matrix view of a matrix.
        """
        head, data = self.pair
        newhead = head.M
        if newhead is head:
            return self
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
                col_indices = dict([(j0,k) for k,j0 in enumerate(xrange(*j.indices(head.rows)))])
            elif ti is slice and tj is slice:
                row_indices = dict([(i0,k) for k,i0 in enumerate(xrange(*i.indices(head.rows)))])
                col_indices = dict([(j0,k) for k,j0 in enumerate(xrange(*j.indices(head.rows)))])
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
        head, data = self.pair
        return type(self)(head, dict(data))

    def __array__(self):
        import numpy
        head, data = self.pair
        storage = head.storage
        shape = head.shape
        r = numpy.zeros(shape,dtype=object)
        if head.is_transpose:
            for (j, i),e in data.iteritems():
                r[i][j] = e
        else:
            for (i,j),e in data.iteritems():
                r[i][j] = e
        return r

    def __pos__(self):
        return self

    def __neg__(self):
        head, data = self.pair
        return type(self)(head, dict([(index,-element) for index, element in data.iteritems()]))

    def __iadd__(self, other):
        # generic code
        if isinstance(other, list):
            other = Matrix(other)
        if self.is_writable:
            ret = self
        else:
            ret = self.copy()
        rows, cols = self.head.shape
        if type(other) is type(self):
            head1, data1 = ret.pair
            head2, data2 = other.pair
            assert head1.shape==head2.shape,`head1, head2`
            if head1.is_transpose:
                if head2.is_transpose:
                    iadd_MATRIX_MATRIX_TT(data1, data2)
                else:
                    iadd_MATRIX_MATRIX_TA(data1, data2)
            elif head2.is_transpose:
                iadd_MATRIX_MATRIX_AT(data1, data2)
            else:
                iadd_MATRIX_MATRIX_AA(data1, data2)
        elif isinstance(other, MatrixBase):
            assert other.head.shape == self.head.shape
            for i in xrange(rows):
                for j in xrange(cols):
                    ret[i, j] = ret[i, j] + other[i, j]
        else:
            #scalar
            for i in xrange(rows):
                for j in xrange(cols):
                    ret[i, j] = ret[i, j] + other
        return ret

    def __imul__(self, other):
        if isinstance(other, list):
            other = Matrix(other)
        if type(other) is type(self):
            head1, data1 = self.pair
            head2, data2 = other.pair
            if head1.is_array or head2.is_array:
                assert head1.shape==head2.shape,`head1, head2`
                if self.is_writable:
                    ret = self
                else:
                    ret = self.copy()
                data1 = ret.data
                if head1.is_transpose:
                    if head2.is_transpose:
                        imul_MATRIX_MATRIX_ATT(data1, data2)
                    else:
                        imul_MATRIX_MATRIX_TA(data1, data2)
                elif head2.is_transpose:
                    imul_MATRIX_MATRIX_AT(data1, data2)
                else:
                    imul_MATRIX_MATRIX_AA(data1, data2)
                return ret
            else:
                assert head1.cols==head2.rows,`head1, head2`
                args = data1, data2, head1.rows, head2.cols, head1.cols
                if head1.is_transpose:
                    if head2.is_transpose:
                        return mul_MATRIX_MATRIX_MTT(*args)
                    return mul_MATRIX_MATRIX_TM(*args)
                elif head2.is_transpose:
                    return mul_MATRIX_MATRIX_MT(*args)
                else:
                    return mul_MATRIX_MATRIX_MM(*args)
        elif isinstance(other, MatrixBase):
            raise NotImplementedError(`type(self), type(other)`)
        else:
            if self.is_writable:
                ret = self
            else:
                ret = self.copy()
            if other:
                head, data = ret.pair
                for key in data:
                    data[key] *= other
            else:
                head, data = ret.pair
                data.clear()
            return ret
        
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
        M,N = self.head.shape
        K = min(M, N)
        L = MatrixDict(MATRIX(M, K, MATRIX_DICT), {})
        U = MatrixDict(MATRIX(K, N, MATRIX_DICT), dict(self.data))
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
        P = PermutationMatrix.convert(pivot_table).T
        return P, L, U

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
        p, l, u = self.lu()
        # a = p*l*u
        # a^-1 = u^-1 * l^-1 * p.T
        det = reduce(lambda x,y:x*y,[u[i,i] for i in range(min(u.head.shape))],1)
        if det:
            linv = l.inv_l()
            uinv = u.T.inv_l().T
            return uinv * linv * p.T
        raise ZeroDivisionError

class PermutationMatrix(MatrixDict):
    """ Represents a square permutation matrix."""

    @classmethod
    def convert(cls, data, typeerror=True):
        if isinstance(data, (list,tuple)):
            n = len(data)
            d = {}
            for i,index in enumerate(data):
                d[i, index] = 1
            return MatrixDict(MATRIX(n, n, MATRIX_DICT), d)
        return super(MatrixDict, cls).convert(data, typeerror=typeerror)

def iadd_MATRIX_MATRIX_AA(data1, data2):
    for key,x in data2.items():
        b = data1.get(key)
        if b is None:
            data1[key] = x
        else:
            b += x
            if b:
                data1[key] = b
            else:
                del data1[key]

def iadd_MATRIX_MATRIX_AT(data1, data2):
    for (j,i),x in data2.items():
        key = i,j
        b = data1.get(key)
        if b is None:
            data1[key] = x
        else:
            b += x
            if b:
                data1[key] = b
            else:
                del data1[key]

def iadd_MATRIX_MATRIX_TA(data1, data2):
    for (i,j),x in data2.items():
        key = j,i
        b = data1.get(key)
        if b is None:
            data1[key] = x
        else:
            b += x
            if b:
                data1[key] = b
            else:
                del data1[key]

iadd_MATRIX_MATRIX_TT = iadd_MATRIX_MATRIX_AA

def imul_MATRIX_MATRIX_AA(data1, data2):
    for key in data1:
        b = data2.get(key)
        if b is None:
            del data1[key]
        else:
            data1[key] *= b

def imul_MATRIX_MATRIX_AT(data1, data2):
    for key in data1:
        i,j = key
        b = data2.get((j,i))
        if b is None:
            del data1[key]
        else:
            data1[key] *= b

imul_MATRIX_MATRIX_TA = imul_MATRIX_MATRIX_AT
imul_MATRIX_MATRIX_ATT = imul_MATRIX_MATRIX_AA

def mul_MATRIX_MATRIX_AA(data1, data2, rows, cols):
    indices = range(n)
    d = {}
    data1_get = data1.get
    data2_get = data2.get
    for i in xrange(rows):
        for j in xrange(cols):
            key = i,j
            a_ij = data1_get(key)
            if a_ij is None:
                continue
            b_ij = data2_get(key)
            if b_ij is None:
                continue
            d[key] = a_ij * b_ij
    return MatrixDict(MATRIX(rows, cols, MATRIX_DICT), d)

def mul_MATRIX_MATRIX_AT(data1, data2, rows, cols):
    indices = range(n)
    d = {}
    data1_get = data1.get
    data2_get = data2.get
    for i in xrange(rows):
        for j in xrange(cols):
            key = i,j
            a_ij = data1_get(key)
            if a_ij is None:
                continue
            b_ij = data2_get((j,i))
            if b_ij is None:
                continue
            d[key] = a_ij * b_ij
    return MatrixDict(MATRIX(rows, cols, MATRIX_DICT), d)

def mul_MATRIX_MATRIX_TA(data1, data2, rows, cols):
    indices = range(n)
    d = {}
    data1_get = data1.get
    data2_get = data2.get
    for i in xrange(rows):
        for j in xrange(cols):
            key = i,j
            a_ij = data1_get((j,i))
            if a_ij is None:
                continue
            b_ij = data2_get(key)
            if b_ij is None:
                continue
            d[key] = a_ij * b_ij
    return MatrixDict(MATRIX(rows, cols, MATRIX_DICT), d)

def mul_MATRIX_MATRIX_ATT(data1, data2, rows, cols):
    indices = range(n)
    d = {}
    data1_get = data1.get
    data2_get = data2.get
    for i in xrange(rows):
        for j in xrange(cols):
            ikey = j,i
            a_ij = data1_get(ikey)
            if a_ij is None:
                continue
            b_ij = data2_get(ikey)
            if b_ij is None:
                continue
            d[i,j] = a_ij * b_ij
    return MatrixDict(MATRIX(rows, cols, MATRIX_DICT), d)

def mul_MATRIX_MATRIX_MM(data1, data2, rows, cols, n):
    indices = range(n)
    d = {}
    data1_get = data1.get
    data2_get = data2.get
    for i in xrange(rows):
        for j in xrange(cols):
            c_ij = 0
            for k in indices:
                a_ik = data1_get((i,k))
                if a_ik is None:
                    continue
                b_kj = data2_get((k,j))
                if b_kj is None:
                    continue
                c_ij += a_ik * b_kj
            if c_ij:
                d[i,j] = c_ij
    return MatrixDict(MATRIX(rows, cols, MATRIX_DICT), d)

def mul_MATRIX_MATRIX_TM(data1, data2, rows, cols, n):
    indices = range(n)
    d = {}
    data1_get = data1.get
    data2_get = data2.get
    for i in xrange(rows):
        for j in xrange(cols):
            c_ij = 0
            for k in indices:
                a_ik = data1_get((k,i))
                if a_ik is None:
                    continue
                b_kj = data2_get((k,j))
                if b_kj is None:
                    continue
                c_ij += a_ik * b_kj
            if c_ij:
                d[i,j] = c_ij
    return MatrixDict(MATRIX(rows, cols, MATRIX_DICT), d)

def mul_MATRIX_MATRIX_MT(data1, data2, rows, cols, n):
    indices = range(n)
    d = {}
    data1_get = data1.get
    data2_get = data2.get
    for i in xrange(rows):
        for j in xrange(cols):
            c_ij = 0
            for k in indices:
                a_ik = data1_get((i,k))
                if a_ik is None:
                    continue
                b_kj = data2_get((j,k))
                if b_kj is None:
                    continue
                c_ij += a_ik * b_kj
            if c_ij:
                d[i,j] = c_ij
    return MatrixDict(MATRIX(rows, cols, MATRIX_DICT), d)

def mul_MATRIX_MATRIX_MTT(data1, data2, rows, cols, n):
    indices = range(n)
    d = {}
    data1_get = data1.get
    data2_get = data2.get
    for i in xrange(rows):
        for j in xrange(cols):
            c_ij = 0
            for k in indices:
                a_ik = data1_get((k,i))
                if a_ik is None:
                    continue
                b_kj = data2_get((j,k))
                if b_kj is None:
                    continue
                c_ij += a_ik * b_kj
            if c_ij:
                d[i,j] = c_ij
    return MatrixDict(MATRIX(rows, cols, MATRIX_DICT), d)
